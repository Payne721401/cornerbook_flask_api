import json
import threading
from models.book import Book
from models.category import Category
from models.borrowing import Borrowing

# --- 4. PATCH Method Details Test ---
def test_patch_book_partial_update(client, db_session, auth_headers):
    """
    SCENARIO: Send a PATCH request with only some fields.
    GIVEN: An existing book with a title and author.
    WHEN: A PATCH request is sent with only a new image_url.
    THEN: Check that only the image_url is updated and other fields remain unchanged.
    """
    book = Book(
        title="Original Title", author="Original Author", isbn="PATCHTEST001",
        total_quantity=1, available_quantity=1
    )
    db_session.add(book)
    db_session.commit()
    original_title = book.title
    response = client.patch(
        f'/api/books/{book.id}',
        data=json.dumps({"image_url": "http://example.com/new.jpg"}),
        content_type='application/json', 
        headers=auth_headers
    )
    assert response.status_code == 200
    db_session.refresh(book)
    assert book.image_url == "http://example.com/new.jpg"
    assert book.title == original_title

def test_patch_book_empty_payload(client, db_session, auth_headers):
    """
    SCENARIO: Send a PATCH request with an empty payload.
    GIVEN: An existing book.
    WHEN: An empty PATCH request is sent.
    THEN: Check that the book's data remains completely unchanged.
    """
    book = Book(
        title="Untouched Title", author="Untouched Author", isbn="PATCHTEST002",
        total_quantity=1, available_quantity=1
    )
    db_session.add(book)
    db_session.commit()
    original_author = book.author
    response = client.patch(
        f'/api/books/{book.id}',
        data=json.dumps({}),
        content_type='application/json',
        headers=auth_headers
    )
    assert response.status_code == 200
    db_session.refresh(book)
    assert book.author == original_author


# --- 3. Foreign Key Constraint Tests ---
def test_delete_book_with_active_borrowing(client, db_session, auth_headers):
    """
    SCENARIO: Attempt to delete a book that has not been returned.
    GIVEN: A book with an active borrowing record.
    WHEN: A DELETE request is sent for that book.
    THEN: Check the response is 409 Conflict, protecting data integrity.
    """
    book = Book(title="Borrowed Book", author="Test Author", isbn="FKTEST001", total_quantity=1, available_quantity=0)
    borrowing = Borrowing(book=book, borrower_name="Test User", borrower_room_number="101", borrower_hotel="Test Hotel")
    db_session.add_all([book, borrowing])
    db_session.commit()
    response = client.delete(f'/api/books/{book.id}', headers=auth_headers)
    assert response.status_code == 409

def test_delete_category_in_use_fails(client, db_session, auth_headers):
    """
    SCENARIO: Attempt to delete a category that is currently assigned to a book.
    GIVEN: A category and a book linked to it.
    WHEN: A DELETE request is sent for that category.
    THEN: Check the response is 409 Conflict, protecting data integrity.
    """
    category = Category(name="Category To Delete")
    book = Book(title="Book with Category", author="Test Author", isbn="FKTEST002", total_quantity=1, available_quantity=1, category=category)
    db_session.add_all([category, book])
    db_session.commit()
    
    response = client.delete(f'/api/categories/{category.id}', headers=auth_headers)
    
    assert response.status_code == 409
    data = response.get_json()
    assert "error" in data
    assert "Cannot delete category" in data["error"]


# --- 2. Return Negative Tests ---
def test_return_already_returned_book(client, db_session, auth_headers):
    """
    SCENARIO: Attempt to return a book that has already been returned.
    GIVEN: A borrowing record marked as is_returned=True.
    WHEN: A return request is sent for that borrowing ID.
    THEN: Check the response is 404 Not Found, as the service only finds active records.
    """
    book = Book(title="Returned Book", author="Test Author", isbn="NEGTEST001", total_quantity=1, available_quantity=1)
    borrowing = Borrowing(book=book, borrower_name="Test User", borrower_room_number="101", borrower_hotel="Test Hotel", is_returned=True)
    db_session.add_all([book, borrowing])
    db_session.commit()
    response = client.post(
        '/api/borrowings/return',
        data=json.dumps({"borrowing_id": borrowing.id}),
        content_type='application/json', 
        headers=auth_headers
    )
    assert response.status_code == 404


# --- 1. Concurrency Test ---
def test_borrow_concurrency(app, db_session, auth_headers):
    """
    SCENARIO: Two clients try to borrow the last available book simultaneously.
    GIVEN: A single book with available_quantity = 1.
    WHEN: Two concurrent borrow requests are made.
    THEN: Check that one request succeeds (201), one fails (409),
          and the book's final available quantity is 0.
    """
    book = Book(title="Concurrent Book", author="Test Author", isbn="CONCURRENCY001", total_quantity=1, available_quantity=1)
    db_session.add(book)
    db_session.commit()
    book_id = book.id
    results = []
    def borrow_task():
        with app.app_context():
            with app.test_client() as client:
                response = client.post(
                    '/api/borrowings/borrow',
                    data=json.dumps({
                        "book_id": book_id,
                        "borrower_name": "Concurrent User",
                        "borrower_email": "concurrent.user@example.com", 
                        "borrower_phone": "123-456-7890", 
                        "borrower_room_number": "C101",
                        "borrower_hotel": "Concurrent Hotel"
                    }),
                    content_type='application/json', 
                    headers=auth_headers
                )
                results.append(response.status_code)
    thread1 = threading.Thread(target=borrow_task)
    thread2 = threading.Thread(target=borrow_task)
    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()
    assert sorted(results) == [201, 409]
    # CORRECTED: Refresh the book object to get the latest state from the DB
    db_session.refresh(book)
    assert book.available_quantity == 0
    borrowing_records = db_session.query(Borrowing).filter_by(book_id=book_id).all()
    assert len(borrowing_records) == 1
