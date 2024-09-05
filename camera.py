import cv2
import numpy as np
from pyzbar import pyzbar
import threading
import time
from send import SerialSender
import re
import receive

# ¶¨ÒåÈ«¾ÖËø£¬ÓÃÓÚ´®¿ÚÍ¨ÐÅµÄÏß³ÌÍ¬²½
serial_lock = threading.Lock()

# ³õÊ¼»¯ SerialSender ÊµÀý£¬ÓÃÓÚÓë Arduino Í¨ÐÅ
sender = SerialSender("/dev/armcontrol", 9600)
cap = None  # È«¾ÖÉãÏñÍ·¶ÔÏó

def open_camera():
    """´ò¿ªÉãÏñÍ·²¢³õÊ¼»¯"""
    global cap
    if cap is not None and cap.isOpened():
        print("Camera is already open.")  # ÉãÏñÍ·ÒÑ¾­´ò¿ª
        return cap

    # ´ò¿ªÖ¸¶¨Ë÷ÒýµÄÉãÏñÍ·
    cap = cv2.VideoCapture(8, cv2.CAP_V4L2)
    if not cap.isOpened():
        print("Failed to open camera.")  # ÉãÏñÍ·´ò¿ªÊ§°Ü
        cap = None
    else:
        print("Camera opened successfully.")  # ÉãÏñÍ·³É¹¦´ò¿ª
        time.sleep(2)  # µÈ´ýÉãÏñÍ·ÎÈ¶¨
    return cap

def process_frame(frame):
    """´¦Àíµ¥Ö¡Í¼Ïñ£¬Ê¶±ð¶þÎ¬Âë²¢ÌáÈ¡ÐÅÏ¢"""
    decoded_objects = pyzbar.decode(frame)
    if decoded_objects:  # Èç¹ûÊ¶±ðµ½¶þÎ¬Âë
        obj = decoded_objects[0]  # »ñÈ¡µÚÒ»¸öÊ¶±ðµ½µÄ¶þÎ¬Âë¶ÔÏó
        points = obj.polygon
        if len(points) > 4:
            hull = cv2.convexHull(np.array([point for point in points], dtype=np.float32))
            hull = list(map(tuple, np.squeeze(hull)))
        else:
            hull = points
        n = len(hull)
        for j in range(0, n):
            cv2.line(frame, hull[j], hull[(j + 1) % n], (0, 255, 0), 3)

        x = obj.rect.left
        y = obj.rect.top
        text = obj.data.decode("utf-8")
        cv2.putText(frame, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        cv2.rectangle(frame, (x, y), (x + obj.rect.width, y + obj.rect.height), (0, 255, 0), 2)

        # ÌáÈ¡¶þÎ¬ÂëÖÐµÄÐÅÏ¢
        qr_data_pattern = r"(\d+),([^,]+),([\d.]+),([^,]+)"
        match = re.match(qr_data_pattern, text)
        if match:
            product_id = int(match.group(1))
            city = match.group(2)
            weight = float(match.group(3))
            product_name = match.group(4)
            print(f"Decoded data - Product ID: {product_id}, City: {city}, Weight: {weight}, Product Name: {product_name}")

            # ¼ÓËø²¢·¢ËÍ city Êý¾Ýµ½ Arduino
            with serial_lock:
                sender.send_data(city)  # ·¢ËÍ city ÐÅÏ¢µ½ Arduino

        return True  # ·µ»Ø True ±íÊ¾³É¹¦´¦ÀíÖ¡
    return False

def close_camera():
    """¹Ø±ÕÉãÏñÍ·"""
    global cap
    if cap and cap.isOpened():
        cap.release()  # ÊÍ·ÅÉãÏñÍ·×ÊÔ´
        cap = None
        print("Camera released.")  # ÉãÏñÍ·ÒÑÊÍ·Å
    else:
        print("Camera was not open or already released.")  # ÉãÏñÍ·Î´´ò¿ª»òÒÑÊÍ·Å

def capture_and_process():
    """²¶»ñÉãÏñÍ·Í¼Ïñ²¢´¦ÀíÖ±µ½Ê¶±ð³ö¶þÎ¬Âë"""
    global cap
    cap = open_camera()  # ´ò¿ªÉãÏñÍ·
    if cap is None:
        print("Failed to open camera.")  # ´ò¿ªÉãÏñÍ·Ê§°Ü
        return

    while True:
        success, frame = cap.read()
        if not success:
            print("Failed to read frame from camera.")  # ¶ÁÈ¡ÉãÏñÍ·Í¼ÏñÊ§°Ü
            break

        if process_frame(frame):  # ³É¹¦Ê¶±ð¶þÎ¬ÂëºóÍË³öÑ­»·
            break

    close_camera()  # ¹Ø±ÕÉãÏñÍ·

    time.sleep(20)
    if receive.received_data == 'finish':
        print("Received finish command.")  # ÊÕµ½ finish ÃüÁî
        with open('finish', 'w') as file:
            file.write('finish')
        print("Written 'finish' to connection file.")  # ½« finish Ð´ÈëÁ¬½ÓÎÄ¼þ

    print("Waiting for the next 'goal reached' command.")  # µÈ´ýÏÂÒ»¸ö 'goal reached' ÃüÁî

if __name__ == '__main__':
    # Ö´ÐÐ²¶»ñºÍ´¦ÀíÁ÷³Ì
    capture_and_process()
    print("Application finished execution.")  # ³ÌÐòÖ´ÐÐÍê³É

