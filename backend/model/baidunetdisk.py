''' baidunetdisk '''
from backend.model.default import DefaultModel

class BaiduNetdisk(DefaultModel):
    id = None
    attribute = 0
    fs_id = 0

    # viewer

def get_baidunetdisk_list(db_results):
    result = []
    if db_results is None or len(db_results) <= 0:
        return result

    for i in db_results:
        row = db_results[i]
        obj = BaiduNetdisk()
        obj.id = row[0]
        obj.attribute = row[1]
        obj.fs_id = row[2]
        result.append(obj)
    return result
