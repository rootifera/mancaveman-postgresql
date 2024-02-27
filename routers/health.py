from fastapi import APIRouter, Depends
from fastapi_limiter.depends import RateLimiter
from starlette import status
from starlette.exceptions import HTTPException

from database import get_redis_connection, close_redis_connection
from dependencies import db_dependency, user_dependency
from tools.common import validate_admin
from tools.config_manager_redis import get_health_check_key, health_check_keygen
from tools.health_benchmark import postgres_health_check, redis_health_check, check_cpu, check_memory, vacuum_db, \
    analyze_db, reindex_db

router = APIRouter(
    prefix='/health',
    tags=['health']
)


@router.get("/status", status_code=status.HTTP_200_OK,
            dependencies=[Depends(RateLimiter(times=3, seconds=60))])
async def health_check(db: db_dependency, key=None):
    health_key = await get_health_check_key()
    if key == health_key:
        pg_health = postgres_health_check(db)
        cpu = check_cpu()
        mem = check_memory()

        redis = await get_redis_connection()
        try:
            rd_health = await redis_health_check(redis)
            return {'health': [pg_health, rd_health, cpu, mem]}
        finally:
            if redis:
                await close_redis_connection(redis)
    elif key == '' or key is None:
        return {'ERROR': 'Missing key'}
    else:
        return {'ERROR': 'Invalid key. Please create a key from the keygen endpoint'}


@router.get('/keygen', status_code=status.HTTP_200_OK)
async def keygen(user: user_dependency):
    if validate_admin(user):
        await health_check_keygen()
        new_key = await get_health_check_key()
        return {'key': new_key,
                'detail': 'Please save your key. If you lose it, you can always generate a new one'}
    else:
        raise HTTPException(status_code=401, detail="Not authenticated or user is not in admin group")


@router.get("/vacuum", status_code=status.HTTP_200_OK, dependencies=[Depends(RateLimiter(times=1, seconds=60))])
async def vacuum_postgresql(db: db_dependency, user: user_dependency):
    validate_admin(user)
    return vacuum_db(db)


@router.get("/analyze", status_code=status.HTTP_200_OK, dependencies=[Depends(RateLimiter(times=1, seconds=60))])
async def analyze_postgresql(db: db_dependency, user: user_dependency):
    validate_admin(user)
    return analyze_db(db)


@router.get("/reindex", status_code=status.HTTP_200_OK, dependencies=[Depends(RateLimiter(times=1, seconds=60))])
async def reindex_postgresql(db: db_dependency, user: user_dependency):
    validate_admin(user)
    return reindex_db(db)
