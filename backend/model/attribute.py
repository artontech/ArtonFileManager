''' attribute '''
from backend.model.default import DefaultModel

class Attribute(DefaultModel):
    id = None
    file = None
    type = 0
    size = 0
    crc32 = 0
    sha256 = ""
    ext = ""
    width = 0
    height = 0
    color = ""
    ahash = 0
    phash = 0
    dhash = 0
    desc = ""
    encrypt = ""
    key = ""
    delete = 0

    # viewer
    fs_id = 0

def get_attribute(row) -> Attribute:
    obj = Attribute()
    obj.id = row[0]
    obj.file = row[1]
    obj.type = row[2]
    obj.size = row[3]
    obj.crc32 = row[4]
    obj.sha256 = row[5]
    obj.ext = row[6]
    obj.width = row[7]
    obj.height = row[8]
    obj.color = row[9]
    obj.ahash = row[10]
    obj.phash = row[11]
    obj.dhash = row[12]
    obj.desc = row[13]
    obj.encrypt = row[14]
    obj.key = row[15]
    obj.delete = row[16]
    return obj

def get_attribute_list(db_results):
    result = []
    if db_results is None or len(db_results) <= 0:
        return result

    for row in db_results:
        result.append(get_attribute(row))
    return result

def union_attribute_baidunetdisk_list(db_results):
    ''' union attribute baidunetdisk list '''
    result = []
    if db_results is None or len(db_results) <= 0:
        return result

    for row in db_results:
        obj = Attribute()
        obj.id = row[0]
        obj.size = row[1]
        obj.crc32 = row[2]
        obj.sha256 = row[3]
        obj.fs_id = row[4]
        result.append(obj)
    return result
