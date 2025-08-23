# routes/pydantic_models.py
from pydantic import BaseModel, constr, conint, EmailStr
from typing import Optional

# --- Category Models ---
class CategoryBase(BaseModel):
    name: constr(min_length=1, max_length=100)

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(CategoryBase):
    pass

# --- Book Models ---
class BookBase(BaseModel):
    title: constr(min_length=1, max_length=255)
    author: constr(min_length=1, max_length=255)
    isbn: constr(min_length=10, max_length=20) # ISBN-10 or ISBN-13
    total_quantity: conint(ge=0)
    category_id: int
    image_url: Optional[str] = None

class BookCreate(BookBase):
    pass

class BookUpdate(BaseModel):
    title: Optional[constr(min_length=1, max_length=255)] = None
    author: Optional[constr(min_length=1, max_length=255)] = None
    isbn: Optional[constr(min_length=10, max_length=20)] = None
    total_quantity: Optional[conint(ge=0)] = None
    available_quantity: Optional[conint(ge=0)] = None
    category_id: Optional[int] = None
    image_url: Optional[str] = None


# --- Borrowing Models ---
class BorrowBook(BaseModel):
    book_id: int
    borrower_name: constr(min_length=1, max_length=255)
    borrower_email: Optional[EmailStr] = None
    borrower_phone: Optional[constr(min_length=1, max_length=20)] = None # <--- 修改為可選，且 min_length 調整為 1 (如果提供)
    borrower_room_number: constr(min_length=1, max_length=10)
    borrower_hotel: constr(min_length=1, max_length=255)

class ReturnBook(BaseModel):
    borrowing_id: int
