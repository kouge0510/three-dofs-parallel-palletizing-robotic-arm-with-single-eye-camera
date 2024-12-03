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

# img_path 图像完整路径
img_path = '/home/sunrise/Desktop/my/1.jpg'
# model_path 量化模型完整路径
model_path = '/home/sunrise/Desktop/my/newbestv5-640.bin'
# 类别名文件
classes_name_path = '/home/sunrise/Desktop/my/coco_classes.names'
# 设置参数
thre_confidence = 0.4
thre_score = 0.25
thre_nms = 0.45
# 框颜色设置
colors = [(255, 255, 0), (0, 255, 0), (0, 255, 255), (255, 0, 0)]

# 1. 加载模型，获取所需输出HW
models = dnn.load(model_path)
model_h, model_w = get_hw(models[0].inputs[0].properties)
print(model_h, model_w)

# 2 加载图像，根据前面模型，转换后的模型是以NV12作为输入的
# 但在OE验证的时候，需要将图像再由NV12转为YUV444
imgOri = cv2.imread(img_path)
inputImage = format_yolov5(imgOri)
img = imequalresize(inputImage, (model_w, model_h))
nv12 = bgr2nv12_opencv(img)

# 3 模型推理
t1 = cv2.getTickCount()
outputs = models[0].forward(nv12)
t2 = cv2.getTickCount()
outputs = outputs[0].buffer # 25200x85x1 
print('time consumption {0} ms'.format((t2-t1)*1000/cv2.getTickFrequency()))

# 4 后处理
image_width, image_height, _ = inputImage.shape
fx, fy = image_width / model_w, image_height / model_h
t1 = cv2.getTickCount()
class_ids, confidences, boxes = yolotools.pypostprocess_yolov5(outputs[0][:, :, 0], fx, fy, 
                                                            thre_confidence, thre_score, thre_nms)
t2 = cv2.getTickCount()
print('post consumption {0} ms'.format((t2-t1)*1000/cv2.getTickFrequency()))


# 5 绘制检测框
with open(classes_name_path, "r") as f:
    class_list = [cname.strip() for cname in f.readlines()]
t1 = cv2.getTickCount()
for (classid, confidence, box) in zip(class_ids, confidences, boxes):
    color = colors[int(classid) % len(colors)]
    cv2.rectangle(imgOri, box, color, 2)
    cv2.rectangle(imgOri, (box[0], box[1] - 20), (box[0] + box[2], box[1]), color, -1)
    cv2.putText(imgOri, class_list[classid], (box[0], box[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, .5, (0,0,0))
t2 = cv2.getTickCount()
print('draw rect consumption {0} ms'.format((t2-t1)*1000/cv2.getTickFrequency()))

cv2.imwrite('res.png', imgOri)
