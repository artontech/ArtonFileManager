''' io '''
from Cryptodome.Cipher import AES
import base64
import codecs
from Cryptodome.Random import get_random_bytes
import hashlib
import os
from urllib import parse
import shutil
import zlib

FILE_TYPE_MAP = {
# Image format
"bmp": {"ico": "image", "cv": True, "web_img": True},
"dib": {"ico": "image", "cv": True},
"jp2": {"ico": "image", "cv": True},
"jpe": {"ico": "image", "cv": True},
"jpg": {"ico": "image", "cv": True, "web_img": True},
"jpeg": {"ico": "image", "cv": True, "web_img": True}, 
"pbm": {"ico": "image", "cv": True},
"pgm": {"ico": "image", "cv": True},
"png": {"ico": "image", "cv": True, "web_img": True},
"ppm": {"ico": "image", "cv": True}, 
"ras": {"ico": "image", "cv": True},
"sr": {"ico": "image", "cv": True},
"tif": {"ico": "image", "cv": True},
"tiff": {"ico": "image", "cv": True},
"webp": {"ico": "image", "cv": True, "web_img": True},
"ico": {"ico": "image", "web_img": True},
"jfif": {"ico": "image", "cv": True, "web_img": True},

# Video format
"avi": {"ico": "video", "web": True},
"f4v": {"ico": "video"},
"flv": {"ico": "video"},
"gif": {"ico": "video", "web": True, "web_img": True},
"kux": {"ico": "video"},
"mkv": {"ico": "video"},
"mov": {"ico": "video"},
"mp4": {"ico": "video", "web": True},
"mpg": {"ico": "video"},
"rm": {"ico": "video"},
"wmv": {"ico": "video"},

# Music format
"mp3": {"ico": "music"},

# Other format
"css": {"ico": "txt"},
"html": {"ico": "txt"},
"txt": {"ico": "txt"},
"ini": {"ico": "config"},
"exe": {"ico": "exe"},
"py": {"ico": "exe"},
}

def get_file_type(ext: str) -> dict:
    return FILE_TYPE_MAP.get(ext.strip('.'), {})

def is_cv_support(ext: str) -> bool:
    if ext == "":
        return False
    return get_file_type(ext).get("cv", False)

def is_web_img(ext: str) -> bool:
    if ext == "":
        return False
    return get_file_type(ext).get("web_img", False)

def get_icon_name(ext: str) -> bool:
    default = "unknown"
    if ext == "":
        return default
    return get_file_type(ext).get("ico", default)

def get_file_size(path: str):
    ''' get file size '''
    if os.path.isfile(path):
        return os.path.getsize(path)
    return None


def get_dir_size(path: str):
    ''' get dir size '''
    if os.path.isdir(path):
        sumsize = 0
        for root, dirs, files in os.walk(path):
            for f in files:
                size = os.path.getsize(os.path.join(root, f))
                sumsize += size
        return sumsize
    return None


def get_size(path: str):
    ''' get file/dir size '''
    if os.path.isfile(path):
        return os.path.getsize(path)
    else:
        return get_dir_size(path)
    return None


def get_sha_256(f: bytes):
    ''' SHA-256 '''
    return hashlib.sha256(f).hexdigest()


def get_md5(f: bytes):
    ''' MD5 '''
    return hashlib.md5(f).hexdigest()

def get_crc_32(f: bytes):
    ''' CRC-32 '''
    return zlib.crc32(f)

def format_file_name(size: int, crc32: int, sha256: str, ext: str):
    if size is None:
        size = 0
    if crc32 is None:
        crc32 = 0
    if ext is None:
        ext = ""
    return "%x_%x_%s%s" % (size, crc32, sha256, ext)

def get_relative_path(root: str, path: str) -> str:
    ''' relative path '''
    root = os.path.abspath(root)
    path = os.path.abspath(path)
    return path.replace(root, "")

def copyfile(src: str, dst: str):
    ''' copy file '''
    shutil.copyfile(src, dst)

def random_key(len: int) -> str:
    return parse.quote(base64.b64encode(get_random_bytes(len)))

def decode_key(key: str) -> str:
    return base64.b64decode(parse.unquote(key))

def encrypt_data_to(f: bytes, key: str, dst: str):
    ''' AES encrypt '''
    key_bytes = decode_key(key)

    cipher = AES.new(key_bytes, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(f)

    with open(dst, "wb+") as file_out:
        for x in (cipher.nonce, tag, ciphertext):
            file_out.write(x)

def decrypt_file(path: str, key: str):
    ''' AES decrypt '''
    key_bytes = decode_key(key)

    with open(path, "rb") as file_in:
        nonce, tag, ciphertext = [file_in.read(x) for x in (16, 16, -1)]

    cipher = AES.new(key_bytes, AES.MODE_EAX, nonce)
    data = cipher.decrypt_and_verify(ciphertext, tag)

    return data

def decrypt_file_to(path: str, key: str, dst: str):
    ''' AES decrypt '''
    data = decrypt_file(path, key)

    with open(dst, "wb+") as file_out:
        file_out.write(data)

def read_text_file(path: str) -> str:
    with codecs.open(path, "r", "utf-8") as fp:
        return fp.read()

def replace_file_content(src_path: str, dst_path: str, rules: list):
    ''' replace text file content '''
    content = read_text_file(src_path)
    for rule in rules:
        content = content.replace(*rule)
    with open(dst_path, "w+") as fp:
        fp.write(content)
