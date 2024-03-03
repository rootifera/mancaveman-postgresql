from fastapi import APIRouter
from starlette.exceptions import HTTPException

from dependencies import db_dependency, user_dependency
from models import LocationRequest, Location, LocationType, LocationUpdateRequest, LocationTypeRequest
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
async def add_location(location: LocationRequest, db: db_dependency, user: user_dependency):
    validate_admin(user)
    location_type = db.query(LocationType).filter(LocationType.id == location.type_id).first()
    if not location_type:
        raise HTTPException(status_code=400, detail="Location type does not exist")

    if location.parent_id:
        parent_location = db.query(Location).filter(Location.id == location.parent_id).first()
        if not parent_location:
            raise HTTPException(status_code=400, detail="Parent location does not exist")

    new_location = Location(name=location.name, type_id=location.type_id, parent_id=location.parent_id)
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

    if location_data.type_id:
        location_type = db.query(LocationType).filter(LocationType.id == location_data.type_id).first()
        if not location_type:
            raise HTTPException(status_code=400, detail="Location type does not exist")
        location.type_id = location_data.type_id

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


@router.get("/types/all")
async def get_all_location_types(db: db_dependency, user: user_dependency):
    validate_user(user)
    types = db.query(LocationType).all()
    return types


@router.get("/types/{type_id}")
async def get_location_type_by_id(type_id: int, db: db_dependency, user: user_dependency):
    validate_user(user)
    location_type = db.query(LocationType).filter(LocationType.id == type_id).first()
    if not location_type:
        raise HTTPException(status_code=404, detail="Location type not found")
    return location_type


@router.post("/types/add")
async def add_location_type(location_type: LocationTypeRequest, db: db_dependency, user: user_dependency):
    validate_admin(user)
    existing_type = db.query(LocationType).filter(LocationType.name == location_type.name).first()
    if existing_type:
        raise HTTPException(status_code=400, detail="Location type already exists")

    new_type = LocationType(name=location_type.name)
    db.add(new_type)
    db.commit()
    db.refresh(new_type)
    return new_type


@router.put("/types/update/{type_id}")
async def update_location_type(type_id: int, location_type_data: LocationTypeRequest, db: db_dependency,
                               user: user_dependency):
    validate_admin(user)
    location_type = db.query(LocationType).filter(LocationType.id == type_id).first()
    if not location_type:
        raise HTTPException(status_code=404, detail="Location type not found")

    location_type.name = location_type_data.name
    db.commit()
    return location_type


@router.delete("/types/delete/{type_id}")
async def delete_location_type(type_id: int, db: db_dependency, user: user_dependency):
    validate_admin(user)
    location_type = db.query(LocationType).filter(LocationType.id == type_id).first()
    if not location_type:
        raise HTTPException(status_code=404, detail="Location type not found")

    db.delete(location_type)
    db.commit()
    return {"message": f"Location type with ID {type_id} has been successfully deleted."}
