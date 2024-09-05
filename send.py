import serial

class SerialSender:
    def __init__(self, port, baudrate=9600):
        try:
            self.ser = serial.Serial(port, baudrate)
            if self.ser.is_open:
                print(f"Serial port {port} opened successfully.")
            else:
                print(f"Failed to open serial port {port}.")
        except serial.SerialException as e:
            print(f"Error opening serial port {port}: {e}")
            self.ser = None

    def send_data(self, data):
        if self.ser and self.ser.is_open:
            try:
                self.ser.write((data + '\n').encode('utf-8'))
                print(f"Sent data: {data}")
            except Exception as e:
                print(f"Error during sending data: {e}")
        else:
            print("Serial port is not open.")

    def close_serial(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
            print("Serial port closed.")


