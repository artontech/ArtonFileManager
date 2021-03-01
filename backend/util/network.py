'''network '''

import json
from json.decoder import JSONDecodeError
import logging
import time
import requests

def request(method, url, max_retry: int = 0, retry_delay: int = 1, **kwargs):
    ''' request '''
    resp_json = {}
    retry = 0
    while True:
        try:
            response = requests.request(method, url, **kwargs)
            resp_json = json.loads(response.text.encode('utf8'))
            break
        except (requests.exceptions.ConnectionError, JSONDecodeError) as e:
            logging.warning("Request %s, retry %d, %s", url, retry, e)
            retry += 1
            if max_retry is not None and retry > max_retry:
                break
            time.sleep(retry_delay)
    return resp_json
