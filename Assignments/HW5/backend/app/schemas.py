from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional
import re

# Author Schemas
class AuthorBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    email: str = Field(..., min_length=5, max_length=100)
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        # Simple email regex validation
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, v):
            raise ValueError('Invalid email format')
        return v.lower()  # Convert to lowercase

class AuthorCreate(AuthorBase):
    pass

class AuthorUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    email: Optional[str] = Field(None, min_length=5, max_length=100)
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        if v is not None:
            email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_regex, v):
                raise ValueError('Invalid email format')
            return v.lower()
        return v

class AuthorOut(AuthorBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Book Schemas
class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    isbn: str = Field(..., min_length=10, max_length=20)
    publication_year: int = Field(..., ge=1000, le=2100)
    available_copies: int = Field(default=1, ge=0)
    author_id: int = Field(..., gt=0)
    
    @field_validator('isbn')
    @classmethod
    def validate_isbn(cls, v):
        # Remove hyphens and spaces
        cleaned = v.replace('-', '').replace(' ', '')
        # Check if it's either ISBN-10 or ISBN-13
        if len(cleaned) not in [10, 13]:
            raise ValueError('ISBN must be 10 or 13 digits')
        if not cleaned.isdigit():
            raise ValueError('ISBN must contain only digits (and hyphens/spaces)')
        return v

class BookCreate(BookBase):
    pass

class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    isbn: Optional[str] = Field(None, min_length=10, max_length=20)
    publication_year: Optional[int] = Field(None, ge=1000, le=2100)
    available_copies: Optional[int] = Field(None, ge=0)
    author_id: Optional[int] = Field(None, gt=0)
    
    @field_validator('isbn')
    @classmethod
    def validate_isbn(cls, v):
        if v is not None:
            cleaned = v.replace('-', '').replace(' ', '')
            if len(cleaned) not in [10, 13]:
                raise ValueError('ISBN must be 10 or 13 digits')
            if not cleaned.isdigit():
                raise ValueError('ISBN must contain only digits (and hyphens/spaces)')
        return v

class BookOut(BookBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Chat application schemas
from enum import Enum
class MessageRoleEnum(str, Enum):
    user = "user"
    assistant = "assistant"
    system = "system"

# Chat Input/Output
class ChatIn(BaseModel):
    user_id: int = 1
    message: str
    conversation_id: Optional[int] = None
    title: Optional[str] = None

class ChatOut(BaseModel):
    conversation_id: int
    reply: str

# Message schemas
class MessageOut(BaseModel):
    id: int
    conversation_id: int
    role: str
    content: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Conversation schemas
class ConversationOut(BaseModel):
    id: int
    user_id: int
    title: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# The following code was the original code before adding validations. It is kept here for reference.
# import enum
# from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Enum

# from pydantic import BaseModel, Field
# from datetime import datetime
# from typing import Optional

# # Author Schemas
# class AuthorBase(BaseModel):
#     first_name: str
#     last_name: str
#     email: str

# class AuthorCreate(AuthorBase):
#     pass

# class AuthorUpdate(BaseModel):
#     first_name: Optional[str] = None
#     last_name: Optional[str] = None
#     email: Optional[str] = None

# class AuthorOut(AuthorBase):
#     id: int
#     created_at: datetime
#     updated_at: datetime
    
#     class Config:
#         from_attributes = True

# # Book Schemas
# class BookBase(BaseModel):
#     title: str
#     isbn: str
#     publication_year: int
#     available_copies: int = 1
#     author_id: int

# class BookCreate(BookBase):
#     pass

# class BookUpdate(BaseModel):
#     title: Optional[str] = None
#     isbn: Optional[str] = None
#     publication_year: Optional[int] = None
#     available_copies: Optional[int] = None
#     author_id: Optional[int] = None

# class BookOut(BookBase):
#     id: int
#     created_at: datetime
#     updated_at: datetime
    
#     class Config:
#         from_attributes = True