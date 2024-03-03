import json
import os
from contextlib import asynccontextmanager
from datetime import datetime
from typing import AsyncGenerator

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Depends
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from starlette.responses import FileResponse

import models
from database import engine, get_redis_connection, close_redis_connection
from routers import auth, hardware, software, logging, health, users, admin, books, files, tags, location
from tools import actionlog
from tools.config_manager import load_config

config = load_config()
load_dotenv()
REDIS = os.getenv("REDIS_URL")


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncGenerator[None, None]:
    application.state.redis = await get_redis_connection()
    await FastAPILimiter.init(application.state.redis)
    try:
        yield
    finally:
        await application.state.redis.flushall()
        await close_redis_connection(application.state.redis)


app = FastAPI(lifespan=lifespan)
# prod: app = FastAPI(docs_url=None, redoc_url=None)
models.Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(admin.router)
app.include_router(files.router)
app.include_router(tags.router)
app.include_router(hardware.router)
app.include_router(software.router)
app.include_router(books.router)
app.include_router(health.router)
app.include_router(location.router)
app.include_router(logging.router)

FAVICON_PATH = 'uploads/images/favicon.ico'


@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    return FileResponse(FAVICON_PATH)


@app.get('/', dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def root():
    with open("version.json", "r") as f:
        ver_info = json.load(f)
    return {
        'appName': ver_info["mancave"][0]["appName"],
        'version': ver_info["mancave"][0]["version"],
        'database': ver_info["mancave"][0]["database"],
        "buildDate": ver_info["mancave"][0]["buildDate"],
        "buildName": ver_info["mancave"][0]["buildName"],
        "buildID": ver_info["mancave"][0]["buildID"],
        "buildNumber": ver_info["mancave"][0]["buildNumber"]
    }


if __name__ == "__main__":
    from tools import config_manager
    from tools import dotenv_loader

    dotenv_loader.load_env()

    if config_manager.is_initdb():
        config_manager.docker_config(True)

    PORT = int(os.getenv('PORT'))

    actionlog.add_log("Server Start",
                      "Server started at {}".format(datetime.now().strftime("%H:%M:%S")), "System")
    uvicorn.run("main:app", host='0.0.0.0', port=PORT, proxy_headers=True, forwarded_allow_ips='*')
    actionlog.add_log("Server Stop",
                      "Server started at {}".format(datetime.now().strftime("%H:%M:%S")), "System")
