from send import SerialSender
import time
import threading


def warehouse1():
    # Initialize SerialSender instance
    sender = SerialSender("/dev/armcontrol", 9600)  # Serial port and baud rate

    # Send data "position"
    time.sleep(2)
    data_to_send = "position1"
    sender.send_data(data_to_send)
    print(f"Sent data: {data_to_send}")
    # Wait for data to be processed
    time.sleep(3)
    print("Exiting warehouse1 script.")

def start_warehouse1_thread():
    # Create and start a thread for armstart function
    warehouse1_thread = threading.Thread(target=warehouse1)
    warehouse1_thread.start()
    return warehouse1_thread

if __name__ == '__main__':
    # Start the warehouse thread
    warehouse1_thread = start_warehouse1_thread()



