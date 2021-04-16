''' url '''
from urllib import parse

def url2path(url: str) -> str:
    ''' parse url to path '''
    path = url
    tmp = path.split("://")
    if len(tmp) > 1:
        path = tmp[1]
    path = path.replace('?', '_')
    return path

def extract_host(url: str) -> str:
    ''' extract host '''
    host = url
    tmp = host.split("://")
    if len(tmp) > 1:
        host = tmp[1]
    host = host.split("/")[0]
    return host

def encode(url: str) -> str:
    return parse.quote_plus(url)
