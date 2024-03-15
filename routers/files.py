"""Files Module"""

import os

from fastapi import APIRouter
from fastapi import File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

from dependencies import user_dependency
from tools.common import randomize_filename
from tools.common import validate_user, validate_admin

router = APIRouter(
    prefix='/files',
    tags=['files']
)


@router.post("/upload")
async def upload_file(user: user_dependency, file_to_upload: UploadFile = File(...), file_type: str = Form(...)):
    validate_user(user)
    validate_admin(user)

    if file_type not in ["doc", "img"]:
        raise HTTPException(status_code=400, detail="Invalid file type. Use 'doc' or 'img'.")

    file_extension = file_to_upload.filename.split(".")[-1]
    new_filename = randomize_filename(file_extension)

    if file_type == "doc":
        upload_path = os.path.join("uploads", "documents", new_filename)
    else:
        upload_path = os.path.join("uploads", "images", new_filename)

    with open(upload_path, "wb") as file_object:
        file_object.write(file_to_upload.file.read())

    return JSONResponse(content={"file": upload_path})
