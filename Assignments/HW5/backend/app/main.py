from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routes import authors, books

from .routes import authors, books, ai  # Add ai


# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Library Management System", version="1.0")

# CORS (for frontend later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(authors.router)
app.include_router(books.router)

@app.get("/")
def root():
    return {"message": "Library Management System API"}

# Include routers
app.include_router(authors.router)
app.include_router(books.router)
app.include_router(ai.router)