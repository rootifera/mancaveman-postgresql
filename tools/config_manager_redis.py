import secrets

from database import get_redis_connection, close_redis_connection


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
    try:
        await redis.set('email:enabled', enabled)
        await redis.set('email:username', username)
        await redis.set('email:password', password)
    finally:
        await close_redis_connection(redis)


async def get_hostname():
    redis = await get_redis_connection()
    return await redis.get('server:hostname')


async def set_hostname(host_name):
    redis = await get_redis_connection()
    await redis.set('server:hostname', host_name)
