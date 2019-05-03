import random
import string
import hashlib
import base64
from datetime import datetime, timedelta

import jwt

from configs import SECRET


def generate_salt(size=16):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=size))


def hash_pass(raw_password, salt=generate_salt()):
    m = hashlib.sha256()
    m.update(raw_password.encode('utf-8'))
    m.update(salt.encode('utf-8'))
    return m.hexdigest(), salt


def check_passwords(income_password, salt, db_password):
    hash_password = hash_pass(income_password, salt)[0]
    return hash_password == db_password


def create_tokens(user_id, expiration_time=25):
    payload = {'user_id': user_id, 'salt': generate_salt()}
    token = jwt.encode(payload, SECRET).decode()
    refresh_payload = {'token': token}
    refresh_token = jwt.encode(refresh_payload, SECRET).decode()
    return token, refresh_token


def decode_token(token, with_leeway=True):
    if with_leeway:
        return jwt.decode(token, SECRET, leeway=0)
    return jwt.decode(token, SECRET)

