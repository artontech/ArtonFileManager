''' Baidu Netdisk '''

import datetime
import json
import logging
import os
import time
import requests
import tornado.gen
from tornado.concurrent import run_on_executor

from backend.controller.default import (DefaultHandler, DefaultWSHandler)
from backend.model.baidunetdisk import BaiduNetdisk
from backend.service import workspace
from backend.util import (io, network)

USE_LOGIC_DELETE = True
MAX_RETRY = 20


class BaiduWebSocket(DefaultWSHandler):
    name = "baidu"

    def open(self):
        logging.info("[ws] Baidu WebSocket opened")

    def on_message(self, msg):
        msg_json = json.loads(msg, strict=False)
        msg_type = msg_json.get("type", None)
        if msg_type == "init":
            wid = msg_json.get("wid", None)
            logging.info("[ws] baidu init: wid=%s", wid)
            if wid is None:
                self.write_json(msg_type="init", err="no_wid")
                return

            self.space = workspace.get_by_id(wid)
            if self.space is None or not self.space.enabled:
                self.write_json(msg_type="init", err="no_workspace")
                return
            self.space.add_ws(self)
            self.write_json(msg_type="init", status="success",
                            data=self.space.serializable())

    def on_close(self):
        logging.info("[ws] close")
        if hasattr(self, "space") and self.space is not None:
            self.space.del_ws(self)


class OAuth(DefaultHandler):
    ''' OAuth login '''

    def data_received(self, chunk):
        pass

    def get(self):
        ''' get '''
        self.post()

    def post(self):
        ''' post '''
        wid = self.get_arg("state")
        code = self.get_arg("code")

        # get workspace first
        space = workspace.get_by_id(wid)
        if space is None or not space.enabled:
            self.write_json(err="no_workspace")
            return

        # get netdisk info
        netdisks = space.driver.get_netdisks(type_name="baidu")
        if netdisks is None:
            self.write_json(err="db")
            return
        if len(netdisks) < 1:
            self.write_json(err="no_netdisk")
            return
        netdisk_info = netdisks[0]

        # OAuth
        url = "https://openapi.baidu.com/oauth/2.0/token?grant_type=authorization_code&\
code=%s&client_id=%s&client_secret=%s&redirect_uri=%s" % (code, netdisk_info.api_key,
                                                          netdisk_info.secret_key,
                                                          netdisk_info.redirect_uri)
        response = requests.get(url)
        logging.warning("Baidu OAuth result: %s", response.text)

        res_json = json.loads(response.text)
        token = res_json.get("access_token", None)
        expires_in = int(res_json.get("expires_in", -1))
        scope = res_json.get("scope", None)
        if token is None or expires_in == -1 or scope is None:
            self.write_json(err="no_token")
            return

        # update netdisk info
        netdisk_info.access_token = token
        netdisk_info.token_expire = datetime.datetime.now(
        )+datetime.timedelta(seconds=expires_in)
        ok = space.driver.update_netdisk(netdisk_info)
        if not ok:
            self.write_json(err="db")
            return
        space.driver.commit()

        self.write_json(status="success", data=token)


class Token(DefaultHandler):
    ''' get token '''

    def data_received(self, chunk):
        pass

    def get(self):
        ''' get '''
        self.post()

    def post(self):
        ''' post '''
        wid = self.get_arg("wid")

        # get workspace first
        space = workspace.get_by_id(wid)
        if space is None or not space.enabled:
            self.write_json(err="no_workspace")
            return

        # get netdisk info
        netdisks = space.driver.get_netdisks(type_name="baidu")
        if netdisks is None:
            self.write_json(err="db")
            return
        if len(netdisks) < 1:
            self.write_json(err="no_netdisk")
            return
        netdisk_info = netdisks[0]

        if netdisk_info.token_expire is None or \
                datetime.datetime.now()+datetime.timedelta(hours=8) >= netdisk_info.token_expire:
            self.write_json(err="token_expire", data=netdisk_info)
            return

        netdisk_info.secret_key = None
        self.write_json(status="success", data=netdisk_info)


class UserInfo(DefaultHandler):
    ''' get user info '''

    def data_received(self, chunk):
        pass

    def get(self):
        ''' get '''
        self.post()

    def post(self):
        ''' post '''
        access_token = self.get_arg("access_token")

        url = "https://pan.baidu.com/rest/2.0/xpan/nas?access_token=%s&method=uinfo" % (
            access_token)
        payload = {}
        headers = {
            'User-Agent': 'pan.baidu.com'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        res_json = json.loads(response.text.encode('utf8'))
        self.write_json(status="success", data=res_json)


class Quota(DefaultHandler):
    ''' get quota '''

    def data_received(self, chunk):
        pass

    def get(self):
        ''' get '''
        self.post()

    def post(self):
        ''' post '''
        access_token = self.get_arg("access_token")

        url = "https://pan.baidu.com/api/quota?access_token=%s&checkfree=0&checkexpire=1" % (
            access_token)
        payload = {}
        headers = {
            'User-Agent': 'pan.baidu.com'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        res_json = json.loads(response.text.encode('utf8'))
        self.write_json(status="success", data=res_json)


class Sync(DefaultHandler):
    ''' sync '''

    def data_received(self, chunk):
        pass

    def get(self):
        ''' get '''
        self.post()

    @tornado.gen.coroutine
    def post(self):
        ''' post '''
        wid = self.get_arg("wid")
        access_token = self.get_arg("access_token")
        upload_root = self.get_arg("upload_root")
        vip_type = int(self.get_arg("vip_type"))

        # get workspace first
        space = workspace.get_by_id(wid)
        if space is None or not space.enabled:
            self.write_json(err="no_workspace")
            return

        yield self.sync(space, access_token, upload_root, vip_type)

    @run_on_executor
    def sync(self, space, access_token, upload_root, vip_type):
        # get attributes
        attrs = space.driver.union_attribute_baidunetdisks()
        if attrs is None:
            self.write_json(err="db")
            return
        attr_len = len(attrs)
        space.send_ws(name="baidu", msg_type="check", status="success", data={
            "total": attr_len
        })
        url_pre = "http://pan.baidu.com/rest/2.0/xpan/file?method=precreate&access_token=%s" % (
            access_token)
        payload = {
            'rtype': '1',
            'isdir': '0',
            'autoinit': '1',
        }
        if vip_type == 0:
            block_size = 4*1024*1024
        elif vip_type == 1:
            block_size = 16*1024*1024
        elif vip_type == 2:
            block_size = 32*1024*1024
        else:
            self.write_json(err="invalid_vip_type")
            return
        last_err = ""
        for i in range(attr_len):
            retry = 0
            while retry < MAX_RETRY:
                if retry > 3:
                    time.sleep(360)
                elif retry > 0:
                    time.sleep(36)
                retry += 1
                attr = attrs[i]
                hash_file_name = io.format_file_name(
                    attr.size, attr.crc32, attr.sha256, None)
                target_path = os.path.abspath(
                    os.path.join(space.data_path, hash_file_name))
                upload_path = '%s/%s' % (upload_root, hash_file_name)

                with open(target_path, "rb") as f:
                    file_data = f.read()
                file_size = len(file_data)
                blocks = []
                blocks_md5 = []
                for j in range(int(file_size / block_size)+1):
                    block = file_data[j*block_size:j*block_size+block_size]
                    blocks.append(block)
                    blocks_md5.append(str(io.get_md5(block)))
                payload['path'] = upload_path
                payload['size'] = str(file_size)
                payload['block_list'] = json.dumps(blocks_md5)
                payload['content-md5'] = str(io.get_md5(file_data))
                payload['slice-md5'] = str(io.get_md5(file_data[:262144]))
                logging.info(
                    "Attr %s, Retry %d, Pre-upload payload: %s", attr.id, retry, payload)

                # pre-upload
                headers = {'User-Agent': 'pan.baidu.com'}
                resp_pre = network.request(
                    "POST", url_pre, max_retry=None, retry_delay=10, headers=headers, data=payload, files=[])
                logging.info("Pre-upload result: %s", resp_pre)

                return_type = resp_pre.get('return_type', 0)
                if return_type == 2:
                    # exist
                    fs_id = resp_pre.get('info', {}).get('fs_id', None)
                    if fs_id is None:
                        last_err = "invalid_fs_id"
                        continue
                else:
                    # upload
                    block_list = resp_pre.get('block_list', [])
                    if len(block_list) == 0:
                        block_list.append(0)
                    uploadid = resp_pre.get('uploadid', None)
                    if uploadid is None:
                        last_err = "invalid_uploadid"
                        continue

                    # upload file
                    block_list_len = len(block_list)
                    for j in block_list:
                        upload_retry = 0
                        while upload_retry < MAX_RETRY:
                            if upload_retry > 0:
                                time.sleep(36)
                            upload_retry += 1
                            url_upload = "https://d.pcs.baidu.com/rest/2.0/pcs/superfile2?method=upload&\
    access_token=%s&path=%s&type=tmpfile&uploadid=%s&partseq=%d" % (access_token, upload_path, uploadid, j)
                            resp_upload = network.request(
                                "POST", url_upload, max_retry=None, retry_delay=20, headers=headers, data={},
                                files=[('file', blocks[j])])
                            logging.info("Upload slice %d/%d,%d result: %s",
                                        j, block_list_len, upload_retry, resp_upload)
                            if resp_upload.get('errno', 0) == 0:
                                upload_retry = 0
                                break
                        if upload_retry >= MAX_RETRY:
                            last_err = "fail_upload"
                            continue

                    # create file
                    url_create = "https://pan.baidu.com/rest/2.0/xpan/file?method=create&access_token=%s" % (
                        access_token)
                    payload['uploadid'] = uploadid
                    resp_create = network.request(
                        "POST", url_create, max_retry=None, retry_delay=20, headers=headers, data=payload, files=[])
                    logging.info("Create result: %s", resp_create)
                    fs_id = resp_create.get('fs_id', None)
                    if fs_id is None:
                        last_err = "invalid_fs_id"
                        continue

                # add baidunetdisk
                baidunetdisk = BaiduNetdisk()
                baidunetdisk.id = attr.id
                baidunetdisk.attribute = attr.id
                baidunetdisk.fs_id = fs_id
                baidunetdisk.id, ok = space.driver.add_baidunetdisk(
                    baidunetdisk)
                if not ok:
                    last_err = "db"
                    continue
                space.driver.commit()

                if i % 10 == 0:
                    space.send_ws(name="baidu", msg_type="sync", status="run", data={
                        "now": i, "total": attr_len
                    })

                # Stop retry
                retry = 0
                break
            if retry >= MAX_RETRY:
                self.write_json(err=last_err)
                return

        space.send_ws(name="baidu", msg_type="done", status="success", data={
            "total": attr_len
        })
        self.write_json(status="success", data=attr_len)
        return
