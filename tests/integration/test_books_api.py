import json
import pytest
from models.book import Book
from models.category import Category
from models.borrowing import Borrowing
from extensions import db

@pytest.mark.skip(reason="Endpoint refactored for batch creation. Test preserved for reference.")
def test_post_book_success(client, db_session, auth_headers):
    """
    GIVEN a valid book payload
    WHEN a POST request is made to /api/books/
    THEN check the response is 201 and the book is in the database.
    """
    category = Category(name="Fiction")
    db_session.add(category)
    db_session.commit()
    book_data = {
        "title": "The Great Gatsby", "author": "F. Scott Fitzgerald",
        "isbn": "9780743273565", "total_quantity": 3, "category_id": category.id
    }
    response = client.post('/api/books/', data=json.dumps(book_data), content_type='application/json', headers=auth_headers)
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['title'] == book_data['title']
    book_in_db = db_session.query(Book).filter_by(isbn=book_data['isbn']).first()
    assert book_in_db is not None

@pytest.mark.skip(reason="Endpoint refactored for batch creation. Test preserved for reference.")
def test_post_book_invalid_data(client, db_session, auth_headers):
    """
    GIVEN an invalid book payload (missing title)
    WHEN a POST request is made to /api/books/
    THEN check the response is 400 Bad Request and contains validation details.
    """
    invalid_data = {
        "author": "F. Scott Fitzgerald", "isbn": "9780743273565", "total_quantity": 3
    }
    response = client.post('/api/books/', data=json.dumps(invalid_data), content_type='application/json', headers=auth_headers)
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'validation_error' in data
    body_errors = data['validation_error']['body_params']
    assert len(body_errors) == 2
    assert body_errors[0]['msg'] == 'Field required'
    assert body_errors[0]['loc'] == ['title']

def test_get_books_filtered(client, db_session):
    """
    GIVEN several books in the database
    WHEN a GET request is made to /api/books/ with filters
    THEN check that only the correct books are returned.
    """
    # CORRECTED: Delete dependent records first to avoid foreign key violations
    db_session.query(Borrowing).delete()
    db_session.query(Book).delete()
    db_session.query(Category).delete()
    db_session.commit()

    cat1 = Category(name="Sci-Fi")
    cat2 = Category(name="Fantasy")
    db_session.add_all([cat1, cat2])
    db_session.commit()
    book1 = Book(title="Dune", author="Frank Herbert", isbn="111", total_quantity=2, available_quantity=2, category_id=cat1.id)
    book2 = Book(title="Foundation", author="Isaac Asimov", isbn="222", total_quantity=3, available_quantity=0, category_id=cat1.id)
    book3 = Book(title="The Hobbit", author="J.R.R. Tolkien", isbn="333", total_quantity=1, available_quantity=1, category_id=cat2.id)
    db_session.add_all([book1, book2, book3])
    db_session.commit()
    response = client.get('/api/books/?category=Sci-Fi')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data['books']) == 2
    response = client.get('/api/books/?available=true')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data['books']) == 2
    response = client.get('/api/books/?search=Herbert')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data['books']) == 1
    assert data['books'][0]['title'] == "Dune"

@pytest.mark.skip(reason="Endpoint refactored for batch creation. Test preserved for reference.")
def test_post_book_invalid_data_details(client, db_session, auth_headers):
    """
    GIVEN an invalid book payload (missing multiple required fields)
    WHEN a POST request is made to /api/books/
    THEN check the response is 400 Bad Request and contains precise validation details.
    """
    invalid_data = {"author": "Missing Everything"}
    response = client.post('/api/books/', data=json.dumps(invalid_data), content_type='application/json', headers=auth_headers)
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'validation_error' in data
    assert any(e['loc'] == ['title'] and 'Field required' in e['msg'] for e in data['validation_error']['body_params'])
    # assert 'details' in data
    # details = data['details']
    
    # 預期至少 'title', 'isbn', 'total_quantity', 'category_id' 字段缺失
    # 根據 pydantic_models.py 中 BookCreate 模型的定義
    validation_errors = data['validation_error']['body_params']
    required_fields_to_check = ['title', 'isbn', 'total_quantity', 'category_id']
    
    for field in required_fields_to_check:
        assert any(d['loc'] == [field] and 'Field required' in d['msg'] for d in validation_errors), \
            f"Expected validation error for missing field: {field}"

@pytest.mark.skip(reason="Endpoint refactored for batch creation. Test preserved for reference.")
def test_post_book_non_existent_category_id(client, db_session, auth_headers):
    """
    GIVEN a book payload with a non-existent category_id
    WHEN a POST request is made to /api/books/
    THEN check the response is 404 Not Found, as the category cannot be found for association.
    """
    # 確保使用的 ID 絕對不會是真實存在的 ID (db_session fixture 會清理，所以這個 ID 不太可能存在)
    non_existent_category_id = 99999

    book_data = {
        "title": "Book with Bad Category", "author": "Author X",
        "isbn": "9780000000000", "total_quantity": 1, "category_id": non_existent_category_id
    }
    response = client.post('/api/books/', data=json.dumps(book_data), content_type='application/json', headers=auth_headers)
    
    # 根據 API 實現 (services/book_service.py)，如果 category_id 不存在，會返回 "Category not found" 錯誤字串
    # 路由層 (routes/books.py) 會將其轉化為 404 狀態碼。
    assert response.status_code == 404
    data = json.loads(response.data)
    assert data['error'] == f"Category with id {non_existent_category_id} not found."

def test_patch_book_increase_total_quantity(client, db_session, auth_headers):
    """
    GIVEN a book with initial total_quantity and available_quantity
    WHEN total_quantity is increased
    THEN available_quantity should increase by the same amount.
    """
    category = Category(name="Test Category for Qty")
    book = Book(title="Book for Qty Test", author="Qty Author", isbn="QTY001", total_quantity=5, available_quantity=3, category=category)
    db_session.add_all([category, book])
    db_session.commit()
    book_id = book.id

    update_data = {"total_quantity": 8} # Increase by 3
    response = client.patch(f'/api/books/{book_id}', data=json.dumps(update_data), content_type='application/json', headers=auth_headers)
    assert response.status_code == 200

    updated_book = db.session.get(Book, book_id)
    assert updated_book.total_quantity == 8
    assert updated_book.available_quantity == 6 # 3 (original available) + 3 (increase)

def test_patch_book_decrease_total_quantity_legal(client, db_session, auth_headers):
    """
    GIVEN a book with initial total_quantity and available_quantity
    WHEN total_quantity is decreased legally (not below borrowed count)
    THEN available_quantity should decrease by the same amount.
    """
    category = Category(name="Test Category for Qty Dec")
    # 10 total, 4 available -> 6 borrowed
    book = Book(title="Book for Qty Dec Test", author="Dec Author", isbn="QTY002", total_quantity=10, available_quantity=4, category=category)
    db_session.add_all([category, book])
    db_session.commit()
    book_id = book.id

    update_data = {"total_quantity": 8} # Decrease by 2 (new total 8, 6 borrowed -> 2 available)
    response = client.patch(f'/api/books/{book_id}', data=json.dumps(update_data), content_type='application/json', headers=auth_headers)
    assert response.status_code == 200

    updated_book = db.session.get(Book, book_id)
    assert updated_book.total_quantity == 8
    assert updated_book.available_quantity == 2 # 4 (original available) - 2 (decrease)

def test_patch_book_decrease_total_quantity_illegal(client, db_session, auth_headers):
    """
    GIVEN a book with initial total_quantity and available_quantity
    WHEN total_quantity is decreased illegally (below borrowed count)
    THEN the request should fail with 409 Conflict.
    """
    category = Category(name="Test Category for Qty Illegal")
    # 5 total, 2 available -> 3 borrowed
    book = Book(title="Book for Qty Illegal Test", author="Illegal Author", isbn="QTY003", total_quantity=5, available_quantity=2, category=category)
    db_session.add_all([category, book])
    db_session.commit()
    book_id = book.id

    update_data = {"total_quantity": 2} # Attempt to decrease below 3 borrowed
    response = client.patch(f'/api/books/{book_id}', data=json.dumps(update_data), content_type='application/json', headers=auth_headers)
    assert response.status_code == 409
    data = json.loads(response.data)
    assert "Cannot reduce total quantity" in data['error']


def test_patch_book_duplicate_isbn(client, db_session, auth_headers):
    """
    GIVEN two books, A and B
    WHEN book A tries to update its ISBN to match book B's ISBN
    THEN the request should fail with 409 Conflict.
    """
    category = Category(name="Test Category for ISBN")
    book_a = Book(title="Book A", author="Author A", isbn="978-0-123-A", total_quantity=1, available_quantity=1, category=category)
    book_b = Book(title="Book B", author="Author B", isbn="978-0-123-B", total_quantity=1, available_quantity=1, category=category)
    db_session.add_all([category, book_a, book_b])
    db_session.commit()
    book_a_id = book_a.id

    update_data = {"isbn": "978-0-123-B"} # Try to set A's ISBN to B's
    response = client.patch(f'/api/books/{book_a_id}', data=json.dumps(update_data), content_type='application/json', headers=auth_headers)
    assert response.status_code == 409
    data = json.loads(response.data)
    assert "ISBN might already exist" in data['error']


# --- NEW: BATCH BOOK CREATION TESTS ---

def test_create_single_book_in_batch_successfully(client, db_session, auth_headers):
    """
    GIVEN a valid book payload within a list
    WHEN a POST request is made to /api/books/
    THEN check the response is 201 and the book is in the database.
    """
    category = Category(name="Fiction Batch")
    db_session.add(category)
    db_session.commit()
    
    book_data = {
        "title": "The Great Gatsby Batch", "author": "F. Scott Fitzgerald",
        "isbn": "9780743273565BATCH", "total_quantity": 3, "category_id": category.id
    }
    payload = {"books": [book_data]}

    response = client.post('/api/books/', data=json.dumps(payload), content_type='application/json', headers=auth_headers)
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]['title'] == book_data['title']
    
    book_in_db = db_session.query(Book).filter_by(isbn=book_data['isbn']).first()
    assert book_in_db is not None

def test_create_multiple_books_successfully(client, db_session, auth_headers):
    """
    GIVEN a valid payload with multiple books
    WHEN a POST request is made to /api/books/
    THEN check the response is 201 and all books are in the database.
    """
    category = Category(name="Bulk Category")
    db_session.add(category)
    db_session.commit()

    payload = {
        "books": [
            {
                "title": "Bulk Book 1", "author": "Author A", "isbn": "1234567890123",
                "total_quantity": 10, "category_id": category.id
            },
            {
                "title": "Bulk Book 2", "author": "Author B", "isbn": "9876543210987",
                "total_quantity": 5, "category_id": category.id
            }
        ]
    }

    response = client.post('/api/books/', data=json.dumps(payload), content_type='application/json', headers=auth_headers)

    assert response.status_code == 201
    response_data = response.get_json()
    assert isinstance(response_data, list)
    assert len(response_data) == 2
    assert response_data[0]['title'] == "Bulk Book 1"
    
    assert db_session.query(Book).count() == 2

def test_create_books_with_duplicate_isbn_in_request(client, db_session, auth_headers):
    """
    GIVEN a batch payload with a duplicate ISBN inside the request list
    WHEN a POST request is made
    THEN check for a 409 Conflict and no books are created.
    """
    category = Category(name="Error Test Category")
    db_session.add(category)
    db_session.commit()

    duplicate_isbn = "1112223334445"
    payload = {
        "books": [
            {"title": "Book A", "author": "Author X", "isbn": duplicate_isbn, "total_quantity": 1, "category_id": category.id},
            {"title": "Book C", "author": "Author Z", "isbn": duplicate_isbn, "total_quantity": 1, "category_id": category.id}
        ]
    }

    response = client.post('/api/books/', data=json.dumps(payload), content_type='application/json', headers=auth_headers)

    assert response.status_code == 409
    response_data = response.get_json()
    assert "error" in response_data
    assert f"Duplicate ISBN {duplicate_isbn} found in request" in response_data["error"]
    
    assert db_session.query(Book).count() == 0

def test_create_books_with_isbn_already_in_db(client, db_session, auth_headers):
    """
    GIVEN a batch payload where one ISBN already exists in the database
    WHEN a POST request is made
    THEN check for a 409 Conflict and no new books are created.
    """
    category = Category(name="Pre-existing Category")
    existing_isbn = "1231231231231"
    existing_book = Book(title="Pre-existing Book", author="Old Author", isbn=existing_isbn, total_quantity=1, available_quantity=1, category=category)
    db_session.add_all([category, existing_book])
    db_session.commit()

    payload = {
        "books": [
            {"title": "New Book 1", "author": "New Author A", "isbn": "9998887776665", "total_quantity": 1, "category_id": category.id},
            {"title": "New Book 2 (Conflict)", "author": "New Author B", "isbn": existing_isbn, "total_quantity": 1, "category_id": category.id}
        ]
    }

    response = client.post('/api/books/', data=json.dumps(payload), content_type='application/json', headers=auth_headers)

    assert response.status_code == 409
    response_data = response.get_json()
    assert "error" in response_data
    assert f"ISBN {existing_isbn} already exists" in response_data["error"]

    assert db_session.query(Book).count() == 1

def test_create_books_with_invalid_category_id_in_batch(client, db_session, auth_headers):
    """
    GIVEN a batch payload where one book has a non-existent category_id
    WHEN a POST request is made
    THEN check for a 404 Not Found and no books are created.
    """
    category = Category(name="Valid Category Batch")
    db_session.add(category)
    db_session.commit()
    invalid_category_id = 99999

    payload = {
        "books": [
            {"title": "Valid Book", "author": "Good Author", "isbn": "1234567890000BATCH", "total_quantity": 1, "category_id": category.id},
            {"title": "Invalid Book", "author": "Bad Author", "isbn": "0009876543211BATCH", "total_quantity": 1, "category_id": invalid_category_id}
        ]
    }

    response = client.post('/api/books/', data=json.dumps(payload), content_type='application/json', headers=auth_headers)

    assert response.status_code == 404
    response_data = response.get_json()
    assert "error" in response_data
    assert f"Category with id {invalid_category_id} not found" in response_data["error"]
    
    # Check that no books were created, including the valid one.
    assert db_session.query(Book).filter(Book.isbn.like('%BATCH')).count() == 0

def test_create_books_with_pydantic_error_in_batch(client, auth_headers, db_session):
    """
    GIVEN an invalid book payload in a batch (e.g., missing title)
    WHEN a POST request is made
    THEN check for a 400 Bad Request with validation details.
    """
    category = Category(name="Pydantic Test Category")
    db_session.add(category)
    db_session.commit()

    invalid_book_data = {
        "author": "F. Scott Fitzgerald", "isbn": "9780743273565PYDANTIC", "total_quantity": 3, "category_id": category.id
    }
    payload = {"books": [invalid_book_data]}
    
    response = client.post('/api/books/', data=json.dumps(payload), content_type='application/json', headers=auth_headers)
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'validation_error' in data
    body_errors = data['validation_error']['body_params']
    assert body_errors[0]['loc'] == ['books', 0, 'title']
    assert body_errors[0]['msg'] == 'Field required'

def test_create_books_with_empty_list(client, auth_headers):
    """
    GIVEN a payload with an empty list of books
    WHEN a POST request is made
    THEN check for a 400 Bad Request.
    """
    payload = {"books": []}
    response = client.post('/api/books/', data=json.dumps(payload), content_type='application/json', headers=auth_headers)
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'validation_error' in data
    assert "List should have at least 1 item" in data['validation_error']['body_params'][0]['msg']
