import json
import pytest
from models.book import Book
from models.category import Category
from models.borrowing import Borrowing

# --- Fixtures for Auth Tests ---

@pytest.fixture(scope="function")
def book_for_auth_tests(db_session):
    """Provides a book to be used in PATCH and DELETE auth tests."""
    # This local cleanup is kept as per original file structure.
    db_session.query(Borrowing).delete()
    db_session.query(Book).delete()
    db_session.query(Category).delete()
    db_session.commit()

    category = Category(name="Auth Test Category")
    db_session.add(category)
    db_session.commit()
    book = Book(
        title="Auth Test Book",
        author="Tester",
        isbn="auth-12345",
        total_quantity=1,
        available_quantity=1,
        category_id=category.id
    )
    db_session.add(book)
    db_session.commit()
    return book

# --- API Key Authentication Tests ---

INVALID_API_KEY = "invalid-key"

# --- Positive Tests ---

@pytest.mark.skip(reason="Endpoint refactored for batch creation. Test preserved for reference.")
def test_post_protected_endpoint_with_valid_api_key(client, db_session, auth_headers):
    category = Category(name="Fiction For Auth")
    db_session.add(category)
    db_session.commit()
    book_data = {
        "title": "A New Book", "author": "An Author",
        "isbn": "9876543210", "total_quantity": 1, "category_id": category.id
    }
    response = client.post('/api/books/', data=json.dumps(book_data), content_type='application/json', headers=auth_headers)
    assert response.status_code == 201

def test_patch_protected_endpoint_with_valid_api_key(client, book_for_auth_tests, auth_headers):
    update_data = {"total_quantity": 10}
    response = client.patch(f'/api/books/{book_for_auth_tests.id}', data=json.dumps(update_data), content_type='application/json', headers=auth_headers)
    assert response.status_code == 200

def test_delete_protected_endpoint_with_valid_api_key(client, book_for_auth_tests, auth_headers):
    response = client.delete(f'/api/books/{book_for_auth_tests.id}', headers=auth_headers)
    assert response.status_code == 204  # MODIFIED: Correct status code for successful deletion is 204.

def test_get_unprotected_endpoint_without_api_key(client):
    response = client.get('/api/books/')
    assert response.status_code == 200

# --- Negative Tests ---

@pytest.mark.skip(reason="Endpoint refactored for batch creation. Test preserved for reference.")
def test_post_protected_endpoint_without_api_key(client):
    book_data = {"title": "No Key Book", "author": "No Key", "isbn": "nokey-123", "total_quantity": 1, "category_id": 1}
    response = client.post('/api/books/', data=json.dumps(book_data), content_type='application/json')
    assert response.status_code == 401
    data = json.loads(response.data)
    # MODIFIED: Assert the exact error message from the API.
    assert data['error'] == 'Unauthorized: Invalid or missing API Key'

@pytest.mark.skip(reason="Endpoint refactored for batch creation. Test preserved for reference.")
def test_post_protected_endpoint_with_invalid_api_key(client):
    book_data = {"title": "Invalid Key Book", "author": "Invalid", "isbn": "invalid-123", "total_quantity": 1, "category_id": 1}
    headers = {"Api-Key": INVALID_API_KEY}
    response = client.post('/api/books/', data=json.dumps(book_data), content_type='application/json', headers=headers)
    assert response.status_code == 401
    data = json.loads(response.data)
    # MODIFIED: Assert the exact error message from the API.
    assert data['error'] == 'Unauthorized: Invalid or missing API Key'

def test_patch_protected_endpoint_without_api_key(client, book_for_auth_tests):
    update_data = {"total_quantity": 5}
    response = client.patch(f'/api/books/{book_for_auth_tests.id}', data=json.dumps(update_data), content_type='application/json')
    assert response.status_code == 401

def test_patch_protected_endpoint_with_invalid_api_key(client, book_for_auth_tests):
    update_data = {"total_quantity": 5}
    headers = {"Api-Key": INVALID_API_KEY}
    response = client.patch(f'/api/books/{book_for_auth_tests.id}', data=json.dumps(update_data), content_type='application/json', headers=headers)
    assert response.status_code == 401

def test_delete_protected_endpoint_without_api_key(client, book_for_auth_tests):
    response = client.delete(f'/api/books/{book_for_auth_tests.id}')
    assert response.status_code == 401

def test_delete_protected_endpoint_with_invalid_api_key(client, book_for_auth_tests):
    headers = {"Api-Key": INVALID_API_KEY}
    response = client.delete(f'/api/books/{book_for_auth_tests.id}', headers=headers)
    assert response.status_code == 401

# --- NEW: BATCH BOOK CREATION AUTH TESTS ---

def test_batch_post_protected_endpoint_with_valid_api_key(client, db_session, auth_headers):
    """Tests that a batch POST with a valid API key succeeds."""
    category = Category(name="Fiction For Auth Batch")
    db_session.add(category)
    db_session.commit()
    book_data = {
        "title": "A New Batch Book", "author": "An Author",
        "isbn": "9876543210-batch", "total_quantity": 1, "category_id": category.id
    }
    payload = {"books": [book_data]}
    response = client.post('/api/books/', data=json.dumps(payload), content_type='application/json', headers=auth_headers)
    assert response.status_code == 201

def test_batch_post_protected_endpoint_without_api_key(client, db_session):
    """Tests that a batch POST without an API key fails."""
    category = Category(name="No Key Category Batch")
    db_session.add(category)
    db_session.commit()
    book_data = {"title": "No Key Book Batch", "author": "No Key", "isbn": "nokey-123-batch", "total_quantity": 1, "category_id": category.id}
    payload = {"books": [book_data]}
    response = client.post('/api/books/', data=json.dumps(payload), content_type='application/json')
    assert response.status_code == 401
    data = json.loads(response.data)
    assert data['error'] == 'Unauthorized: Invalid or missing API Key'

def test_batch_post_protected_endpoint_with_invalid_api_key(client, db_session):
    """Tests that a batch POST with an invalid API key fails."""
    category = Category(name="Invalid Key Category Batch")
    db_session.add(category)
    db_session.commit()
    book_data = {"title": "Invalid Key Book Batch", "author": "Invalid", "isbn": "invalid-123-batch", "total_quantity": 1, "category_id": category.id}
    payload = {"books": [book_data]}
    headers = {"Api-Key": INVALID_API_KEY}
    response = client.post('/api/books/', data=json.dumps(payload), content_type='application/json', headers=headers)
    assert response.status_code == 401
    data = json.loads(response.data)
    assert data['error'] == 'Unauthorized: Invalid or missing API Key'
