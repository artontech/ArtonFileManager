''' baidunetdisk '''
from backend.model.default import DefaultModel

class OSS(DefaultModel):
    id = None
    attribute = 0
    path = None

    # viewer

def get_oss_list(db_results):
    result = []
    if db_results is None or len(db_results) <= 0:
        return result

    for i in db_results:
        row = db_results[i]
        obj = OSS()
        obj.id = row[0]
        obj.attribute = row[1]
        obj.path = row[2]
        result.append(obj)
    return result
