import threading
import time
from armstart import armstart
import receive
import camera
from warehouse1 import warehouse1
from warehouse2 import warehouse2
from send import SerialSender
lock = threading.Lock()  # ?¡§¨°???3¨¬??
content = 'NULL'  # 3?¨º??¡¥?¨²¨¨Y
goal_reached_event = threading.Event()  # ?¡§¨°?¨°???¨º??t¨®?¨®¨² 'goal reached'
recognition_event = threading.Event()  # ?¡§¨°?¨°???¨º??t¨®?¨®¨² 'recognition'

goal_reached_count = 0  # ¨ª3??¨º?¦Ì? 'goal reached' ¦Ì?¡ä?¨ºy
warehouse_ready = False  # ¨®?¨®¨²¡À¨º¨º?¨º?¡¤?¨®|???¡äDD 'warehouse' ???-
reset_ready = False  # ¨®?¨®¨²¡À¨º¨º?¨º?¡¤?¨®|???¡äDD 'warehouse' ???-
def check_command_file():
    """?¨¬2¨¦?¨¹¨¢????to¨ª¨º?¡Àe???t¦Ì??¨²¨¨Y?¡ê"""
    sender = SerialSender("/dev/armcontrol", 9600)  # Serial port and baud rate
    global content
    while True:
        try:
            # ¡ä|¨¤¨ª?¨¹¨¢????t
            with open('command', 'r') as file:
                new_content = file.read().strip()
                with lock:
                    content = new_content
                if content == 'goal reached':
                    print("Goal reached command detected.")
                    goal_reached_event.set()  # ¨¦¨¨??¨º??t¨ª¡§?a 'goal reached' ¡À??¨¬2a¦Ì?
        except FileNotFoundError:
            print("Command file not found.")

        # ¡ä|¨¤¨ª¨º?¡Àe???t
        try:
            with open('recognition', 'r') as file:
                recognition_content = file.read().strip()
                with lock:
                    if recognition_content == 'undamaged':
                        print("Undamaged detected.")
                        recognition_event.set()  # ¨¦¨¨??¨º??t¨ª¡§?a 'undamaged' ¡À??¨¬2a¦Ì?
                    elif recognition_content == 'damaged':
                        print("Damaged detected.")
                        with open('finish', 'w') as file:
                            file.write('finish')
                        print("Written 'finish' to connection file.")
                        with open('recognition', 'w') as file:
                            file.write('')  # ??3yrecognition??¨¢?
                        data_send = "reset"
                        print("sending reset command to Arduino.")
                        sender.send_data(data_send)
                        print(f"Sent data: {data_send}")
                        time.sleep(3)
        except FileNotFoundError:
            print("Recognition file not found.")

        time.sleep(5)  # ?Y¨º¡À?¨®3¨´o¨®??¨º?

def start_armstart_thread():
    """¡ä¡ä?¡§2¡é???¡¥¨°?????3¨¬¨¤¡ä?¡äDD armstart o¡¥¨ºy?¡ê"""
    armstart_thread = threading.Thread(target=armstart)
    armstart_thread.start()
    return armstart_thread

def start_camera_thread():
    """¡ä¡ä?¡§2¡é???¡¥¨°?????3¨¬¨¤¡ä?¡äDD¨¦???¨ª¡¤¨º?¡Àeo¡¥¨ºy?¡ê"""
    camera_thread = threading.Thread(target=camera.capture_and_process)
    camera_thread.start()
    return camera_thread

def main():
    global goal_reached_count, warehouse_ready, reset_ready
    sender = SerialSender("/dev/armcontrol", 9600)  # Serial port and baud rate
    """?¡Âo¡¥¨ºy¡ê?¨®?¨®¨²???¡¥?¨¹¨¢????t?¨¤????3¨¬?¡ê"""
    # ???¡¥??3¨¬¨¤¡ä?¨¤???¨¹¨¢????t
    command_file_thread = threading.Thread(target=check_command_file)
    command_file_thread.start()

    # ???¡¥¡ä??¨²?¨¤¨¬y??3¨¬
    serial_thread = threading.Thread(target=receive.serial_listener)
    serial_thread.start()

    try:
        goal_reached_count = 0  # 3?¨º??¡¥ goal_reached_count ??¨ºy

        while True:
            # 3?D??¨¤2a 'goal reached' ¨º??t
            if goal_reached_event.is_set():
                # ¨ª3??¨º?¦Ì? 'goal reached' ¦Ì?¡ä?¨ºy
                goal_reached_count += 1
                print(f"Goal reached count: {goal_reached_count}")
                # ¦Ì¨²??¡ä?¨º?¦Ì? 'goal reached'¡ê?¨¬?3??-?¡¤?¡äDD reset

                armstart_thread = start_armstart_thread()

                # ¦Ì¨¨¡äy armstart ??3¨¬¨ª¨º3¨¦
                armstart_thread.join()
                print("Armstart thread has finished execution.")

                with open('command', 'w') as file:
                    file.write('')  # ??3ygoal reached??¨¢?
                print("Cleared content from command file.")
                goal_reached_event.clear()

                # ¦Ì¨²??¡ä?¨º?¦Ì? 'goal reached'¡ê?¨¬?3??-?¡¤?¡äDD warehouse
                if goal_reached_count == 4:
                    print("Fourth goal reached, starting warehouse1 operation.")
                    warehouse1()
                    print("sending reset command to Arduino.")
                    time.sleep(1)
                    data_send = "reset"
                    sender.send_data(data_send)
                    print(f"Sent data: {data_send}")
                    time.sleep(2)
                    continue  # ¨¬?3?¦Ì¡À?¡ã?-?¡¤¡ê???D??a¨º?
                    # ¦Ì¨²??¡ä?¨º?¦Ì? 'goal reached'¡ê?¨¬?3??-?¡¤?¡äDD warehouse
                if goal_reached_count == 5:
                    print("Fourth goal reached, starting warehouse2 operation.")
                    warehouse2()
                    print("sending reset command to Arduino.")
                    time.sleep(1)
                    data_send = "reset"
                    sender.send_data(data_send)
                    print(f"Sent data: {data_send}")
                    time.sleep(2)
                    continue  # ¨¬?3?¦Ì¡À?¡ã?-?¡¤¡ê???D??a¨º?

            # ?¨¤2a 'recognition_event' ¨º??t
            if recognition_event.is_set():
                # ???¡¥¨¦???¨ª¡¤¨º?¡Àe??3¨¬
                camera_thread = start_camera_thread()
                camera_thread.join()  # ¦Ì¨¨¡äy¨¦???¨ª¡¤¨º?¡Àe??3¨¬¨ª¨º3¨¦

                # ??3y¨º?¡Àe???t?D¦Ì??¨²¨¨Y
                with open('recognition', 'w') as file:
                    file.write('')
                print("Cleared content from recognition file.")
                recognition_event.clear()  # ????¨º?¡Àe¨º??t

            time.sleep(1)  # ??¨¦¨´CPU??¨®?¡ê??-?¡¤¦Ì¨¨¡äy1??
        print("All threads have finished execution.")
    except KeyboardInterrupt:
        print("Main thread interrupted by user.")
    finally:
        print("All threads have finished execution.")

if __name__ == '__main__':
    main()


