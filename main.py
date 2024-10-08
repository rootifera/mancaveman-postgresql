import json
import os
from contextlib import asynccontextmanager
from datetime import datetime
from typing import AsyncGenerator
from typing import Dict

from dotenv import load_dotenv
from fastapi import FastAPI, Depends
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from starlette.responses import FileResponse

from database import get_redis_connection, close_redis_connection
from routers import auth, hardware, software, logging, health, users, admin, books, files, tags, location
from tools.actionlog import add_log

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
# models.Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(users.router)
app.include_router(health.router)
app.include_router(logging.router)
app.include_router(files.router)
app.include_router(tags.router)
app.include_router(location.router)
app.include_router(hardware.router)
app.include_router(software.router)
app.include_router(books.router)

FAVICON_PATH = 'uploads/images/favicon.ico'

add_log("Server Start",
        "Server started at {}".format(datetime.now().strftime("%H:%M:%S")), "System")


@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    return FileResponse(FAVICON_PATH)


def load_version_info() -> Dict:
    with open("version.json", "r") as file:
        version_info = json.load(file)
    return version_info["mancave"][0]


@app.get('/', dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def root():
    ver_info = load_version_info()
    return {
        'appName': ver_info["appName"],
        'version': ver_info["version"],
        'database': ver_info["database"],
        "buildDate": ver_info["buildDate"],
        "buildName": ver_info["buildName"],
        "buildID": ver_info["buildID"],
        "buildNumber": ver_info["buildNumber"]
    }
