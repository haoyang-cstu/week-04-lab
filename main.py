from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session

from database import get_db, engine
from models import Book, Base
from schemas import BookCreate, BookUpdate, BookResponse

# Create tables in the database (if they don't exist yet)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Book Tracker API", version="2.0.0")


@app.get("/")
def read_root():
    return {"message": "Welcome to Book Tracker API"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/books", response_model=list[BookResponse])
def get_books(status: str | None = None, db: Session = Depends(get_db)):
    query = db.query(Book)
    if status:
        # Filter by status query parameter, e.g. GET /books?status=reading
        query = query.filter(Book.status == status)
    return query.all()


@app.get("/books/stats")
def get_stats(db: Session = Depends(get_db)):
    books = db.query(Book).all()
    total = len(books)

    # Count books in each status bucket.
    by_status = {}
    for book in books:
        by_status[book.status] = by_status.get(book.status, 0) + 1

    # Average rating across books that actually have a rating.
    ratings = [b.rating for b in books if b.rating is not None]
    average_rating = round(sum(ratings) / len(ratings), 2) if ratings else None

    return {
        "total": total,
        "by_status": by_status,
        "average_rating": average_rating,
    }


@app.get("/books/{book_id}", response_model=BookResponse)
def get_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@app.post("/books", response_model=BookResponse, status_code=201)
def create_book(data: BookCreate, db: Session = Depends(get_db)):
    book = Book(**data.model_dump())
    db.add(book)
    db.commit()
    db.refresh(book)
    return book


@app.put("/books/{book_id}", response_model=BookResponse)
def update_book(book_id: int, updates: BookUpdate, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")

    if updates.status is not None:
        book.status = updates.status
    if updates.rating is not None:
        book.rating = updates.rating

    db.commit()
    db.refresh(book)
    return book


@app.delete("/books/{book_id}")
def delete_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")

    db.delete(book)
    db.commit()
    return {"message": f"Book {book_id} deleted"}
