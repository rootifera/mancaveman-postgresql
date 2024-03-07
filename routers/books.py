"""Books Module"""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy.orm import joinedload
from starlette import status

from dependencies import db_dependency, user_dependency
from models import Users, Books, BookRequest, BookAuthor, BookAuthorAssociation, BookCategory, BookCategoryAssociation, \
    Location, ItemLocation
from tools import actionlog
from tools.book_populator import get_book_info
from tools.common import validate_admin, validate_user

router = APIRouter(
    prefix='/books',
    tags=['books']
)


def format_book_response(book, db_session):
    author_names = db_session.query(BookAuthor.name).join(
        BookAuthorAssociation, BookAuthorAssociation.author_id == BookAuthor.id
    ).filter(BookAuthorAssociation.book_id == book.id).all()
    authors_list = [author[0] for author in author_names]

    category_names = db_session.query(BookCategory.name).join(
        BookCategoryAssociation, BookCategoryAssociation.book_category_id == BookCategory.id
    ).filter(BookCategoryAssociation.book_id == book.id).all()
    categories_list = [category[0] for category in category_names]

    item_location_info = db_session.query(ItemLocation.location_id).filter(
        ItemLocation.item_id == book.id,
        ItemLocation.item_type == 'book'
    ).first()

    location_hierarchy = []
    if item_location_info:
        location_id = item_location_info.location_id
        location_info = db_session.query(Location).filter(Location.id == location_id).first()
        while location_info:
            location_hierarchy.insert(0, {"id": location_info.id, "name": location_info.name,
                                          "parent_id": location_info.parent_id})
            location_info = db_session.query(Location).filter(Location.id == location_info.parent_id).first()

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
        "categories": categories_list,
        "print_type": book.print_type,
        "maturity_rating": book.maturity_rating,
        "condition": book.condition,
        "position": book.position,
        "location": location_hierarchy,
    }

    return book_data


@router.get("/get_all", status_code=status.HTTP_200_OK)
async def get_all(db: db_dependency, user: user_dependency):
    validate_user(user)
    books = db.query(Books).all()
    formatted_books = [format_book_response(book, db) for book in books]
    return formatted_books


@router.get("/get_by_id/{id}", status_code=status.HTTP_200_OK)
async def get_by_id(db: db_dependency, user: user_dependency, id: int):
    validate_user(user)
    book = db.query(Books).filter(Books.id == id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    formatted_book = format_book_response(book, db)
    return formatted_book


@router.get("/get_by_title/{title}", status_code=status.HTTP_200_OK)
async def get_by_title(user: user_dependency, db: db_dependency, title: str,
                       exact_match: bool = Query(False, description="Search for books by an exact title match.")):
    validate_user(user)

    query = db.query(Books).options(joinedload(Books.authors), joinedload(Books.categories))

    if exact_match:
        books = query.filter(Books.title == title).all()
    else:
        books = query.filter(Books.title.ilike(f"%{title}%")).all()

    if not books:
        raise HTTPException(status_code=404, detail="No books found with the given title.")

    formatted_books = [format_book_response(book, db) for book in books]
    return formatted_books


@router.get("/get_by_author/{author}", status_code=status.HTTP_200_OK)
async def get_by_author(author: str, db: db_dependency, user: user_dependency,
                        exact_match: bool = Query(False, description="Search for books by an exact author match.")):
    validate_user(user)

    query = db.query(Books).join(BookAuthorAssociation).join(BookAuthor)
    if exact_match:
        books = query.filter(BookAuthor.name == author).all()
    else:
        books = query.filter(BookAuthor.name.ilike(f"%{author}%")).all()

    if not books:
        raise HTTPException(status_code=404, detail="No books found for the given author.")

    formatted_books = [format_book_response(book, db) for book in books]
    return formatted_books


@router.get("/get_by_publisher/{publisher}", status_code=status.HTTP_200_OK)
async def get_by_publisher(user: user_dependency, db: db_dependency, publisher: str,
                           exact_match: bool = Query(False,
                                                     description="Search for books by an exact publisher match.")):
    validate_user(user)

    query = db.query(Books)
    if exact_match:
        query = query.filter(Books.publisher == publisher)
    else:
        query = query.filter(Books.publisher.ilike(f"%{publisher}%"))

    query = query.options(joinedload(Books.authors), joinedload(Books.categories))

    books = query.all()

    if not books:
        raise HTTPException(status_code=404, detail="No books found with the given publisher.")

    formatted_books = [format_book_response(book, db) for book in books]
    return formatted_books


@router.get("/get_by_category/{category}", status_code=status.HTTP_200_OK)
async def get_by_category(user: user_dependency, db: db_dependency, category: str,
                          exact_match: bool = Query(False, description="Search for books by an exact category match.")):
    validate_user(user)

    query = db.query(Books).join(BookCategoryAssociation).join(BookCategory)
    if exact_match:
        books = query.filter(BookCategory.name == category).all()
    else:
        books = query.filter(BookCategory.name.ilike(f"%{category}%")).all()

    if not books:
        raise HTTPException(status_code=404, detail="No books found for the given category.")

    formatted_books = [format_book_response(book, db) for book in books]
    return formatted_books


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

    formatted_books = [format_book_response(book, db) for book in books]
    return formatted_books


@router.get("/get_by_isbn/{isbn}", status_code=status.HTTP_200_OK)
async def get_by_isbn(db: db_dependency, user: user_dependency, isbn: str):
    validate_user(user)

    if len(isbn) not in [10, 13]:
        raise HTTPException(status_code=400, detail="Invalid ISBN format. ISBN must be either 10 or 13 digits long.")

    isbn_field = Books.isbn_10 if len(isbn) == 10 else Books.isbn_13
    book = db.query(Books).filter(isbn_field == isbn).first()

    if book:
        formatted_book = format_book_response(book, db)
        return formatted_book
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
        query = query.join(BookCategoryAssociation).join(BookCategory).filter(BookCategory.name.ilike(f"%{category}%"))
    if maturity_rating:
        query = query.filter(Books.maturity_rating.ilike(f"%{maturity_rating}%"))
    if print_type:
        query = query.filter(Books.print_type.ilike(f"%{print_type}%"))

    if all(param is None for param in [title, author, publisher, category, print_type, maturity_rating]):
        query = query.order_by(Books.id.desc())

    results = query.limit(limit).all()

    if not results:
        raise HTTPException(status_code=404, detail="No books found matching the search criteria.")

    formatted_results = [format_book_response(book, db) for book in results]
    return formatted_results


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

    if db.query(Books).filter(
            (Books.isbn_10 == book_request.isbn_10) | (Books.isbn_13 == book_request.isbn_13)).first():
        raise HTTPException(status_code=400, detail="Book with the same ISBN already exists")

    new_book = Books(**book_request.dict(exclude={"author", "category", "location_id", "position"}))
    db.add(new_book)
    db.commit()

    for author_name in book_request.author:
        author, _ = db.get_or_create(BookAuthor, name=author_name)
        db.add(BookAuthorAssociation(book_id=new_book.id, author_id=author.id))

    for category_name in book_request.category:
        category, _ = db.get_or_create(BookCategory, name=category_name)
        db.add(BookCategoryAssociation(book_id=new_book.id, category_id=category.id))

    if book_request.location_id is not None:
        item_location = ItemLocation(item_id=new_book.id, item_type='book', location_id=book_request.location_id,
                                     position=book_request.position)
        db.add(item_location)

    db.commit()

    # Log the action
    actionlog.add_log("New book added",
                      f"Book titled '{book_request.title}' added at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                      user.get('username'))

    return {"message": "Book added successfully with authors, categories, and location"}


@router.put("/update/{book_id}", status_code=status.HTTP_202_ACCEPTED)
async def update_book(book_id: int, book_request: BookRequest, db: db_dependency, user: user_dependency):
    validate_admin(user)

    book = db.query(Books).filter(Books.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    if book_request.isbn_10 or book_request.isbn_13:
        existing_book = db.query(Books).filter(
            Books.id != book_id,
            (Books.isbn_10 == book_request.isbn_10) | (Books.isbn_13 == book_request.isbn_13)
        ).first()
        if existing_book:
            raise HTTPException(status_code=400, detail="Another book with the given ISBN already exists.")

    for key, value in book_request.dict(exclude={"author", "category", "location_id", "position"}).items():
        if hasattr(book, key) and value is not None:
            setattr(book, key, value)

    db.query(BookAuthorAssociation).filter(BookAuthorAssociation.book_id == book_id).delete()
    for author_name in book_request.author:
        author, _ = db.get_or_create(BookAuthor, name=author_name)
        db.add(BookAuthorAssociation(book_id=book.id, author_id=author.id))

    if book_request.location_id is not None:
        item_location = db.query(ItemLocation).filter(ItemLocation.item_id == book_id,
                                                      ItemLocation.item_type == 'book').first()
        if item_location:
            item_location.location_id = book_request.location_id
            item_location.position = book_request.position
        else:
            db.add(ItemLocation(item_id=book_id, item_type='book', location_id=book_request.location_id,
                                position=book_request.position))

    db.commit()

    actionlog.add_log("Book updated",
                      f"Book titled '{book_request.title}' updated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                      user.get('username'))

    return {"message": f"Book with ID {book_id} updated successfully."}


@router.delete("/delete/{book_id}", status_code=status.HTTP_202_ACCEPTED)
async def delete_book(book_id: int, db: db_dependency, user: user_dependency):
    validate_admin(user)

    book = db.query(Books).filter(Books.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    db.query(BookAuthorAssociation).filter(BookAuthorAssociation.book_id == book_id).delete()

    db.query(BookCategoryAssociation).filter(BookCategoryAssociation.book_id == book_id).delete()

    db.query(ItemLocation).filter(ItemLocation.item_id == book_id, ItemLocation.item_type == 'book').delete()

    db.delete(book)
    db.commit()

    return {"message": "Book deleted successfully."}
