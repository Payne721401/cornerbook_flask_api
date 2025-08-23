# routes/books.py
from flask import Blueprint, request, jsonify
from extensions import db
from models.book import Book
from models.category import Category
from services.book_service import get_all_books_service
from routes.pydantic_models import BookCreate, BookUpdate
from flask_pydantic import validate
from sqlalchemy.exc import IntegrityError

books_bp = Blueprint('books_bp', __name__)

@books_bp.route('/', methods=['POST'], strict_slashes=False)
@validate()
def create_book(body: BookCreate):
    """Create a new book."""

    category = db.session.get(Category, body.category_id)
    if not category:
        return jsonify({"error": f"Category with id {body.category_id} not found."}), 404

    try:
        new_book = Book(
            title=body.title,
            author=body.author,
            isbn=body.isbn,
            total_quantity=body.total_quantity,
            available_quantity=body.total_quantity,
            category_id=body.category_id,
            image_url=body.image_url
        )
        db.session.add(new_book)
        db.session.commit()
        return jsonify(new_book.to_dict()), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Failed to create book. ISBN might already exist or category_id is invalid."}), 409

@books_bp.route('/', methods=['GET'], strict_slashes=False)
def get_books():
    """Get a list of books with optional filters and pagination."""
    filters = {
        'search': request.args.get('search'),
        'category': request.args.get('category'),
        'available': request.args.get('available')
    }

    # Get pagination parameters with defaults
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)

    # Get paginated books from the service
    pagination_obj = get_all_books_service(filters, page, per_page)
    
    # Format the response to include pagination metadata
    return jsonify({
        "books": [book.to_dict() for book in pagination_obj.items],
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

@books_bp.route('/<int:id>', methods=['GET'])
def get_book(id):
    """Get a single book by ID."""
    book = db.session.get(Book, id)
    if not book:
        return jsonify({"error": "Book not found"}), 404
    return jsonify({"book": book.to_dict()}), 200

@books_bp.route('/<int:id>', methods=['PATCH'])
@validate()
def update_book(id, body: BookUpdate):
    """Update book information (partial updates)."""
    book = db.session.get(Book, id)
    if not book:
        return jsonify({"error": "Book not found"}), 404

    update_data = body.model_dump(exclude_unset=True)

    if 'total_quantity' in update_data:
        new_total_quantity = update_data['total_quantity']
        
        borrowed_count = book.total_quantity - book.available_quantity

        # 新的總數不能少於已被借出的數量
        if new_total_quantity < borrowed_count:
            return jsonify({
                "error": f"Cannot reduce total quantity to {new_total_quantity}. "
                         f"There are currently {borrowed_count} books on loan."
            }), 409

        # 計算數量差異，並應用到可借閱數量上
        quantity_diff = new_total_quantity - book.total_quantity
        book.available_quantity += quantity_diff
        book.total_quantity = new_total_quantity
        
        # 從 update_data 中移除 total_quantity，避免被下方的通用邏輯重複設定
        del update_data['total_quantity']

    try:
        for key, value in update_data.items():
            setattr(book, key, value)
        db.session.commit()
        return jsonify(book.to_dict()), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Update failed. ISBN might already exist or category_id is invalid."}), 409

@books_bp.route('/<int:id>', methods=['DELETE'])
def delete_book(id):
    """Delete a book."""
    book = db.session.get(Book, id)
    if not book:
        return jsonify({"error": "Book not found"}), 404
    
    if any(not b.is_returned for b in book.borrowings):
        return jsonify({"error": "Cannot delete book with active borrowing records."}), 409

    db.session.delete(book)
    db.session.commit()
    return '', 204
