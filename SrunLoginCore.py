import requests
import re
from srunutils.SrunBase64 import *
from srunutils.SrunMD5 import *
from srunutils.SrunSHA1 import *
from srunutils.SrunXEncode import *
import time

class SrunLoginCore:
    def __init__(self,
        url_portal = "http://10.0.0.55/srun_portal_pc",
        url_login_api = "http://10.0.0.55/cgi-bin/srun_portal",
        url_get_challenge_api = "http://10.0.0.55/cgi-bin/get_challenge",
        url_rad_user_info = "http://10.0.0.55/cgi-bin/rad_user_info",
        internal_ip = "0.0.0.0",
        n = "200",
        vtype = "1",
        acid = "1",
        enc = "srun_bx1",
        debug = False
    ):
        self.UA = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'}
        self.url_portal = url_portal
        self.url_login_api = url_login_api
        self.url_get_challenge_api = url_get_challenge_api
        self.url_rad_user_info = url_rad_user_info
        self.debug = debug
        self.ip = None
        if internal_ip != "0.0.0.0":
            self.ip = internal_ip
        else:
            self.ip = self.get_ip()
        
        self.n = n
        self.vtype = vtype
        self.acid = acid
        self.enc = enc
    
    def login(self, username, password):
        """
        Login to the Srun auth system with the given username and password.

        Args:
        - username (str): The username for the Srun auth system.
        - password (str): The plain password.

        Returns:
        - bool: True if the login is successful, False otherwise.
        """
        if self.is_login():
            return True
        
        self.user = username
        self.plain_pwd = password
        
        self.token = self.get_challenge_token(username)
        self.enc_pwd, self.hmd5 = self.get_encrypted_password(password)
        self.info = self.get_info(username, password)
        self.chksum = self.get_checksum()

        login_params = {
            "callback": "jQuery",
            "action": "login",
            "username": self.user,
            "password": self.enc_pwd,
            "os": "Windows+10",
            "name": "Windows",
            "double_stack": "0",
            "chksum": self.chksum,
            "info": self.info,
            "ac_id": self.acid,
            "ip": self.ip,
            "n": "200",
            "type": "1",
            "_": int(time.time()*1000)
        }
        try:
            resp = requests.get(self.url_login_api, params=login_params, headers=self.UA).text
        except:
            self.dbg("[WARN] login network error, call url_login_api failed")
            return False
        self.dbg("[DEBUG] login: " + resp)
        return '"suc_msg":"login_ok"' in resp

    def get_ip(self):
        """
        Call url_rad_user_info("http://x.x.x.x/cgi-bin/rad_user_info") to get the ip of the user.
        Notice: May get the public IP of the user if user is not in or already connected to the campus network.

        Returns:
        - str: The internal ip of the user.
        """
        params = {
            "callback": "jQuery",
            "ip": self.ip,
            "_": int(time.time() * 1000)
        }
        try:
            resp = requests.get(self.url_rad_user_info, params=params).text
        except:
            self.dbg("[WARN] get_ip network error, call url_rad_user_info failed")
            return self.ip
        self.dbg("[DEBUG] get_ip: " + resp)
        return re.search('"online_ip":"(.*?)"', resp).group(1)

    def is_login(self) -> bool:
        """
        Get ip status from url_rad_user_info("http://x.x.x.x/cgi-bin/rad_user_info").

        Returns:
        - bool: True if the user is online, False otherwise.
        """
        params = {
            "callback": "jQuery",
            "ip": self.ip,
            "_": int(time.time() * 1000)
        }
        try:
            resp = requests.get(self.url_rad_user_info, params=params).text
        except:
            self.dbg("[WARN] is_login network error, call url_rad_user_info failed")
            return False
        self.dbg("[DEBUG] is_login: " + resp)
        return '"error":"ok"' in resp

    def get_challenge_token(self, username) -> str:
        """
        Get the challenge token for the given username and ip 
        from url_get_challenge_api("http://x.x.x.x/cgi-bin/get_challenge").

        Args:
        - username (str): The username to get the challenge token for.

        Returns:
        - str: The challenge token for the given username.
        """
        challenge_params = {
            "callback": "jQuery",
            "username": username,
            "ip": self.ip,
            "_": int(time.time() * 1000)
        }
        try:
            resp = requests.get(self.url_get_challenge_api, params=challenge_params, headers=self.UA).text
        except:
            self.dbg("[WARN] get_challenge_token network error, call url_get_challenge_api failed")
            return ""
        self.dbg("[DEBUG] get_challenge_token resp: " + resp)
        token = re.search('"challenge":"(.*?)"', resp).group(1)
        self.dbg("[DEBUG] get_challenge_token token: " + token)
        return token
    
    def get_encrypted_password(self, plain_password) -> tuple:
        """
        Using HMAC-MD5 algorithm to encrypt the given plain password.

        Args:
        - plain_password (str): The plain password to encrypt.

        Returns:
        - tuple: A tuple containing the encrypted password and its MD5 hash.
        """
        hmd5 = get_md5(plain_password, self.token)
        enc_pwd = '{MD5}' + hmd5
        self.dbg("[DEBUG] get_encrypted_password: " + enc_pwd)
        return enc_pwd, hmd5

    def get_info(self, username, plain_password) -> str:
        """
        Returns the encoded login information for the given username, password, ip, acid, and enc_ver.

        Args:
        - username (str): The username to login with.
        - plain_password (str): The plain-text password to login with.

        Returns:
        - str: The encoded login information.
        """
        info_params = {
            "username": username,
            "password": plain_password,
            "ip": self.ip,
            "acid": self.acid,
            "enc_ver": self.enc
        }
        info = re.sub("'", '"', str(info_params))
        info = re.sub(" ", "", info)
        info = "{SRBX1}" + get_base64(get_xencode(info, self.token))
        self.dbg("[DEBUG] get_info: " + info)
        return info

    def get_checksum(self) -> str:
        """
        Calculates the checksum for the login request using the (token + user, token + hmd5, token + acid,
        token + ip, token + n, token + vtype, and token + info) attributes.

        Returns:
        - str: The calculated checksum.
        """
        s = "".join([self.token + getattr(self, x) for x in ["user", "hmd5", "acid", "ip", "n", "vtype", "info"]])
        chksum = get_sha1(s)
        self.dbg("[DEBUG] get_checksum: " + chksum)
        return chksum

    def dbg(self, msg):
        if self.debug:
            print(msg)