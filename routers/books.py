"""Books Module"""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from starlette import status

from dependencies import db_dependency, user_dependency
from models import Users, Books, BookRequest, BookAuthor, BookAuthorAssociation
from tools import actionlog
from tools.book_populator import get_book_info
from tools.common import validate_admin, validate_user

router = APIRouter(
    prefix='/books',
    tags=['books']
)


def format_book_response(book, db_session):
    author_names = db_session.query(BookAuthor.name).join(
        BookAuthorAssociation, BookAuthorAssociation.book_author_id == BookAuthor.id
    ).filter(BookAuthorAssociation.book_id == book.id).all()
    authors_list = [author[0] for author in author_names]

    categories_list = book.category if book.category else []

    book_data = {
        "id": book.id,
        "isbn_10": book.isbn_10,
        "isbn_13": book.isbn_13,
        "title": book.title,
        "subtitle": book.subtitle,
        "authors": authors_list,
        "publisher": book.publisher,
        "published_date": book.published_date,
        "description": book.description,
        "category": categories_list,
        "print_type": book.print_type,
        "maturity_rating": book.maturity_rating,
        "condition": book.condition,
        "location": book.location
    }

    return book_data


@router.get("/get_all", status_code=status.HTTP_200_OK)
async def get_all(db: db_dependency, user: user_dependency):
    validate_user(user)
    books = db.query(Books).all()
    formatted_books = [format_book_response(book, db) for book in books]
    return formatted_books


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
async def get_by_author(author: str, db: db_dependency, user: user_dependency, exact_match: bool = Query(False)):
    validate_user(user)

    query = db.query(Books).join(BookAuthorAssociation).join(BookAuthor)
    if exact_match:
        books = query.filter(BookAuthor.name == author).all()
    else:
        books = query.filter(BookAuthor.name.ilike(f"%{author}%")).all()

    if books:
        return books
    else:
        raise HTTPException(status_code=404, detail="No books found for the given author.")


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

    query = db.query(Books)

    if author:
        query = query.join(BookAuthorAssociation).join(BookAuthor).filter(BookAuthor.name.ilike(f"%{author}%"))

    if title:
        query = query.filter(Books.title.ilike(f"%{title}%"))
    if publisher:
        query = query.filter(Books.publisher.ilike(f"%{publisher}%"))
    if category:
        query = query.filter(Books.category.any(category))
    if maturity_rating:
        query = query.filter(Books.maturity_rating.ilike(f"%{maturity_rating}%"))
    if print_type:
        query = query.filter(Books.print_type.ilike(f"%{print_type}%"))

    if all(param is None for param in [title, author, publisher, category, print_type, maturity_rating]):
        query = query.order_by(Books.id.desc())

    results = query.limit(limit).all()

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
async def add_book(book_request: BookRequest, db: db_dependency, user: user_dependency):
    validate_admin(user)

    try:
        new_book = Books(**book_request.dict(exclude={"author"}))

        for author_name in book_request.author:
            author = db.query(BookAuthor).filter_by(name=author_name).first()
            if not author:
                author = BookAuthor(name=author_name)
                db.add(author)
                db.commit()

            book_author_link = BookAuthorAssociation(book=new_book, author=author)
            db.add(book_author_link)

        db.commit()
        actionlog.add_log("New book", f"{book_request.title} added at {datetime.now().strftime('%H:%M:%S')}",
                          user.get('username'))
        return {"message": "Book added successfully with authors"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error adding book: {str(e)}")


@router.put("/update/{book_id}", status_code=status.HTTP_202_ACCEPTED)
async def update_book(book_id: int, book_request: BookRequest, db: db_dependency, user: user_dependency):
    validate_admin(user)

    book = db.query(Books).filter(Books.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    for key, value in book_request.dict(exclude={"author"}).items():
        setattr(book, key, value)

    db.query(BookAuthorAssociation).filter(BookAuthorAssociation.book_id == book_id).delete()
    for author_name in book_request.author:
        author = db.query(BookAuthor).filter_by(name=author_name).first()
        if not author:
            author = BookAuthor(name=author_name)
            db.add(author)
            db.commit()
        book_author_link = BookAuthorAssociation(book_id=book.id, book_author_id=author.id)
        db.add(book_author_link)

    db.commit()
    return {"message": f"Book with ID {book_id} updated successfully."}


@router.delete("/delete/{book_id}", status_code=status.HTTP_202_ACCEPTED)
async def delete_book(book_id: int, db: db_dependency, user: user_dependency):
    validate_admin(user)

    db.query(BookAuthorAssociation).filter(BookAuthorAssociation.book_id == book_id).delete()
    deletion_result = db.query(Books).filter(Books.id == book_id).delete()

    if deletion_result:
        db.commit()
        return {"message": "Book deleted successfully."}
    else:
        db.rollback()
        raise HTTPException(status_code=404, detail="Book not found")
