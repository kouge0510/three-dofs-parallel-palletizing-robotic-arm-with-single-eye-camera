import numpy as np
import cv2
import os
from hobot_dnn import pyeasy_dnn as dnn
from bputools.format_convert import imequalresize, bgr2nv12_opencv

import lib.pyyolotools as yolotools

def get_hw(pro):
    if pro.layout == "NCHW":
        return pro.shape[2], pro.shape[3]
    else:
        return pro.shape[1], pro.shape[2]

def format_yolov5(frame):
    row, col, _ = frame.shape
    _max = max(col, row)
    result = np.zeros((_max, _max, 3), np.uint8)
    result[0:row, 0:col] = frame
    return result


model_path = '/home/wheeltec/Desktop/my/best1v5-640.bin'
classes_name_path = '/home/wheeltec/Desktop/my/coco_classes.names'
models = dnn.load(model_path)
model_h, model_w = get_hw(models[0].inputs[0].properties)
print("Model Height:", model_h, "Model Width:", model_w)

thre_confidence = 0.4
thre_score = 0.25
thre_nms = 0.45
colors = [(255, 255, 0), (0, 255, 0), (0, 255, 255), (255, 0, 0)]


cap = cv2.VideoCapture(8)  # 

# 
while True:
    ret, frame = cap.read()  # 
    if not ret:
        print("Error: Couldn't capture frame")
        break

    inputImage = format_yolov5(frame)
    img = imequalresize(inputImage, (model_w, model_h))
    nv12 = bgr2nv12_opencv(img)

    t1 = cv2.getTickCount()
    outputs = models[0].forward(nv12)
    t2 = cv2.getTickCount()
    outputs = outputs[0].buffer
    print('Inference time: {0} ms'.format((t2 - t1) * 1000 / cv2.getTickFrequency()))

    image_width, image_height, _ = inputImage.shape
    fx, fy = image_width / model_w, image_height / model_h
    t1 = cv2.getTickCount()
    class_ids, confidences, boxes = yolotools.pypostprocess_yolov5(outputs[0][:, :, 0], fx, fy,
                                                                   thre_confidence, thre_score, thre_nms)
    print(class_ids)
    print(boxes)
    t2 = cv2.getTickCount()
    print('Post-processing time: {0} ms'.format((t2 - t1) * 1000 / cv2.getTickFrequency()))
    
    with open(classes_name_path, "r") as f:
        class_list = [cname.strip() for cname in f.readlines()]

    for (classid, confidence, box) in zip(class_ids, confidences, boxes):
        color = colors[int(classid) % len(colors)]
        cv2.rectangle(frame, box, color, 2)
        cv2.rectangle(frame, (box[0], box[1] - 20), (box[0] + box[2], box[1]), color, -1)
        #cv2.putText(frame, str(classid), (box[0], box[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, .5, (0, 0, 0))
        cv2.putText(frame, class_list[classid], (box[0], box[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, .5, (0,0,0))
        print(class_list)
    cv2.imshow('frame', frame)  # 
    if cv2.waitKey(1) & 0xFF == ord('q'):  # 
        break

# 
cap.release()
cv2.destroyAllWindows()
