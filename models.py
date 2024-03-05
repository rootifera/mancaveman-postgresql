import datetime
from typing import Optional, List

from pydantic import BaseModel, Field
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import UniqueConstraint

from database import Base


class LocationRequest(BaseModel):
    name: str
    type_id: int
    parent_id: Optional[int] = None


class LocationUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, description="New name for the location")
    type_id: Optional[int] = Field(None, description="New type ID for the location")
    parent_id: Optional[int] = Field(None, description="New parent ID for the location")


class LocationTypeRequest(BaseModel):
    name: str


class LocationType(Base):
    __tablename__ = 'location_types'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    locations = relationship("Location", backref="type", lazy="dynamic")


class Location(Base):
    __tablename__ = 'locations'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    type_id = Column(Integer, ForeignKey('location_types.id', ondelete="CASCADE"), nullable=False)
    parent_id = Column(Integer, ForeignKey('locations.id', ondelete="CASCADE"), nullable=True)
    children = relationship("Location", backref=backref('parent', remote_side=[id]),
                            cascade="all, delete, delete-orphan")


class InitDB(Base):
    __tablename__ = 'initdb'
    id = Column(Integer, primary_key=True)
    status = Column(Boolean, default=False)


class Users(Base):
    """Class for users"""
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    username = Column(String, unique=True)
    hashed_password = Column(String)
    is_admin = Column(Boolean, default=True)
    reset_token = Column(String, default='NORESET')
    books_api_key = Column(String, default='NOKEY')


class CreateUserRequest(BaseModel):
    username: str
    email: str
    password: str
    is_admin: bool


class Token(BaseModel):
    access_token: str
    refresh_token: Optional[str]
    token_type: str


class Hardware(Base):
    """Class for Hardware"""
    __tablename__ = 'hardware'

    id = Column(Integer, primary_key=True, index=True)
    category = relationship("HardwareCategory", back_populates="hardware")
    category_id = Column(Integer, ForeignKey('hardware_category.id'))
    component_type = relationship("ComponentType", back_populates="hardware")
    component_type_id = Column(Integer, ForeignKey('component_type.id'))
    brand = relationship("HardwareBrand", back_populates="hardware")
    brand_id = Column(Integer, ForeignKey('hardware_brand.id'))
    model = Column(String)
    condition = Column(String, default="Untested")
    quantity = Column(Integer)
    location = Column(String)
    is_new = Column(Boolean, default=False)
    purchase_date = Column(String, nullable=True)
    purchased_from = Column(String, nullable=True)
    store_link = Column(String, nullable=True)
    photos = Column(String, nullable=True)
    user_manual = Column(String, nullable=True)
    invoice = Column(String, nullable=True)
    barcode = Column(String, nullable=True)
    repair_history = Column(String, nullable=True)
    notes = Column(String, nullable=True)


class HardwareRequest(BaseModel):
    category_id: int
    component_type_id: int
    brand_id: int
    model: str
    condition: str
    quantity: int
    location: str
    is_new: bool
    purchase_date: Optional[str]
    purchased_from: Optional[str]
    store_link: Optional[str]
    photos: Optional[str]
    user_manual: Optional[str]
    invoice: Optional[str]
    barcode: Optional[str]
    repair_history: Optional[str]
    tags: List[str] = []
    notes: Optional[str]


class HardwareBrand(Base):
    __tablename__ = 'hardware_brand'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    hardware = relationship("Hardware", back_populates="brand")


class HardwareBrandRequest(BaseModel):
    name: str


class HardwareCategory(Base):
    __tablename__ = 'hardware_category'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    hardware = relationship("Hardware", back_populates="category")
    component_types = relationship("ComponentType", back_populates="hardware_category")


class HardwareCategoryRequest(BaseModel):
    name: str


class ComponentType(Base):
    __tablename__ = 'component_type'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    hardware_category_id = Column(Integer, ForeignKey('hardware_category.id'))
    hardware_category = relationship("HardwareCategory")
    hardware = relationship("Hardware", back_populates="component_type")


class ComponentTypeRequest(BaseModel):
    name: str
    hardware_category_id: int


class Tag(Base):
    __tablename__ = 'tags'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    tag_type = Column(String)
    __table_args__ = (UniqueConstraint('name', 'tag_type', name='_name_tag_type_uc'),)


class HardwareTag(Base):
    __tablename__ = 'hardware_tags'
    hardware_id = Column(Integer, ForeignKey('hardware.id'), primary_key=True)
    tag_id = Column(Integer, ForeignKey('tags.id'), primary_key=True)


class Software(Base):
    __tablename__ = 'software'
    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey('software_category.id'))
    category = relationship("SoftwareCategory", back_populates="software")
    name = Column(String)
    publisher_id = Column(Integer, ForeignKey('software_publisher.id'))
    publisher = relationship("SoftwarePublisher", back_populates="software")
    developer_id = Column(Integer, ForeignKey('software_developer.id'))
    developer = relationship("SoftwareDeveloper", back_populates="software")
    platform_id = Column(Integer, ForeignKey('software_platform.id'))
    platform = relationship("SoftwarePlatform", back_populates="software")
    year = Column(Integer, nullable=True)
    barcode = Column(String, nullable=True)
    location = Column(String)
    media_type_id = Column(Integer, ForeignKey('software_type.id'))
    media_type = relationship("SoftwareMediaType", back_populates="software")
    media_count = Column(Integer, nullable=True)
    condition = Column(String, nullable=True)
    product_key = Column(String, nullable=True)
    photo = Column(String, nullable=True)
    multiple_copies = Column(Boolean, nullable=True, default=False)
    multicopy_id = Column(Integer, nullable=True)
    image_backups = Column(Boolean, nullable=True, default=False)
    image_backup_location = Column(String, nullable=True)
    redump_disk_ids = Column(String, nullable=True)
    notes = Column(String, nullable=True)


class SoftwareTag(Base):
    __tablename__ = 'software_tags'
    software_id = Column(Integer, ForeignKey('software.id'), primary_key=True)
    tag_id = Column(Integer, ForeignKey('tags.id'), primary_key=True)


class SoftwareCategory(Base):
    __tablename__ = 'software_category'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    software = relationship("Software", back_populates="category")


class SoftwareCategoryRequest(BaseModel):
    name: str


class SoftwarePublisher(Base):
    __tablename__ = 'software_publisher'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    software = relationship("Software", back_populates="publisher")


class SoftwarePublisherRequest(BaseModel):
    name: str


class SoftwareDeveloper(Base):
    __tablename__ = 'software_developer'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    software = relationship("Software", back_populates="developer")


class SoftwareDeveloperRequest(BaseModel):
    name: str


class SoftwarePlatform(Base):
    __tablename__ = 'software_platform'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    software = relationship("Software", back_populates="platform")


class SoftwarePlatformRequest(BaseModel):
    name: str


class SoftwareMediaType(Base):
    __tablename__ = 'software_type'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    software = relationship("Software", back_populates="media_type")


class SoftwareMediaTypeRequest(BaseModel):
    name: str


class SoftwareRequest(BaseModel):
    category_id: int
    name: str
    publisher_id: int
    developer_id: int
    platform_id: int
    year: Optional[int]
    barcode: Optional[str]
    location: str
    media_type_id: Optional[int]
    media_count: Optional[int]
    condition: Optional[str]
    product_key: Optional[str]
    photo: Optional[str]
    multiple_copies: Optional[bool]
    multicopy_id: Optional[int]
    image_backups: Optional[bool]
    image_backup_location: Optional[str]
    redump_disk_ids: Optional[str]
    tags: List[str] = []
    notes: Optional[str]


class ActionLog(Base):
    """Class for logs"""
    __tablename__ = 'actionlog'

    id = Column(Integer, primary_key=True, index=True)
    action = Column(String)
    log = Column(String)
    user = Column(String)
    log_date = Column(String, default=datetime.date.today(), nullable=False)


class Books(Base):
    """Class for books"""
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True, index=True)
    isbn_10 = Column(String, nullable=True, index=True)
    isbn_13 = Column(String, nullable=True, index=True)
    title = Column(String, index=True)
    subtitle = Column(String, nullable=True)
    authors = relationship('BookAuthorAssociation', back_populates='book')
    publisher = Column(String, index=True)
    published_date = Column(String)
    description = Column(String, nullable=True)
    categories = relationship('BookCategoryAssociation', back_populates='book')
    print_type = Column(String, nullable=True)
    maturity_rating = Column(String, nullable=True)
    condition = Column(String, nullable=True)
    location_id = Column(Integer, ForeignKey('locations.id'), nullable=True)
    position = Column(String, nullable=True)
    location = relationship('Location', backref='books')


class BookRequest(BaseModel):
    title: str
    subtitle: Optional[str] = ''
    author: List[str]
    publisher: str
    published_date: str
    description: Optional[str] = ''
    category: List[str] = []
    print_type: Optional[str] = ''
    maturity_rating: Optional[str] = ''
    condition: Optional[str] = ''
    isbn_10: Optional[str] = ''
    isbn_13: Optional[str] = ''
    location: List[LocationRequest] = []
    position: Optional[str] = ''


class BookAuthorAssociation(Base):
    __tablename__ = 'book_author_association'
    book_id = Column(Integer, ForeignKey('books.id', ondelete="CASCADE"), primary_key=True)
    author_id = Column(Integer, ForeignKey('book_author.id', ondelete="CASCADE"), primary_key=True)
    book = relationship('Books', back_populates='authors')
    author = relationship('BookAuthor', back_populates='books')


class BookAuthor(Base):
    __tablename__ = 'book_author'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    books = relationship('BookAuthorAssociation', back_populates='author')


class BookCategory(Base):
    __tablename__ = 'book_category'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    books = relationship('BookCategoryAssociation', back_populates='category')


class BookCategoryAssociation(Base):
    __tablename__ = 'book_category_association'
    book_id = Column(Integer, ForeignKey('books.id'), primary_key=True)
    book_category_id = Column(Integer, ForeignKey('book_category.id'), primary_key=True)
    book = relationship('Books', back_populates='categories')
    category = relationship('BookCategory', back_populates='books')
