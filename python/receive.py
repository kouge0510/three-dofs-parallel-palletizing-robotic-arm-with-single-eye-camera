import serial
import time
import threading

# ¨¨???¡À?¨¢?
received_data = ""
done_flag = threading.Event()
finish_flag = False  # ?¡§¨°? finish_flag
data_lock = threading.Lock()  # ?¡§¨°???3¨¬??

def serial_listener():
    global received_data
    try:
        ser = serial.Serial("/dev/armcontrol", 9600, timeout=1)
        if ser.is_open:
            print("Serial port /dev/ttyUSB0 opened successfully.")
        else:
            print("Failed to open serial port /dev/ttyUSB0.")
            return 1
    except serial.SerialException as e:
        print(f"Error opening serial port /dev/ttyUSB0: {e}")
        return 1

    try:
        while True:
            try:
                data = ser.readline().decode('utf-8', errors='ignore').strip()
                if data:
                    with data_lock:  # ¡À¡ê?¡è?? received_data ¦Ì?¡¤??¨º
                        received_data = data
                    print(f"Received data: {received_data}")

                    # ¡ä|¨¤¨ª done ?¨¹¨¢?¦Ì????-
                    if received_data == 'done':
                        print("Received done command.")
                        done_flag.set()  # ¨¦¨¨?? done ¡À¨º??¡ê?¨ª¡§?a?¡Â??3¨¬

                        # ?? done D¡ä¨¨? connection ???t
                        with open('connection', 'w') as file:
                            file.write('done')
                        print("Written 'done' to connection file.")

                    # ¡ä|¨¤¨ª complete ?¨¹¨¢?¦Ì????-
                    elif received_data == 'complete':
                        print("Received complete command.")

                    # ¡ä|¨¤¨ª finish ?¨¹¨¢?¦Ì????-
                    elif received_data == 'finish':
                        print("Received finish command.")
                        finish_flag= True  # ¨¦¨¨?? finish ¡À¨º??¡ê?¨ª¡§?a?¡Â??3¨¬

            except serial.SerialException as e:
                print(f"Error reading from serial port: {e}")
                break

            time.sleep(1)

    except KeyboardInterrupt:
        print("Serial listener interrupted by user.")
    finally:
        ser.close()
        print("Serial port closed.")

    return 0


