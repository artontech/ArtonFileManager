''' tag '''
from backend.model.default import DefaultModel

class Tag(DefaultModel):
    id = None
    key = ""
    value = ""
    delete = 0

    # viewer

def get_tag_list(db_results):
    result = []
    if db_results is None or len(db_results) <= 0:
        return result

    for i in range(len(db_results)):
        row = db_results[i]
        obj = Tag()
        obj.id = row[0]
        obj.key = row[1]
        obj.value = row[2]
        obj.delete = row[3]
        result.append(obj)
    return result
