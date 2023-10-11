# https://github.com/coffeehat/BIT-srun-login-script
import hmac
import hashlib

def get_md5(password,token):
	return hmac.new(token.encode(), password.encode(), hashlib.md5).hexdigest()