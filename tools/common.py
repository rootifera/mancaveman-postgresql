# shared functions
import json
import os
import random
import secrets
import string
from datetime import datetime

from starlette.exceptions import HTTPException

from definitions import ROOT_DIR


def validate_user(user):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    return True


def validate_admin(user):
    if not user.get('is_admin'):
        raise HTTPException(status_code=401, detail='Insufficient Permissions (admin)')
    return True


def randomize_filename(file_to_rename: str, filename_length: int = 16):
    file_extension = file_to_rename.split(".")[-1]
    random_name = ''.join(random.choice(string.ascii_lowercase) for _ in range(filename_length))
    return f"{random_name}.{file_extension}"


def version_generator(version: str, buildname: str, buildnumber: str, version_file):
    with open(version_file, 'r') as f:
        ver = json.load(f)

    ver['mancave'][0]['version'] = version
    ver['mancave'][0]['buildName'] = buildname
    ver['mancave'][0]['buildDate'] = datetime.today().strftime('%Y-%m-%d')
    ver['mancave'][0]['buildID'] = secrets.token_hex(12)
    ver['mancave'][0]['buildNumber'] = buildnumber

    with open(version_file, 'w') as f:
        json.dump(ver, f, indent=2)

