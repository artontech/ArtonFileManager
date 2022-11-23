''' attribute '''
from backend.model.default import DefaultModel

class Attribute(DefaultModel):
    id = None
    file = None
    type = 0
    size = 0
    encrypt_crc32 = None
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
    check_date = None

    # viewer
    fs_id = 0

    def none(self):
        ''' clear '''
        super().none()

        self.id = None
        self.file = None
        self.type = None
        self.size = None
        self.encrypt_crc32 = None
        self.crc32 = None
        self.sha256 = None
        self.ext = None
        self.width = None
        self.height = None
        self.color = None
        self.ahash = None
        self.phash = None
        self.dhash = None
        self.desc = None
        self.encrypt = None
        self.key = None
        self.delete = None
        self.check_date = None

def get_attribute(row) -> Attribute:
    obj = Attribute()
    obj.id = row[0]
    obj.file = row[1]
    obj.type = row[2]
    obj.size = row[3]
    obj.encrypt_crc32 = row[4]
    obj.crc32 = row[5]
    obj.sha256 = row[6]
    obj.ext = row[7]
    obj.width = row[8]
    obj.height = row[9]
    obj.color = row[10]
    obj.ahash = row[11]
    obj.phash = row[12]
    obj.dhash = row[13]
    obj.desc = row[14]
    obj.encrypt = row[15]
    obj.key = row[16]
    obj.delete = row[17]
    obj.check_date = row[18]
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

def union_attribute_oss_list(db_results):
    ''' union attribute oss list '''
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
