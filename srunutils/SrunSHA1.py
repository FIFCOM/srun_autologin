# https://github.com/coffeehat/BIT-srun-login-script
import hashlib

def get_sha1(value):
    return hashlib.sha1(value.encode()).hexdigest()