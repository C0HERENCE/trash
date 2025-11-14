import base64
import time
from pathlib import Path
from pyqrcode import QRCode
import sys

from game_for_peace.account import get_account_manager
from game_for_peace.gp_client import GpRequestClient

try:
    b = u'\u2588\u2588'
    sys.stdout.write(b + '\r')
    sys.stdout.flush()
except UnicodeEncodeError:
    BLOCK = 'MM'
else:
    BLOCK = b

def print_cmd_qr(qrText, white=BLOCK, black='  ', enableCmdQR=True):
    blockCount = int(enableCmdQR)
    if abs(blockCount) == 0:
        blockCount = 1
    white *= abs(blockCount)
    if blockCount < 0:
        white, black = black, white
    sys.stdout.write(' '*50 + '\r')
    sys.stdout.flush()
    qr = qrText.replace('0', white).replace('1', black)
    sys.stdout.write(qr)
    sys.stdout.flush()


def save_qr_image(qr_data, path):
    code = qr_data["qrcode"]["qrcodebase64"]
    raw = base64.b64decode(code)
    Path(path).write_bytes(raw)
    return Path(path)


def wait_for_open_id(client, uuid, timeout=120):
    last_status = None
    end_time = time.time() + timeout
    while time.time() < end_time:
        scan = client.request_qr_code_scan_status(uuid, last_status)
        if scan:
            last_status = scan.get("wx_errcode", last_status)
            code = scan.get("wx_code")
            if code:
                return code
        time.sleep(1)
    raise RuntimeError("qr scan timed out")


def login_flow(client, account):
    print("requesting wx sdk ticket...")
    ticket = client.request_wx_sdk_ticket()
    print("requesting qr code...")
    qr_result = client.request_wx_login_qr_code(ticket)
    
    qr_content = f"https://open.weixin.qq.com/connect/confirm?uuid={qr_result['uuid']}"
    qrCode = QRCode(qr_content)
    print_cmd_qr(qrCode.text(1))
    open_id = wait_for_open_id(client, qr_result["uuid"])
    print("wechat scan confirmed. requesting auth...")
    client.get_personal_auth(open_id)
    info = client.login(open_id)
    account.save_login_info(info)
    print("login success. info cached.")


def g4p_login():
    account = get_account_manager()
    client = GpRequestClient(account)
    if not account.is_valid_login():
        login_flow(client, account)
    roles = client.get_all_roles()
    account.role_list = roles
    return client
