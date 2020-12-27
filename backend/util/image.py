''' image '''

import cv2
import numpy as np


def parse_image(f: bytes):
    ''' parse image '''
    nparr = np.frombuffer(f, np.uint8)
    return cv2.imdecode(nparr, cv2.IMREAD_COLOR)


def load_image(path: str):
    ''' load image '''
    return cv2.imread(path)


def a_hash(img) -> int:
    ''' 均值哈希算法 '''
    # 缩放为8*8
    img = cv2.resize(img, (8, 8))
    # 转换为灰度图
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # s为像素和初值为0，hash_str为hash值初值为''
    s = 0
    ahash = 0
    # 遍历累加求像素和
    for i in range(8):
        for j in range(8):
            s = s+gray[i, j]
    # 求平均灰度
    avg = s/64
    # 灰度大于平均值为1相反为0生成图片的hash值
    for i in range(8):
        for j in range(8):
            if gray[i, j] > avg:
                ahash += 1 << (j+8*i)
    return ahash


def d_hash(img) -> int:
    ''' 差值哈希算法 '''
    # 缩放8*8
    img = cv2.resize(img, (9, 8))
    # 转换灰度图
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    dhash = 0
    # 每行前一个像素大于后一个像素为1，相反为0，生成哈希
    for i in range(8):
        for j in range(8):
            if gray[i, j] > gray[i, j+1]:
                dhash += 1 << (j+8*i)
    return dhash


def p_hash(img) -> int:
    ''' 感知哈希算法 '''
    # 缩放32*32
    img = cv2.resize(img, (32, 32))   # , interpolation=cv2.INTER_CUBIC
    # 转换为灰度图
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # 将灰度图转为浮点型，再进行dct变换
    dct = cv2.dct(np.float32(gray))
    # opencv实现的掩码操作
    dct_roi = dct[0:8, 0:8]

    phash = 0
    avreage = np.mean(dct_roi)
    for i in range(dct_roi.shape[0]):
        for j in range(dct_roi.shape[1]):
            if dct_roi[i, j] > avreage:
                phash += 1 << (j+8*i)
    return phash


def hamming(hash1: int, hash2: int) -> int:
    ''' get hamming distance '''
    d = hash1 ^ hash2
    result = 0
    while d != 0:
        result += d & 1
        d = d >> 1
    return result


def calculate(image1, image2):
    ''' 灰度直方图算法 '''
    # 计算单通道的直方图的相似值
    hist1 = cv2.calcHist([image1], [0], None, [256], [0.0, 255.0])
    hist2 = cv2.calcHist([image2], [0], None, [256], [0.0, 255.0])
    # 计算直方图的重合度
    degree = 0
    for i in range(len(hist1)):
        if hist1[i] != hist2[i]:
            degree = degree + \
                (1 - abs(hist1[i] - hist2[i]) / max(hist1[i], hist2[i]))
        else:
            degree = degree + 1
    degree = degree / len(hist1)
    return degree
