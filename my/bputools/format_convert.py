import numpy as np
import cv2
from PIL import Image


def imequalresize(img, target_size, pad_value=127.):
    target_w, target_h = target_size
    image_h, image_w = img.shape[:2]
    img_channel = 3 if len(img.shape) > 2 else 1

    # 确定缩放尺度，确定最终目标尺寸
    scale = min(target_w * 1.0 / image_w, target_h * 1.0 / image_h)
    new_h, new_w = int(scale * image_h), int(scale * image_w)

    resize_image = cv2.resize(img, (new_w, new_h))

    # 准备待返回图像
    pad_image = np.full(shape=[target_h, target_w, img_channel], fill_value=pad_value)

    # 将图像resize_image放置在pad_image的中间
    dw, dh = (target_w - new_w) // 2, (target_h - new_h) // 2
    pad_image[dh:new_h + dh, dw:new_w + dw, :] = resize_image

    return pad_image

def bgr2nv12_opencv(image):
    image = image.astype(np.uint8)
    height, width = image.shape[0], image.shape[1]
    yuv420p = cv2.cvtColor(image, cv2.COLOR_BGR2YUV_I420).reshape(
        (height * width * 3 // 2, ))
    y = yuv420p[:height * width]
    uv_planar = yuv420p[height * width:].reshape(
        (2, height * width // 4))
    uv_packed = uv_planar.transpose((1, 0)).reshape(
        (height * width // 2, ))
    nv12 = np.zeros_like(yuv420p)
    nv12[:height * width] = y
    nv12[height * width:] = uv_packed
    return nv12


def nv122yuv444(imgnv12, img_size):
    nv12_data = imgnv12.flatten()
    imgw, imgh = img_size[:2]
    yuv444 = np.empty([imgh, imgw, 3], dtype=np.uint8)
    yuv444[:, :, 0] = nv12_data[:imgw * imgh].reshape(imgh, imgw)
    u = nv12_data[imgw * imgh::2].reshape(imgh // 2, imgw // 2)
    yuv444[:, :, 1] = Image.fromarray(u).resize((imgw, imgh), resample=0)
    v = nv12_data[imgw * imgh + 1::2].reshape(imgh // 2, imgw // 2)
    yuv444[:, :, 2] = Image.fromarray(v).resize((imgw, imgh), resample=0)
    return yuv444.astype(np.int8)