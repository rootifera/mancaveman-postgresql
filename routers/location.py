from fastapi import APIRouter
from starlette.exceptions import HTTPException

from dependencies import db_dependency, user_dependency
from models import LocationRequest, Location, LocationUpdateRequest
from tools.common import validate_admin, validate_user

router = APIRouter(
    prefix='/location',
    tags=['location']
)


@router.get("/all")
async def get_all_locations(db: db_dependency, user: user_dependency):
    validate_user(user)
    locations = db.query(Location).all()
    return locations


@router.get("/{location_id}")
async def get_location_by_id(location_id: int, db: db_dependency, user: user_dependency):
    validate_user(user)
    location = db.query(Location).filter(Location.id == location_id).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    return location


@router.post("/add")
async def add_location(location_request: LocationRequest, db: db_dependency, user: user_dependency):
    validate_admin(user)

    if location_request.parent_id:
        parent_location = db.query(Location).filter(Location.id == location_request.parent_id).first()
        if not parent_location:
            raise HTTPException(status_code=400, detail="Parent location does not exist")
    else:
        location_request.parent_id = None

    new_location = Location(name=location_request.name, parent_id=location_request.parent_id)
    db.add(new_location)
    db.commit()
    db.refresh(new_location)
    return new_location


@router.put("/update/{location_id}")
async def update_location(location_id: int, location_data: LocationUpdateRequest, db: db_dependency,
                          user: user_dependency):
    validate_admin(user)
    location = db.query(Location).filter(Location.id == location_id).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")

    if location_data.parent_id is not None:
        if location_data.parent_id:
            parent_location = db.query(Location).filter(Location.id == location_data.parent_id).first()
            if not parent_location:
                raise HTTPException(status_code=400, detail="Parent location does not exist")
        location.parent_id = location_data.parent_id

    if location_data.name:
        location.name = location_data.name

    db.commit()
    return location


@router.delete("/delete/{location_id}")
async def delete_location(location_id: int, db: db_dependency, user: user_dependency):
    validate_admin(user)
    location = db.query(Location).filter(Location.id == location_id).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")

    db.delete(location)
    db.commit()
    return {"message": f"Location with ID {location_id} has been successfully deleted."}
