import os
from typing import Generator

import aioredis
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL")
REDIS_URL = os.getenv("REDIS_URL")

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


async def get_redis_connection():
    return aioredis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)


async def close_redis_connection(redis):
    await redis.close()


async def invalidate_redis_cache(pattern: str):
    redis = await get_redis_connection()
    try:
        keys = await redis.keys(pattern)
        if keys:
            await redis.delete(*keys)
    finally:
        await close_redis_connection(redis)


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
