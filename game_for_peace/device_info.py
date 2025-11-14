class DeviceInfoManager:
    def __init__(self):
        self.device_info = {
            "cGzip": "1",
            "cDevicePPI": "280",
            "cGameId": "20004",
            "cDeviceImei": "2025032415220882152:54:00:a6:85:dc954819",
            "cDeviceScreenHeight": "1920",
            "cDeviceCPU": "arm64-v8a$x86_64",
            "cDeviceSP": "",
            "cSystemVersionCode": "28",
            "cWifiMac": "",
            "cWifiSsid": "",
            "cDeviceNet": "WIFI",
            "cClientVersionCode": "2102091464",
            "cDeviceKey": "9ce672d08ee76dc1",
            "cChannelId": "1",
            "cDeviceMem": "25132",
            "cDeviceRom": "emulator",
            "cDeviceMac": "",
            "cCurrentGameId": "20004",
            "cRand": "1762331459784",
            "cDeviceScreenWidth": "1080",
            "cDeviceModel": "MI 9",
            "cClientVersionName": "3.32.2.1453",
            "cSystem": "android",
            "cDeviceId": "2025032415220882152:54:00:a6:85:dc954819",
            "cSystemVersionName": "9",
            "cDeviceImsi": "2025032415220882152:54:00:a6:85:dc954819",
        }

    def get_common_info(self):
        return dict(self.device_info)
