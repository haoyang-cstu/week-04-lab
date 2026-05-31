from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="Book Tracker API", version="1.0.0")

# Pydantic models for validation
class BookCreate(BaseModel):
    title: str
    author: str
    status: str = "want_to_read"  # "reading", "read", "want_to_read"
    rating: Optional[int] = None  # 1-5, only if status is "read"

class BookUpdate(BaseModel):
    status: Optional[str] = None
    rating: Optional[int] = None

# In-memory storage
books_db = []
next_id = 1

@app.get("/")
def read_root():
    return {"message": "Welcome to Book Tracker API"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/books")
def get_books(status: Optional[str] = None):
    if status:
        # Filter by status query parameter, e.g. GET /books?status=reading
        return [b for b in books_db if b["status"] == status]
    return books_db

@app.get("/books/stats")
def get_stats():
    total = len(books_db)

    # Count books in each status bucket.
    by_status = {}
    for book in books_db:
        by_status[book["status"]] = by_status.get(book["status"], 0) + 1

    # Average rating across books that actually have a rating.
    ratings = [b["rating"] for b in books_db if b["rating"] is not None]
    average_rating = round(sum(ratings) / len(ratings), 2) if ratings else None

    return {
        "total": total,
        "by_status": by_status,
        "average_rating": average_rating,
    }

@app.get("/books/{book_id}")
def get_book(book_id: int):
    for book in books_db:
        if book["id"] == book_id:
            return book
    raise HTTPException(status_code=404, detail="Book not found")

@app.post("/books", status_code=201)
def create_book(book: BookCreate):
    global next_id
    new_book = book.model_dump()
    new_book["id"] = next_id
    books_db.append(new_book)
    next_id += 1
    return new_book

@app.put("/books/{book_id}")
def update_book(book_id: int, updates: BookUpdate):
    for book in books_db:
        if book["id"] == book_id:
            if updates.status is not None:
                book["status"] = updates.status
            if updates.rating is not None:
                book["rating"] = updates.rating
            return book
    raise HTTPException(status_code=404, detail="Book not found")

@app.delete("/books/{book_id}")
def delete_book(book_id: int):
    for index, book in enumerate(books_db):
        if book["id"] == book_id:
            books_db.pop(index)
            return {"message": f"Book {book_id} deleted"}
    raise HTTPException(status_code=404, detail="Book not found")
