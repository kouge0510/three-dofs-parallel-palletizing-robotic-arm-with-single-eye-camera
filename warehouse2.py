from send import SerialSender
import time
import threading


def warehouse2():
    # Initialize SerialSender instance
    sender = SerialSender("/dev/armcontrol", 9600)  # Serial port and baud rate

    # Send data "position"
    time.sleep(2)
    data_to_send = "position2"
    sender.send_data(data_to_send)
    print(f"Sent data: {data_to_send}")
    # Wait for data to be processed
    time.sleep(3)
    print("Exiting warehouse1 script.")

def start_warehouse2_thread():
    # Create and start a thread for armstart function
    warehouse2_thread = threading.Thread(target=warehouse2)
    warehouse2_thread.start()
    return warehouse2_thread

if __name__ == '__main__':
    # Start the warehouse thread
    warehouse2_thread = start_warehouse2_thread()



