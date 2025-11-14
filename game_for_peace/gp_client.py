import hashlib
import time

import requests

from game_for_peace.account import get_account_manager
from game_for_peace.device_info import DeviceInfoManager


class GpRequestClient:
    def __init__(self, account_manager, session=None):
        self.account_manager = account_manager
        self.device_manager = DeviceInfoManager()
        self.session = session or requests.Session()
        self.session.headers.update({"User-Agent": "FkG4P-Python"})
        self.base_url = "https://formal.api.gp.qq.com"

    def _post(self, path=None, data=None, json_data=None, full_url=None):
        if not full_url:
            url = f"{self.base_url}/{path.lstrip('/')}"
        else:
            url = full_url
        resp = self.session.post(url, data=data, json=json_data, timeout=30)
        resp.raise_for_status()
        return resp

    def request_wx_sdk_ticket(self):
        resp = self._post("user/getwxsdkticket")
        payload = resp.json()
        ticket = payload.get("data")
        if not ticket:
            raise RuntimeError("no sdk ticket returned")
        return ticket

    def request_wx_login_qr_code(self, sdk_ticket):
        now_ms = str(int(time.time() * 1000))
        app_id = "wxb7659468ecf2f4ce"
        to_sign = f"appid={app_id}&noncestr={now_ms}&sdk_ticket={sdk_ticket}&timestamp={now_ms}"
        signature = hashlib.sha1(to_sign.encode()).hexdigest()
        resp = self.session.get(
            "https://open.weixin.qq.com/connect/sdk/qrconnect",
            params={
                "appid": app_id,
                "noncestr": now_ms,
                "timestamp": now_ms,
                "scope": "snsapi_userinfo",
                "signature": signature,
            },
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        if "qrcode" not in data:
            raise RuntimeError("qr code response invalid")
        return data

    def request_qr_code_scan_status(self, uuid, last_status=None):
        try:
            params = {"uuid": uuid, "f": "json"}
            if last_status is not None:
                params["last"] = last_status
            resp = self.session.get(
                "https://long.open.weixin.qq.com/connect/l/qrconnect",
                params=params,
                headers={
                    "User-Agent": "Apache-HttpClient/UNAVAILABLE (java 1.4)",
                    "Connection": "Keep-Alive",
                },
                timeout=10,
            )
            resp.raise_for_status()
            return resp.json()
        except Exception:
            return None

    def get_personal_auth(self, open_id):
        resp = self._post(
            "user/getpersonalauth",
            json_data={
                "accessToken": "",
                "loginType": "wx",
                "openid": open_id,
            },
        )
        return resp.text

    def login(self, open_id):
        form = self.device_manager.get_common_info()
        form.update(
            {
                "code": open_id,
                "loginType": "wx",
                "autoLogin": "0",
                "gameOpenId": self.account_manager.game_open_id,
                "uin": "",
                "accessToken": "",
                "lastGetRemarkTime": "0",
                "lastLoginTime": "0",
                "appOpenid": "",
                "payToken": "",
            }
        )
        resp = self._post("user/login", data=form)
        result = resp.json()
        data = result.get("data")
        if not data:
            raise RuntimeError("login failed")
        return data

    def get_all_roles(self):
        info = self.account_manager.login_info
        form = self.device_manager.get_common_info()
        form.update(
            {
                "openId": info["appOpenid"],
                "gameOpenId": self.account_manager.game_open_id,
                "gameId": self.account_manager.game_id,
                "userId": info["userId"],
                "token": info["token"],
                "friendUserId": info["userId"],
            }
        )
        resp = self._post("game/allrolelistv2", data=form)
        payload = resp.json()
        data = payload.get("data") or {}
        roles = data.get("20004") or data.get("roles")
        if roles is None:
            raise RuntimeError("role list missing")
        return roles

    def get_recent_battle_list(self, role_id=None, count=10):
        info = self.account_manager.login_info
        form = self.device_manager.get_common_info()
        form.update(
            {
                "openId": info["appOpenid"],
                "gameOpenId": self.account_manager.game_open_id,
                "gameId": self.account_manager.game_id,
                "roleId": role_id or self._default_role_id(),
                "userId": info["userId"],
                "token": info["token"],
                "pageSize": count
            }
        )
        resp = self._post("play/getrecentbattlelist", data=form)
        payload = resp.json()
        data = payload.get("data")
        if not data:
            raise RuntimeError("error request")
        return data
    
    def get_battle_mode_tabs(self):
        info = self.account_manager.login_info
        form = self.device_manager.get_common_info()
        form.update(
            {
                "openId": info["appOpenid"],
                "gameOpenId": self.account_manager.game_open_id,
                "gameId": self.account_manager.game_id,
                "userId": info["userId"],
                "friendUserId": info["userId"],
                "token": info["token"]
            }
        )
        resp = self._post("play/getbattlefilters", data=form)
        payload = resp.json()
        data = payload.get("data")
        if not data:
            raise RuntimeError("error request")
        return data

    def get_pubg_battle_list(self, role_id=None, page=1, count=20, tabIndex=1, modes="101"):
        info = self.account_manager.login_info
        form = self.device_manager.get_common_info()
        form.update(
            {
                "openId": info["appOpenid"],
                "page": page,
                "pageSize": count,
                "gameOpenId": self.account_manager.game_open_id,
                "gameId": self.account_manager.game_id,
                "roleId": role_id or self._default_role_id(),
                "userId": info["userId"],
                "token": info["token"],
                "filter": "0",
                "tabIndex": tabIndex,
                "mode": modes
            }
        )
        resp = self._post("play/getpubgbattlelist", data=form)
        payload = resp.json()
        data = payload.get("data")
        if not data:
            raise RuntimeError("error request")
        return data
    
    def parse_replay_data(self, role_id=None, battleId=None):
        info = self.account_manager.login_info
        form = self.device_manager.get_common_info()
        form.update(
            {
                "openId": info["appOpenid"],
                "gameOpenId": self.account_manager.game_open_id,
                "gameId": self.account_manager.game_id,
                "roleId": role_id or self._default_role_id(),
                "userId": info["userId"],
                "token": info["token"],
                "battleId": battleId
            }
        )
        resp = self._post("play/parsereplaydata", data=form)
        payload = resp.json()
        data = payload.get("data")
        if not data:
            raise RuntimeError("error request")
        return data
    
    def get_pubg_replay_data(self, battleId=None):
        info = self.account_manager.login_info
        form = self.device_manager.get_common_info()
        form.update(
            {
                "bopenid": self.account_manager.game_open_id,
                "battleId": battleId,
                "env": "",
                "serverIndex": "5",
                "openId": info["appOpenid"],
                "gameId": self.account_manager.game_id
            }
        )
        resp = self._post(full_url="https://c.gp.qq.com/h5/getpubgreplaydata4.php", data=form)
        payload = resp.json()
        data = payload.get("data")
        if not data:
            raise RuntimeError("error request")
        return data

    def _default_role_id(self):
        roles = self.account_manager.role_list or []
        for role in roles:
            if role.get("isMainRole"):
                return role.get("roleId")
        return roles[0]["roleId"] if roles else ""


def get_gp_client():
    return GpRequestClient(get_account_manager())
