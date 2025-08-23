# routes/borrowings.py
from flask import Blueprint, request, jsonify
from services.borrowing_service import borrow_book_service, return_book_service
from models.borrowing import Borrowing
from models.book import Book # Import the Book model
from extensions import db
from routes.pydantic_models import BorrowBook
from flask_pydantic import validate
from sqlalchemy import or_ # Import or_ for complex queries

borrowings_bp = Blueprint('borrowings_bp', __name__)

@borrowings_bp.route('/borrow', methods=['POST'])
@validate()
def borrow_book_endpoint(body: BorrowBook):
    """Endpoint to borrow a book."""
    borrowing_record, error = borrow_book_service(body.model_dump())
    
    if error == "Book not found":
        return jsonify({"error": error}), 404
    if error == "Book is not available for borrowing":
        return jsonify({"error": error}), 409
    if error:
        return jsonify({"error": "An internal error occurred"}), 500
        
    return jsonify(borrowing_record.to_dict()), 201

@borrowings_bp.route('/return/<int:borrowing_id>', methods=['PATCH'])
def return_book_endpoint(borrowing_id: int):
    """Endpoint to return a book."""
    borrowing_record, error = return_book_service(borrowing_id)

    if error == "Active borrowing record not found":
        return jsonify({"error": error}), 404
    if error == "Cannot return book: available quantity would exceed total quantity":
        return jsonify({"error": error}), 409
    if error:
        return jsonify({"error": "An internal error occurred"}), 500

    return jsonify(borrowing_record.to_dict()), 200

@borrowings_bp.route('/', methods=['GET'], strict_slashes=False)
def get_borrowings():
    """Get a list of all borrowing records with optional filters and pagination."""
    query = db.session.query(Borrowing)
    
    # --- Fuzzy Search Logic ---
    search_filter = request.args.get('search')
    if search_filter:
        search_term = f"%{search_filter}%"
        # Join with the Book table to search by book title
        query = query.join(Book, Borrowing.book_id == Book.id)
        query = query.filter(
            or_(
                Borrowing.borrower_name.ilike(search_term),
                Borrowing.borrower_email.ilike(search_term),
                Borrowing.borrower_phone.ilike(search_term),
                Borrowing.borrower_hotel.ilike(search_term),
                Book.title.ilike(search_term)
            )
        )

    # --- is_returned Filter Logic ---
    is_returned_filter = request.args.get('is_returned')
    if is_returned_filter is not None:
        if is_returned_filter.lower() in ['false', 'f', '0', 'no']:
            query = query.filter(Borrowing.is_returned == False)
        elif is_returned_filter.lower() in ['true', 't', '1', 'yes']:
            query = query.filter(Borrowing.is_returned == True)
            
    # --- Pagination Logic ---
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)

    if per_page == 0:
        items = query.order_by(Borrowing.borrowed_at.desc()).all()
        class AllItemsPagination:
            def __init__(self, items):
                self.items = items
                self.total = len(items)
                self.pages = 1 if self.total > 0 else 0
                self.page = 1
                self.per_page = self.total
                self.has_next = False
                self.has_prev = False
                self.next_num = None
                self.prev_num = None
        pagination_obj = AllItemsPagination(items)
    else:
        pagination_obj = query.order_by(Borrowing.borrowed_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
    
    # Format and return the response
    return jsonify({
        "borrowings": [b.to_dict() for b in pagination_obj.items],
        "pagination": {
            "total": pagination_obj.total,
            "pages": pagination_obj.pages,
            "page": pagination_obj.page,
            "per_page": pagination_obj.per_page,
            "has_next": pagination_obj.has_next,
            "has_prev": pagination_obj.has_prev,
            "next_num": pagination_obj.next_num,
            "prev_num": pagination_obj.prev_num
        }
    }), 200

@borrowings_bp.route('/<int:id>', methods=['GET'])
def get_borrowing(id):
    """Get a single borrowing record by ID."""
    borrowing = db.session.get(Borrowing, id)
    if not borrowing:
        return jsonify({"error": "Borrowing record not found"}), 404
    return jsonify(borrowing.to_dict()), 200
