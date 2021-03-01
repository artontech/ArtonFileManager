''' netdisk '''
from backend.model.default import DefaultModel

class Netdisk(DefaultModel):
    id = None
    type = ""
    api_key = ""
    secret_key = ""
    redirect_uri = ""
    upload_root = ""
    access_token = ""
    token_expire = None
    refresh_token = ""

    # viewer

def get_netdisk_list(db_results):
    result = []
    if db_results is None or len(db_results) <= 0:
        return result

    for i in range(len(db_results)):
        row = db_results[i]
        obj = Netdisk()
        obj.id = row[0]
        obj.type = row[1]
        obj.api_key = row[2]
        obj.secret_key = row[3]
        obj.redirect_uri = row[4]
        obj.upload_root = row[5]
        obj.access_token = row[6]
        obj.token_expire = row[7]
        result.append(obj)
    return result
