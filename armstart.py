from send import SerialSender
import time
import threading
# ?¡§¨°?¨¨???¡À¨º??


def armstart():
    # Initialize SerialSender instance
    sender = SerialSender("/dev/armcontrol", 9600)  # Serial port and baud rate


    # Send data "go"
    time.sleep(5)
    data_to_send = "go"
    sender.send_data(data_to_send)
    print(f"Sent data: {data_to_send}")
    # Wait for data to be processed
    time.sleep(3)
    print("Exiting armstart script.")

def start_armstart_thread():
    # Create and start a thread for armstart function
    armstart_thread = threading.Thread(target=armstart)
    armstart_thread.start()
    return armstart_thread

if __name__ == '__main__':
    # Start the armstart thread
    armstart_thread = start_armstart_thread()


