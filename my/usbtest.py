import numpy as np
import cv2
import time
from postprocess import postprocess
from hobot_dnn import pyeasy_dnn as dnn
import os
cap = None  # È«¾ÖÉãÏñÍ·¶ÔÏó
def bgr2nv12_opencv(image):
    height, width = image.shape[0], image.shape[1]
    area = height * width
    yuv420p = cv2.cvtColor(image, cv2.COLOR_BGR2YUV_I420).reshape((area * 3 // 2,))
    y = yuv420p[:area]
    uv_planar = yuv420p[area:].reshape((2, area // 4))
    uv_packed = uv_planar.transpose((1, 0)).reshape((area // 2,))

    nv12 = np.zeros_like(yuv420p)
    nv12[:height * width] = y
    nv12[height * width:] = uv_packed
    return nv12

def get_hw(pro):
    if pro.layout == "NCHW":
        return pro.shape[2], pro.shape[3]
    else:
        return pro.shape[1], pro.shape[2]

def print_properties(pro):
    print("tensor type:", pro.tensor_type)
    print("data type:", pro.dtype)
    print("layout:", pro.layout)
    print("shape:", pro.shape)

def write_result(result):
    with open('/home/wheeltec/wheeltec_ros2/install/wheeltec_nav2/lib/wheeltec_nav2/recognition', 'w') as file:
        file.write(result)

def check_start_condition(file_path):
    try:
        with open(file_path, 'r+') as file:
            content = file.read().strip()
            if content == 'done':
                file.seek(0)
                file.truncate()
                return True
            return False
    except FileNotFoundError:
        return False

def perform_detection(models):
    cap = cv2.VideoCapture(8)
    if not cap.isOpened():
        print("Error: Cannot open camera")
        return False

    start_time = time.time()
    detection_times = []

    while time.time() - start_time < 5:
        ret, frame = cap.read()
        if not ret:
            print("Error: Unable to read camera frame")
            break

        h, w = get_hw(models[0].inputs[0].properties)
        des_dim = (w, h)
        resized_data = cv2.resize(frame, des_dim, interpolation=cv2.INTER_AREA)

        nv12_data = bgr2nv12_opencv(resized_data)
        outputs = models[0].forward(nv12_data)

        prediction_bbox = postprocess(outputs, model_hw_shape=(640, 640), origin_image=frame)

        if len(prediction_bbox) > 5:
            detection_times.append(time.time())

    cap.release()
    return True


def main():
    connection_file_path = '/home/wheeltec/wheeltec_ros2/install/wheeltec_nav2/lib/wheeltec_nav2/connection'
    models = dnn.load('/home/wheeltec/Desktop/my/best1v5-640.bin')
    print_properties(models[0].inputs[0].properties)
    print(len(models[0].outputs))
    for output in models[0].outputs:
        print_properties(output.properties)

    done_count = 0

    try:
        while True:
            print("Waiting for 'done' command to start...")
            while not check_start_condition(connection_file_path):
                time.sleep(1)

            done_count += 1

            if perform_detection(models):
                if done_count < 3:
                    write_result("undamaged")
                    print("undamaged")
                else:
                    write_result("damaged")
                    print("damaged")
                    break

    finally:
        print("camera damage detection complete")

if __name__ == '__main__':
    main()

