import uuid
import random
import string
import json
import time
import requests
from requests.adapters import HTTPAdapter
from urllib.parse import urlparse


def random_string(length):
    charset = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    return ''.join(random.choice(charset) for _ in range(length))


def dict_to_json(obj):
    return json.dumps(obj, default=str)


def create_timestamp():
    return str(round(time.time() * 1000) / 1000)


class Instagram:
    def __init__(self, proxy=None):
        self.proxy = proxy
        self.values = {}
        self.results = {}

    def _send_request(self, url, method, headers, body=None, debug=False):
        try:
            if self.proxy:
                parsed_url = urlparse(f'http://{self.proxy}')
                proxy_dict = {
                    'http': f'http://{self.proxy}',
                    'https': f'http://{self.proxy}'
                }
                session = requests.Session()
                session.proxies.update(proxy_dict)
            else:
                session = requests.Session()

            headers.update({
                'x-ig-app-locale': 'en_US',
                'x-ig-device-locale': 'en_US',
                'x-ig-mapped-locale': 'en_US',
                'x-pigeon-session-id': f'UFS-{str(uuid.uuid4())}-0',
                'x-pigeon-rawclienttime': create_timestamp(),
                'x-ig-bandwidth-speed-kbps': '-1.000',
                'x-ig-bandwidth-totalbytes-b': '0',
                'x-ig-bandwidth-totaltime-ms': '0',
                'x-bloks-version-id': 'a346110fb4a15c99b37b5a1bb467d8c3743d9cc71071e1a27c283c83af805962',
                'x-ig-www-claim': '0',
                'x-bloks-is-prism-enabled': 'false',
                'x-bloks-prism-button-version': 'CONTROL',
                'x-bloks-prism-colors-enabled': 'false',
                'x-bloks-prism-font-enabled': 'false',
                'x-ig-attest-params': '{"attestation":[{"version":2,"type":"keystore","errors":[-1013],"challenge_nonce":"","signed_nonce":"","key_hash":""}]}',
                'x-bloks-is-layout-rtl': 'false',
                'x-ig-device-id': str(uuid.uuid4()),
                'x-ig-family-device-id': str(uuid.uuid4()),
                'x-ig-timezone-offset': '0',
                'x-fb-connection-type': 'WIFI',
                'x-ig-connection-type': 'WIFI',
                'x-ig-capabilities': '3brTv10=',
                'x-ig-app-id': '567067343352427',
                'user-agent': 'Instagram 341.0.0.0.75 Android (33/13; 560dpi; 1440x2560; Genymobile/Samsung; Galaxy S7; motion_phone_arm64; vbox86; en_US; 623186617)',
                'accept-language': 'en-US',
                'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'accept-encoding': 'utf-8',
                'host': 'i.instagram.com',
                'x-fb-http-engine': 'Liger',
                'x-fb-client-ip': 'True',
                'x-fb-server-cluster': 'True',
                'connection': 'keep-alive',
            })

            if 'token' in self.values:
                headers['authorization'] = self.values['token']
            if 'claim' in self.values:
                headers['x-ig-www-claim'] = self.values['claim']

            if debug:
                print(headers)

            response = session.request(method, url, headers=headers, data=body)

            if 'x-ig-set-www-claim' in response.headers:
                self.values['claim'] = response.headers['x-ig-set-www-claim']
            if 'ig-set-ig-u-rur' in response.headers:
                self.values['rur'] = response.headers['ig-set-ig-u-rur']

            return response.json()
        except Exception as error:
            print("Error in _send_request:", error)
            return {'error': str(error)}

    def login(self, username, password):
        try:
            android_id = f"android-{uuid.uuid4().hex[:8]}"
            params = dict_to_json({
                "client_input_params": {
                    "password": f"#PWD_INSTAGRAM_BROWSER:0:&:{password}",
                    "contact_point": username,
                    "device_id": android_id,
                    "login_attempt_count": 1,
                    "has_whatsapp_installed": 0,
                    "family_device_id": str(uuid.uuid4()),
                    "device_emails": [],
                },
                "server_params": {
                    "login_source": "Login",
                    "password_text_input_id": f"{random_string(6)}:185",
                    "username_text_input_id": f"{random_string(6)}:184",
                    "device_id": None,
                }
            })

            url = "https://i.instagram.com/api/v1/bloks/apps/com.bloks.www.bloks.caa.login.async.send_login_request/"
            response = self._send_request(url, 'POST', {
                'x-ig-android-id': android_id,
                'x-ig-nav-chain': f"com.bloks.www.caa.login.login_homepage:com.bloks.www.caa.login.login_homepage:1:button:{create_timestamp()}::",
            }, body=params)

            if 'token' in response.get('body', ''):
                token_pattern = r'Bearer\sIGT:[^\s]+'
                tokens = re.findall(token_pattern, response['body'])

                if tokens:
                    self.values['token'] = tokens[0]
                    return {"complete": True, "values": self.values}
                else:
                    return {"complete": False, "error": "No tokens found."}

            return {"complete": False, "error": response.get('error')}
        except Exception as e:
            return {"complete": False, "error": str(e)}

# Example of how to use it
if __name__ == "__main__":
    ig = Instagram(proxy="proxy.example.com:8080")
    result = ig.login("your_username", "your_password")
    print(result)
