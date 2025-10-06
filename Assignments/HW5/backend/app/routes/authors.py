from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/authors", tags=["Authors"])

# CREATE Author
@router.post("/", response_model=schemas.AuthorOut, status_code=status.HTTP_201_CREATED)
def create_author(author: schemas.AuthorCreate, db: Session = Depends(get_db)):
    # Check if email already exists
    existing = db.query(models.Author).filter(models.Author.email == author.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    db_author = models.Author(**author.dict())
    db.add(db_author)
    db.commit()
    db.refresh(db_author)
    return db_author

# GET All Authors (with pagination)
@router.get("/", response_model=List[schemas.AuthorOut])
def get_authors(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    authors = db.query(models.Author).offset(skip).limit(limit).all()
    return authors

# GET Single Author
@router.get("/{author_id}", response_model=schemas.AuthorOut)
def get_author(author_id: int, db: Session = Depends(get_db)):
    author = db.query(models.Author).filter(models.Author.id == author_id).first()
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    return author

# UPDATE Author
@router.put("/{author_id}", response_model=schemas.AuthorOut)
def update_author(author_id: int, author: schemas.AuthorUpdate, db: Session = Depends(get_db)):
    db_author = db.query(models.Author).filter(models.Author.id == author_id).first()
    if not db_author:
        raise HTTPException(status_code=404, detail="Author not found")
    
    # Check email uniqueness if updating email
    if author.email and author.email != db_author.email:
        existing = db.query(models.Author).filter(models.Author.email == author.email).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")
    
    # Update fields
    for key, value in author.dict(exclude_unset=True).items():
        setattr(db_author, key, value)
    
    db.commit()
    db.refresh(db_author)
    return db_author

# DELETE Author
@router.delete("/{author_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_author(author_id: int, db: Session = Depends(get_db)):
    db_author = db.query(models.Author).filter(models.Author.id == author_id).first()
    if not db_author:
        raise HTTPException(status_code=404, detail="Author not found")
    
    # Check if author has books (prevent deletion)
    if db_author.books:
        raise HTTPException(
            status_code=400, 
            detail="Cannot delete author with existing books"
        )
    
    db.delete(db_author)
    db.commit()
    return None

# GET Books by Author (special endpoint)
@router.get("/{author_id}/books", response_model=List[schemas.BookOut])
def get_author_books(author_id: int, db: Session = Depends(get_db)):
    author = db.query(models.Author).filter(models.Author.id == author_id).first()
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    return author.books