# tests/integration/test_borrowing_api.py
import json
from app import db
from models.book import Book
from models.category import Category
from models.borrowing import Borrowing

# --- Success Scenarios ---

def test_borrow_successful_transaction(client, db_session, auth_headers):
    """
    GIVEN a book with available quantity > 0
    WHEN a POST request is made to /api/borrowings/borrow
    THEN the book's available quantity should decrease by 1 and a borrowing record is created.
    """
    category = Category(name="Test Category")
    book = Book(title="Test Book", author="Test Author", isbn="12345", total_quantity=2, available_quantity=2, category=category)
    db_session.add_all([category, book])
    db_session.commit()
    
    borrow_data = {
        "book_id": book.id, 
        "borrower_name": "John Doe",
        "borrower_email": "john.doe@example.com",
        "borrower_phone": "123-456-7890",
        "borrower_room_number": "101",
        "borrower_hotel": "Grand Hotel"
    }
    
    response = client.post('/api/borrowings/borrow', data=json.dumps(borrow_data), content_type='application/json', headers=auth_headers)
    assert response.status_code == 201
    
    # Verify book quantity
    assert db.session.get(Book, book.id).available_quantity == 1
    
    # Verify borrowing record details
    borrowing_record = db.session.query(Borrowing).filter_by(book_id=book.id).first()
    assert borrowing_record is not None
    assert borrowing_record.borrower_name == "John Doe"
    assert borrowing_record.borrower_email == "john.doe@example.com"
    assert borrowing_record.borrower_phone == "123-456-7890"

def test_borrow_out_of_stock_transaction(client, db_session, auth_headers):
    """
    GIVEN a book with available quantity = 0
    WHEN a POST request is made to /api/borrowings/borrow
    THEN the transaction should fail with a 409 status code.
    """
    category = Category(name="Test Category")
    book = Book(title="Test Book", author="Test Author", isbn="12345", total_quantity=1, available_quantity=0, category=category)
    db_session.add_all([category, book])
    db_session.commit()
    
    borrow_data = {
        "book_id": book.id, 
        "borrower_name": "John Doe",
        "borrower_email": "john.doe@example.com",
        "borrower_phone": "123-456-7890",
        "borrower_room_number": "101",
        "borrower_hotel": "Grand Hotel"
    }
    
    response = client.post('/api/borrowings/borrow', data=json.dumps(borrow_data), content_type='application/json', headers=auth_headers)
    assert response.status_code == 409

def test_return_successful_transaction(client, db_session, auth_headers):
    """
    GIVEN an unreturned borrowing record
    WHEN a PATCH request is made to /api/borrowings/return/{borrowing_id}
    THEN the book's available quantity should increase by 1 and the borrowing record is marked as returned.
    """
    category = Category(name="Test Category")
    book = Book(title="Test Book", author="Test Author", isbn="12345", total_quantity=2, available_quantity=1, category=category)
    borrowing = Borrowing(
        book=book, 
        borrower_name="John Doe", 
        is_returned=False, 
        borrower_email="john.doe@example.com",
        borrower_phone="123-456-7890",
        borrower_room_number="101", 
        borrower_hotel="Grand Hotel"
    )
    db_session.add_all([category, book, borrowing])
    db_session.commit()
    
    response = client.patch(f'/api/borrowings/return/{borrowing.id}', content_type='application/json', headers=auth_headers)
    assert response.status_code == 200
    
    assert db.session.get(Book, book.id).available_quantity == 2
    assert db.session.get(Borrowing, borrowing.id).is_returned is True
    assert db.session.get(Borrowing, borrowing.id).returned_at is not None

def test_return_record_not_found(client, auth_headers):
    """
    GIVEN a non-existent borrowing record ID
    WHEN a PATCH request is made to /api/borrowings/return/{borrowing_id}
    THEN the response should be 404 Not Found.
    """
    non_existent_id = 9999
    response = client.patch(f'/api/borrowings/return/{non_existent_id}', content_type='application/json', headers=auth_headers)
    assert response.status_code == 404

# --- New Fuzzy Search Tests ---

def test_get_borrowings_fuzzy_search(client, db_session, auth_headers):
    """
    GIVEN multiple borrowing records with different data
    WHEN a GET request with a 'search' query parameter is made
    THEN only the matching borrowing records should be returned.
    """
    # Setup Data
    cat = Category(name="Searchable Books")
    book1 = Book(title="The Art of Programming", author="Author A", isbn="111", total_quantity=2, available_quantity=1, category=cat)
    book2 = Book(title="Another Fine Book", author="Author B", isbn="222", total_quantity=1, available_quantity=1, category=cat)
    
    b1 = Borrowing(book=book1, borrower_name="Alice Smith", borrower_email="alice.s@web.com", borrower_phone="111-222-3333", borrower_room_number="A1", borrower_hotel="Grand Palace")
    b2 = Borrowing(book=book2, borrower_name="Bob Johnson", borrower_email="bob.j@mail.net", borrower_phone="444-555-6666", borrower_room_number="B2", borrower_hotel="Central Inn")
    b3 = Borrowing(book=book1, borrower_name="Charlie Brown", borrower_email="charlie@web.com", borrower_phone="777-888-9999", borrower_room_number="C3", borrower_hotel="Grand Palace")
    
    db_session.add_all([cat, book1, book2, b1, b2, b3])
    db_session.commit()

    # Test cases: (search_term, expected_ids)
    test_cases = [
        ("alice", [b1.id]),          # Search by name (case-insensitive)
        ("MAIL.NET", [b2.id]),        # Search by email (case-insensitive)
        ("555", [b2.id]),             # Search by partial phone
        ("Grand Palace", [b1.id, b3.id]), # Search by hotel
        ("art of programming", [b1.id, b3.id]), # Search by book title (case-insensitive)
        ("web.com", [b1.id, b3.id]),    # Search by part of email domain
        ("nonexistent", []),          # Search with no results
        ("o", [b1.id, b2.id, b3.id])    # Broad search matching name, book, hotel
    ]

    for term, expected_ids in test_cases:
        response = client.get(f'/api/borrowings/?search={term}', headers=auth_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        
        returned_ids = {item['id'] for item in data['borrowings']}
        assert returned_ids == set(expected_ids), f"Search for '{term}' failed"
