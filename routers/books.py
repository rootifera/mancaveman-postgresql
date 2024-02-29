"""Books Module"""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import and_
from sqlalchemy import func
from starlette import status

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
                       exact_match: bool = Query(False, description="Search for books by an exact title match.")):
    validate_user(user)

    if exact_match:
        books = db.query(Books).filter(Books.title == title).all()
    else:
        books = db.query(Books).filter(Books.title.ilike(f"%{title}%")).all()

    if not books:
        raise HTTPException(status_code=404, detail="No books found with the given title.")

    return books


@router.get("/get_by_author/{author}", status_code=status.HTTP_200_OK)
async def get_by_author(user: user_dependency, db: db_dependency, author: str,
                        exact_match: bool = Query(False, description="Search for books by an exact author match.")):
    validate_user(user)

    if exact_match:
        books = db.query(Books).filter(Books.author.contains([author])).all()
    else:
        books = db.query(Books).all()  # I know it's a bad and lazy idea. Sorry
        books = [book for book in books if any(author.lower() in auth.lower() for auth in book.author)]

    if not books:
        raise HTTPException(status_code=404, detail="No books found for the given author.")

    return books


@router.get("/get_by_publisher/{publisher}", status_code=status.HTTP_200_OK)
async def get_by_publisher(user: user_dependency, db: db_dependency, publisher: str,
                           exact_match: bool = Query(False,
                                                     description="Search for books by an exact publisher match.")):
    validate_user(user)

    if exact_match:
        books = db.query(Books).filter(Books.publisher == publisher).all()
    else:
        books = db.query(Books).filter(Books.publisher.ilike(f"%{publisher}%")).all()

    if not books:
        raise HTTPException(status_code=404, detail="No books found with the given publisher.")

    return books


@router.get("/get_by_category/{category}", status_code=status.HTTP_200_OK)
async def get_by_category(user: user_dependency, db: db_dependency, category: str,
                          exact_match: bool = Query(False, description="Search for books by an exact category match.")):
    validate_user(user)

    books = db.query(Books).all()
    if exact_match:
        filtered_books = [book for book in books if category in book.category]
    else:
        filtered_books = [book for book in books if
                          any(cat.lower().find(category.lower()) != -1 for cat in book.category)]

    if not filtered_books:
        raise HTTPException(status_code=404, detail="No books found for the given category.")

    return filtered_books


@router.get("/get_by_print_type/{print_type}", status_code=status.HTTP_200_OK)
async def get_by_print_type(user: user_dependency, db: db_dependency, print_type: str,
                            exact_match: bool = Query(False,
                                                      description="Search for books by an exact print type match.")):
    validate_user(user)

    if exact_match:
        books = db.query(Books).filter(Books.print_type == print_type).all()
    else:
        books = db.query(Books).filter(Books.print_type.ilike(f"%{print_type}%")).all()

    if not books:
        raise HTTPException(status_code=404, detail="No books found with the given print type.")

    return books


@router.get("/get_by_print_type/{print_type}", status_code=status.HTTP_200_OK)
async def get_by_print_type(user: user_dependency, db: db_dependency, print_type: str,
                            exact_match: bool = Query(False,
                                                      description="Search for books by an exact print type match.")):
    validate_user(user)

    if exact_match:
        books = db.query(Books).filter(Books.print_type == print_type).all()
    else:
        books = db.query(Books).filter(Books.print_type.ilike(f"%{print_type}%")).all()

    if not books:
        raise HTTPException(status_code=404, detail="No books found with the specified print type.")

    return books


@router.get("/get_by_isbn/{isbn}", status_code=status.HTTP_200_OK)
async def get_by_isbn(db: db_dependency, user: user_dependency, isbn: str):
    validate_user(user)

    if len(isbn) not in [10, 13]:
        raise HTTPException(status_code=400, detail="Invalid ISBN format. ISBN must be either 10 or 13 digits long.")

    isbn_field = Books.isbn_10 if len(isbn) == 10 else Books.isbn_13
    result = db.query(Books).filter(isbn_field == isbn).first()

    if result:
        return result
    else:
        raise HTTPException(status_code=404, detail="Book not found with the provided ISBN.")


@router.get("/search/")
async def book_search(
        db: db_dependency,
        user: user_dependency,
        title: Optional[str] = None,
        author: Optional[str] = None,
        publisher: Optional[str] = None,
        category: Optional[str] = None,
        print_type: Optional[str] = None,
        maturity_rating: Optional[str] = None,
        limit: int = Query(100, description="Limit the number of results", le=1000)
):
    validate_user(user)

    if all(param is None for param in [title, author, publisher, category, print_type, maturity_rating]):
        return db.query(Books).order_by(Books.id.desc()).limit(10).all()

    filters = []
    if title:
        filters.append(func.lower(Books.title).ilike(f"%{func.lower(title)}%"))
    if author:
        filters.append(Books.author.any(func.lower(author)))
    if publisher:
        filters.append(func.lower(Books.publisher).ilike(f"%{func.lower(publisher)}%"))
    if category:
        filters.append(Books.category.any(func.lower(category)))
    if maturity_rating:
        filters.append(func.lower(Books.maturity_rating).ilike(f"%{func.lower(maturity_rating)}%"))
    if print_type:
        filters.append(func.lower(Books.print_type).ilike(f"%{func.lower(print_type)}%"))

    query = db.query(Books).filter(and_(*filters)).limit(limit)

    results = query.all()
    if not results:
        raise HTTPException(status_code=404, detail="No books found matching the search criteria.")

    return results


@router.get('/autofill')
async def autofill(user: user_dependency, db: db_dependency, isbn: str):
    validate_user(user)

    current_user = db.query(Users).filter(Users.id == user.get('id')).first()
    api_key = current_user.books_api_key

    if api_key == 'NOKEY':
        return await get_book_info(isbn)
    else:
        return await get_book_info(isbn, api_key)


@router.post("/add", status_code=status.HTTP_201_CREATED)
async def add_book(user: user_dependency, db: db_dependency, book_request: BookRequest):
    validate_admin(user)

    try:
        book_model = Books(**book_request.dict())
        db.add(book_model)
        db.commit()
        actionlog.add_log("New book", f"{book_request.title} added at {datetime.now().strftime('%H:%M:%S')}",
                          user.get('username'))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error adding book: {str(e)}")
    return {"message": "Book added successfully"}


@router.put("/update/{book_id}", status_code=status.HTTP_202_ACCEPTED)
async def update_book(user: user_dependency, db: db_dependency,
                      book_request: BookRequest, book_id: int):
    validate_admin(user)

    book_model = db.query(Books).filter(Books.id == book_id).first()

    if not book_model:
        raise HTTPException(status_code=404, detail="Book not found")

    for var, value in vars(book_request).items():
        setattr(book_model, var, value) if value else None

    try:
        db.commit()
        return {"message": f"Book with ID {book_id} updated successfully."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred while updating the book: {e}")


@router.delete("/delete/{book_id}", status_code=status.HTTP_202_ACCEPTED)
async def delete_book(user: user_dependency, db: db_dependency, book_id: int):
    validate_admin(user)

    deleted = db.query(Books).filter(Books.id == book_id).delete()
    if not deleted:
        db.rollback()
        raise HTTPException(status_code=404, detail="Book not found")

    db.commit()

    actionlog.add_log("Book deleted", f"Book with ID {book_id} deleted at {datetime.now().strftime('%H:%M:%S')}",
                      user.get('username'))

    return {"message": "Book deleted successfully."}
