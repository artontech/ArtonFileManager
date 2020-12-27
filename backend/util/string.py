''' string '''

import base64
import os

def join(str1: str, str2: str) -> str:
    ''' join string '''
    if str1 is None:
        str1 = ''
    if str2 is None:
        str2 = ''
    return str1 + str2

def str2bool(data: str, default: bool = None) -> bool:
    ''' trans to bool '''
    l_str = str(data).lower()
    if l_str == "true":
        return True
    if l_str == "false":
        return False
    return default

def str2base64(data: str, encoding: str = "utf-8") -> str:
    ''' trans to base64 '''
    return base64.b64encode(data.encode(encoding)).decode()

def relative_path(path1: str, path2: str) -> str:
    ''' calc relative path '''
    path1, path2 = path1.split(os.sep), path2.split(os.sep)
    intersection = 0
    for index in range(min(len(path1), len(path2))):
        m, n = path1[index], path2[index]
        if m != n:
            intersection = index
            break

    def backward():
        return (len(path1) - intersection - 1) * ('..' + os.sep)

    def forward():
        return os.sep.join(path2[intersection:])

    out = backward() + forward()
    return out
