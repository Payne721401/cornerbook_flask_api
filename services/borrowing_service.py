# services/borrowing_service.py
from app import db
from models.book import Book
from models.borrowing import Borrowing
from datetime import datetime

def borrow_book_service(data):
    """
    Handles the business logic for borrowing a book.
    Manages database transaction and updates book availability.
    """
    book_id = data.get('book_id')
    
    try:
        # Use with_for_update to lock the selected row
        book = db.session.query(Book).filter_by(id=book_id).with_for_update().first()

        if not book:
            db.session.rollback()
            return None, "Book not found"

        if book.available_quantity <= 0:
            db.session.rollback()
            return None, "Book is not available for borrowing"

        book.available_quantity -= 1
        
        new_borrowing = Borrowing(
            book_id=book.id,
            borrower_name=data.get('borrower_name'),
            borrower_room_number=data.get('borrower_room_number'),
            borrower_hotel=data.get('borrower_hotel')
        )
        db.session.add(new_borrowing)
        db.session.commit()
        return new_borrowing, None
        
    except Exception as e:
        db.session.rollback()
        # In a real app, you'd want to log the error e
        return None, "An internal error occurred"

def return_book_service(borrowing_id):
    """
    Handles the business logic for returning a book.
    Manages database transaction and updates book availability.
    """
    try:
        # Find the specific, non-returned borrowing record and lock it
        borrowing_record = db.session.query(Borrowing).filter_by(
            id=borrowing_id, 
            is_returned=False
        ).with_for_update().first()

        if not borrowing_record:
            db.session.rollback()
            return None, "Active borrowing record not found"
        
        # Lock the associated book row as well
        book = db.session.query(Book).filter_by(id=borrowing_record.book_id).with_for_update().first()

        # --- Start of modifications ---
        # Add check to ensure available_quantity does not exceed total_quantity
        if book.available_quantity >= book.total_quantity:
            db.session.rollback()
            return None, "Cannot return book: available quantity would exceed total quantity"
        # --- End of modifications ---

        book.available_quantity += 1
        borrowing_record.is_returned = True
        borrowing_record.returned_at = datetime.utcnow()
        
        db.session.commit()
        return borrowing_record, None

    except Exception as e:
        db.session.rollback()
        # In a real app, you'd want to log the error e
        return None, "An internal error occurred"
