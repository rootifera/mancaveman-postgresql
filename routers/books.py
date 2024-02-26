"""Books Module"""

from datetime import datetime

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import func
from starlette import status

from definitions import DESC_FUZZY
from dependencies import db_dependency, user_dependency
from models import Users, Books, BookRequest
from tools import actionlog
from tools.book_populator import get_book_info
from tools.common import validate_admin, validate_user

router = APIRouter(
    prefix='/books',
    tags=['books']
)


@router.get("/get_all", status_code=status.HTTP_200_OK)
async def get_all(db: db_dependency, user: user_dependency):
    validate_user(user)
    return db.query(Books).all()


@router.get("/get_by_id/{id}", status_code=status.HTTP_200_OK)
async def get_by_id(db: db_dependency, user: user_dependency, id: str):
    validate_user(user)
    return db.query(Books).filter(Books.id == id).first()


@router.get("/get_by_title/{title}", status_code=status.HTTP_200_OK)
async def get_by_title(user: user_dependency, db: db_dependency, title: str,
                       fuzzy: bool = Query(False, description=DESC_FUZZY)):
    validate_user(user)
    if fuzzy:
        return db.query(Books).filter(Books.title.ilike(f"%{title}%")).all()
    else:
        return db.query(Books).filter(Books.title == title).all()


@router.get("/get_by_author/{author}", status_code=status.HTTP_200_OK)
async def get_by_author(user: user_dependency, db: db_dependency, author: str,
                        fuzzy: bool = Query(False, description=DESC_FUZZY)):
    validate_user(user)
    if fuzzy:
        return db.query(Books).filter(Books.author.ilike(f"%{author}%")).all()
    else:
        return db.query(Books).filter(Books.author == author).all()


@router.get("/get_by_publisher/{publisher}", status_code=status.HTTP_200_OK)
async def get_by_publisher(user: user_dependency, db: db_dependency, publisher: str,
                           fuzzy: bool = Query(False, description=DESC_FUZZY)):
    validate_user(user)
    if fuzzy:
        return db.query(Books).filter(Books.publisher.ilike(f"%{publisher}%")).all()
    else:
        return db.query(Books).filter(Books.publisher == publisher).all()


@router.get("/get_by_category/{category}", status_code=status.HTTP_200_OK)
async def get_by_category(user: user_dependency, db: db_dependency, category: str,
                          fuzzy: bool = Query(False, description=DESC_FUZZY)):
    validate_user(user)
    if fuzzy:
        return db.query(Books).filter(Books.category.ilike(f"%{category}%")).all()
    else:
        return db.query(Books).filter(Books.category == category).all()


@router.get("/get_by_print_type/{print_type}", status_code=status.HTTP_200_OK)
async def get_by_publisher(user: user_dependency, db: db_dependency, print_type: str,
                           fuzzy: bool = Query(False, description=DESC_FUZZY)):
    validate_user(user)
    if fuzzy:
        return db.query(Books).filter(Books.print_type.ilike(f"%{print_type}%")).all()
    else:
        return db.query(Books).filter(Books.print_type == print_type).all()


@router.get("/get_by_print_type/{print_type}", status_code=status.HTTP_200_OK)
async def get_by_print_type(user: user_dependency, db: db_dependency, print_type: str,
                            fuzzy: bool = Query(False, description=DESC_FUZZY)):
    validate_user(user)
    if fuzzy:
        return db.query(Books).filter(Books.print_type.ilike(f"%{print_type}%")).all()
    else:
        return db.query(Books).filter(Books.print_type == print_type).all()


@router.get("/get_by_isbn/{isbn}", status_code=status.HTTP_200_OK)
async def get_by_isbn(db: db_dependency, user: user_dependency, isbn: str):
    validate_user(user)

    if len(isbn) != 10 and len(isbn) != 13:
        raise HTTPException(status_code=400, detail="Invalid ISBN format")

    if len(isbn) == 10:
        result = db.query(Books).filter(Books.isbn_10 == isbn).first()
        if result is not None:
            return result
        else:
            raise HTTPException(status_code=404, detail="Book not found")
    if len(isbn) == 13:
        result = db.query(Books).filter(Books.isbn_13 == isbn).first()
        if result is not None:
            return result
        else:
            raise HTTPException(status_code=404, detail="Book not found")


@router.get("/search/")
async def book_search(
        db: db_dependency,
        user: user_dependency,
        title: str = None,
        author: str = None,
        publisher: str = None,
        category: str = None,
        print_type: str = None,
        maturity_rating: str = None,
        limit: int = Query(100, description="Limit the number of results", le=1000)
):
    validate_user(user)
    # if no search parameters given, it will return 10 most recent hardware
    if all(hw is None for hw in [title, author, publisher, category, print_type, maturity_rating]):
        return db.query(Books).order_by(Books.id.desc()).limit(10).all()

    filters = []
    if title:
        filters.append(func.lower(Books.title).ilike(f"%{title.lower()}%"))
    if author:
        filters.append(func.lower(Books.author).ilike(f"%{author.lower()}%"))
    if publisher:
        filters.append(func.lower(Books.publisher).ilike(f"%{publisher.lower()}%"))
    if category:
        filters.append(func.lower(Books.category).ilike(f"%{category.lower()}%"))
    if maturity_rating:
        filters.append(func.lower(Books.maturity_rating).ilike(f"%{maturity_rating.lower()}%"))
    if print_type:
        filters.append(func.lower(Books.print_type).ilike(f"%{print_type.lower()}%"))

    return db.query(Books).filter(*filters).limit(limit).all()


@router.get('/autofill')
async def autofill(user: user_dependency, db: db_dependency, isbn: str):
    validate_user(user)

    current_user = db.query(Users).filter(Users.id == user.get('id')).first()
    api_key = current_user.books_api_key

    if api_key == 'NOKEY':
        return get_book_info(isbn)
    else:
        return get_book_info(isbn, api_key)


@router.post("/add", status_code=status.HTTP_201_CREATED)
async def add_book(user: user_dependency, db: db_dependency, book_request: BookRequest):
    validate_user(user)
    validate_admin(user)

    log_data = book_request.model_dump()
    book_model = Books(**book_request.model_dump())
    db.add(book_model)
    db.commit()
    actionlog.add_log("New book", "{} added at {}".format(log_data['title'],
                                                          datetime.now().strftime("%H:%M:%S")),
                      user.get('username'))
    return None


@router.put("/update/{book_id}", status_code=status.HTTP_202_ACCEPTED)
async def update_software(user: user_dependency, db: db_dependency, book_request: BookRequest,
                          book_id: int):
    validate_user(user)
    validate_admin(user)

    book_model = db.query(Books).filter(Books.id == book_id).first()

    if book_model is None:
        raise HTTPException(status_code=404, detail="Not found")

    book_model.title = book_request.title
    book_model.subtitle = book_request.subtitle
    book_model.author = book_request.author
    book_model.publisher = book_request.publisher
    book_model.published_date = book_request.published_date
    book_model.description = book_request.description
    book_model.category = book_request.category
    book_model.print_type = book_request.print_type
    book_model.maturity_rating = book_request.maturity_rating
    book_model.condition = book_request.condition
    book_model.location = book_request.location
    book_model.isbn_10 = book_request.isbn_10
    book_model.isbn_13 = book_request.isbn_13

    db.add(book_model)
    db.commit()


@router.delete("/delete/{book_id}", status_code=status.HTTP_202_ACCEPTED)
async def delete_software(user: user_dependency, db: db_dependency, book_id: int):
    validate_user(user)
    validate_admin(user)

    book_model = db.query(Books).filter(Books.id == book_id).first()

    if book_model is None:
        raise HTTPException(status_code=404, detail='Not Found')
    db.query(Books).filter(Books.id == book_id).delete()
    db.commit()

    actionlog.add_log("Book deleted",
                      "{} deleted at {}".format(book_model.name,
                                                datetime.now().strftime("%H:%M:%S")), user.get('username'))

    return status.HTTP_200_OK
