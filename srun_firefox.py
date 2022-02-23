# @author FIFCOM
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from prettytable import PrettyTable
from shutil import which
import socket
import json
import time

ua_list = {
    'pc': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 '
          'Safari/537.36',
    'mobile': 'Mozilla/5.0 (Linux; Android 11; Mi 10) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.87 '
              'Mobile Safari/537.36'
}


def file_exists(file_path):
    try:
        with open(file_path, 'r'):
            return True
    except FileNotFoundError:
        return False


def cmd_exists(file_path):
    return which(file_path) is not None


class SrunFireFox:
    # portal_url: srun login portal page url
    # ua_type: pc or mobile, to simulate device type
    # if debug is True, Edge Browser will be visible
    def __init__(self, debug=False):
        self.internal_ip = socket.gethostbyname(socket.gethostname())
        self.options = Options()
        self.profile = webdriver.FirefoxProfile()

        # if file exists "srun_cfg.json" then json decode it
        if file_exists('srun_cfg.json'):
            self.cfg = json.load(open('srun_cfg.json', 'r'))
        else:
            self.cfg = {}

        if self.cfg != {}:
            pass
        elif self.cfg == {}:
            raise Exception('srun_cfg.json is not found or empty')
        elif self.cfg['portal_url'] == '' or self.cfg['username'] == '' or self.cfg['password'] == '' \
                or self.cfg['gecko_path'] == '' or self.cfg['gecko_driver'] == '' or self.cfg['ua_type'] == '':
            raise Exception('Configuration is not complete, pls edit srun_cfg.json')
        elif not cmd_exists(self.cfg['gecko_path']) or not cmd_exists(self.cfg['gecko_driver']):
            raise Exception('Gecko driver or path is not found')

        self.ua = ua_list[self.cfg['ua_type']]
        self.options.headless = not debug
        self.profile.set_preference("general.useragent.override", self.ua)

        self.firefox = webdriver.Firefox(executable_path=self.cfg['gecko_driver'],
                                         options=self.options, firefox_profile=self.profile)

    def login(self):
        self.firefox.get(self.cfg['portal_url'] + '&wlanuserip=' + self.internal_ip)
        # get url
        time.sleep(1)
        url = self.firefox.current_url
        print(url)
        # not logged in
        if url.find('srun_portal') != -1 and url.find('success') == -1:
            self.firefox.find_element(By.ID, "username").send_keys(self.cfg['username'])
            self.firefox.find_element(By.ID, "password").send_keys(self.cfg['password'])
            self.firefox.find_element(By.ID, "login-account").click()
            # wait for login
            time.sleep(1)
            url = self.firefox.current_url
            # logged
            if url.find('srun_portal') != -1 and url.find('success') != -1 and self.is_login():
                return True
            else:
                return False
        else:
            return False

    def logout(self):
        self.firefox.get(self.cfg['portal_url'] + '&wlanuserip=' + self.internal_ip)
        time.sleep(1)
        url = self.firefox.current_url
        if url.find('srun_portal') != -1 and url.find('success') != -1:
            self.firefox.find_element(By.ID, "logout").click()
            self.firefox.find_element(By.CSS_SELECTOR, ".btn-confirm").click()
            time.sleep(1)
            url = self.firefox.current_url
            if url.find('srun_portal') != -1 and url.find('success') == -1:
                return True
            else:
                return False
        else:
            return False

    def info(self):
        # get user info in portal page span elements
        self.firefox.get(self.cfg['portal_url'] + '&wlanuserip=' + self.internal_ip)
        time.sleep(0.5)
        username = self.firefox.find_element(By.ID, "username").text
        used_flow = self.firefox.find_element(By.ID, "used-flow").text
        used_time = self.firefox.find_element(By.ID, "used-time").text
        balance = self.firefox.find_element(By.ID, "balance").text
        ip = self.firefox.find_element(By.ID, "ipv4").text
        ret = PrettyTable()
        ret.field_names = ["Srun AutoLogin", "@564568e"]
        ret.add_row(['Username', username])
        ret.add_row(['Used Flow', used_flow])
        ret.add_row(['Used Time', used_time])
        ret.add_row(['Balance', balance])
        ret.add_row(['IP', ip])
        return ret

    def is_login(self):
        # return True if logged in and network is connected
        self.firefox.get('http://qq.com')
        time.sleep(1)
        url = self.firefox.current_url
        if url.find('qq.com') != -1:
            return True
        else:
            return False

    def quit(self):
        self.firefox.quit()


if __name__ == '__main__':
    print("Srun AutoLogin - Firefox ver")
    print("Initializing...")
    srun = SrunFireFox(debug=True)
    if srun.is_login():
        print(srun.info())
        print('Already logged in, type Y to logout')
        i = input()
        if i.lower() == 'y':
            if srun.logout():
                print('logout success')
            else:
                print('!!! logout failed')
    else:
        print('Not logged in, type Y to login')
        i = input()
        if i.lower() == 'y':
            if srun.login():
                print('login success')
            else:
                print('!!! login failed')
    srun.quit()

