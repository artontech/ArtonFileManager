''' io '''
import base64
import codecs
import hashlib
import io
import os
import shutil
import zlib
from urllib import parse
from Cryptodome.Cipher import AES
from Cryptodome.Random import get_random_bytes

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
        for root, _, files in os.walk(path):
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


def get_sha_256(data: bytes):
    ''' SHA-256 '''
    return hashlib.sha256(data).hexdigest()


def get_md5(data: bytes):
    ''' MD5 '''
    return hashlib.md5(data).hexdigest()

def get_crc_32(data: bytes):
    ''' CRC-32 '''
    chunk_size = 1024 * 1024
    chunk_start = 0
    crc = 0
    data_len = len(data)

    while chunk_start < data_len:
        chunk_next = chunk_start + chunk_size
        crc = zlib.crc32(data[chunk_start:chunk_next], crc)
        chunk_start = chunk_next
    return crc

def get_file_crc_32(path: str):
    ''' CRC-32 '''
    chunk_size = 1024 * 1024
    crc = 0

    with open(path, "rb") as fp:
        while True:
            buffer = fp.read(chunk_size)
            if len(buffer) <= 0:
                return crc
            crc = zlib.crc32(buffer, crc)

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

def random_key(key_len: int) -> str:
    return parse.quote(base64.b64encode(get_random_bytes(key_len)))

def decode_key(key: str) -> str:
    return base64.b64decode(parse.unquote(key))

def encrypt_data_to(data: bytes, key: str, dst: str, calc_crc_in=False, calc_crc_out=False):
    ''' AES encrypt '''
    chunk_size = 10240 * AES.block_size
    chunk_start = 0
    crc32_in = 0
    crc32_out = 0

    key_bytes = decode_key(key)
    cipher = AES.new(key_bytes, AES.MODE_EAX)

    with open(dst, "wb+") as file_out:
        tag = bytes(AES.block_size)
        file_out.write(cipher.nonce)
        file_out.write(tag) # Placeholder
        crc32_out = zlib.crc32(tag, zlib.crc32(cipher.nonce, crc32_out))

        while True:
            chunk_next = chunk_start + chunk_size
            chunk_in = data[chunk_start:chunk_next]
            chunk_out = cipher.encrypt(chunk_in)
            if len(chunk_out) == 0:
                break
            if calc_crc_in:
                crc32_in = zlib.crc32(chunk_in, crc32_in)
            if calc_crc_out:
                crc32_out = zlib.crc32(chunk_out, crc32_out)
            file_out.write(chunk_out)
            chunk_start = chunk_next
    return crc32_in, crc32_out

def decrypt_file(path: str, key: str):
    ''' AES decrypt '''
    key_bytes = decode_key(key)

    with open(path, "rb") as file_in:
        nonce, tag, ciphertext = [file_in.read(x) for x in (16, 16, -1)]

    cipher = AES.new(key_bytes, AES.MODE_EAX, nonce)
    data = cipher.decrypt_and_verify(ciphertext, tag)

    return data

def decrypt_file_stream(path: str, key: str, file_out: io.FileIO = None, calc_crc_in=False, calc_crc_out=False):
    ''' AES decrypt with crc32 checksum '''
    buffer = bytearray()
    def write_buffer(data: bytes):
        ''' Write chunk to buffer '''
        buffer.extend(data)
    def write_file(data: bytes):
        ''' Write chunk to file '''
        file_out.write(data)
        file_out.flush()
    writer = write_file if file_out else write_buffer
    chunk_size = 10240 * AES.block_size
    key_bytes = decode_key(key)
    crc32_in = 0
    crc32_out = 0

    with open(path, "rb") as file_in:
        nonce = file_in.read(AES.block_size)
        tag = file_in.read(AES.block_size) # TODO: tag check
        crc32_in = zlib.crc32(tag, zlib.crc32(nonce, crc32_in))

        cipher = AES.new(key_bytes, AES.MODE_EAX, nonce)

        while True:
            chunk_in = file_in.read(chunk_size)
            chunk_out = cipher.decrypt(chunk_in)
            if len(chunk_out) == 0:
                break
            if calc_crc_in:
                crc32_in = zlib.crc32(chunk_in, crc32_in)
            if calc_crc_out:
                crc32_out = zlib.crc32(chunk_out, crc32_out)
            writer(chunk_out)

    return bytes(buffer), crc32_in, crc32_out

def decrypt_file_to(path: str, key: str, dst: str):
    ''' AES decrypt '''
    with open(dst, "wb+") as file_out:
        decrypt_file_stream(path, key, file_out=file_out)

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
