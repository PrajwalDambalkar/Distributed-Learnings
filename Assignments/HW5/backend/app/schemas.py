from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

# Author Schemas
class AuthorBase(BaseModel):
    first_name: str
    last_name: str
    email: str

class AuthorCreate(AuthorBase):
    pass

class AuthorUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None

class AuthorOut(AuthorBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Book Schemas
class BookBase(BaseModel):
    title: str
    isbn: str
    publication_year: int
    available_copies: int = 1
    author_id: int

class BookCreate(BookBase):
    pass

class BookUpdate(BaseModel):
    title: Optional[str] = None
    isbn: Optional[str] = None
    publication_year: Optional[int] = None
    available_copies: Optional[int] = None
    author_id: Optional[int] = None

class BookOut(BookBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True