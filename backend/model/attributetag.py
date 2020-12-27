''' Attribute tag '''
from backend.model.default import DefaultModel

class AttributeTag(DefaultModel):
    ''' AttributeTag '''
    id = None
    tag_id = None
    target = None
    type = None
    delete = 0

    # viewer
    key = ""
    value = ""

def get_attribute_tag_list(db_results):
    ''' get attribute tag list '''
    result = []
    if db_results is None or len(db_results) <= 0:
        return result

    for row in db_results:
        obj = AttributeTag()
        obj.id = row[0]
        obj.tag_id = row[1]
        obj.target = row[2]
        obj.type = row[3]
        obj.delete = row[4]
        result.append(obj)
    return result

def union_attribute_tag_list(db_results):
    ''' union attribute tag list '''
    result = []
    if db_results is None or len(db_results) <= 0:
        return result

    for row in db_results:
        obj = AttributeTag()
        obj.id = row[0]
        obj.tag_id = row[1]
        obj.target = row[2]
        obj.type = row[3]
        obj.delete = row[4]
        obj.key = row[5]
        obj.value = row[6]
        result.append(obj)
    return result
