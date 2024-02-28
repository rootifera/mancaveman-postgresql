import re
import secrets

import validators

from database import get_redis_connection, close_redis_connection


def is_hostname_valid(host_name: str) -> bool:
    return validators.domain(host_name)


def email_to_username(email_address: str):
    username = email_address.strip().lower().split('@')
    return username[0]


def is_app_passwd_valid(app_passwd: str) -> bool:
    """
    Validates a gmail app password.
    """
    app_pw_pattern = re.compile(r'[a-z]{4} [a-z]{4} [a-z]{4} [a-z]{4}')
    app_pw_stripped = app_passwd.strip().lower()
    return bool(app_pw_pattern.fullmatch(app_pw_stripped))


async def health_check_keygen():
    """
    Generates a new health check key and stores it in Redis.
    """
    hc_key = secrets.token_hex(16)
    redis = await get_redis_connection()
    try:
        await redis.set('HEALTH:KEY', hc_key)
    finally:
        await close_redis_connection(redis)


async def get_health_check_key():
    """
    Retrieves the health check key from Redis.
    """
    redis = await get_redis_connection()
    try:
        hc_key = await redis.get('HEALTH:KEY')
        return hc_key
    finally:
        await close_redis_connection(redis)


async def get_email_credentials():
    redis = await get_redis_connection()
    enabled = await redis.get('email:enabled')
    if enabled == 'False':
        return False
    else:
        username = await redis.get('email:username')
        password = await redis.get('email:password')
        return username, password


async def set_email_credentials(username, password, enabled=True):
    redis = await get_redis_connection()
    username = email_to_username(username)
    try:
        await redis.set('email:enabled', int(enabled))
        await redis.set('email:username', username)
        await redis.set('email:password', password)
    finally:
        await close_redis_connection(redis)


async def get_hostname():
    redis = await get_redis_connection()
    return await redis.get('server:hostname')


async def set_hostname(host_name):
    redis = await get_redis_connection()
    try:
        await redis.set('server:hostname', host_name)
    finally:
        await close_redis_connection(redis)
