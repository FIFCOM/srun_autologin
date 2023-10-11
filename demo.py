import os
from SrunLoginCore import *
import time

# sudo apt install net-tools
command = "ifconfig eth0 | grep 'inet addr:' | cut -d: -f2 | awk '{ print $1}'"
internal_ip = os.popen(command).read().strip()

srun = SrunLoginCore(
    url_portal = "http://10.0.0.55/srun_portal_pc",
    url_login_api = "http://10.0.0.55/cgi-bin/srun_portal",
    url_get_challenge_api = "http://10.0.0.55/cgi-bin/get_challenge",
    url_rad_user_info = "http://10.0.0.55/cgi-bin/rad_user_info",
    acid = "1",
    internal_ip = internal_ip,
    debug = True
)

is_login = srun.is_login()
if is_login:
    print("Already Logged in!")

max_retry = 20
while not is_login and max_retry > 0:
    is_login = srun.login(
        username="123456789",
        password="123456"
    )
    if is_login:
        print("Login Success!")
    else:
        print("Login Failed! Retrying in 5 seconds...")
        max_retry -= 1
        time.sleep(5)