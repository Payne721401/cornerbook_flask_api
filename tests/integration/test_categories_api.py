import json
from models.category import Category
from models.book import Book
from extensions import db

def test_get_categories(client, db_session):
    """
    GIVEN 2 categories in the database
    WHEN a GET request is made to /api/categories/
    THEN check the response is 200 and contains the 2 categories.
    """
    db_session.add(Category(name="Fiction"))
    db_session.add(Category(name="Science"))
    db_session.commit()
    response = client.get('/api/categories/')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 2

def test_get_all_categories(client, db_session):
    """
    GIVEN multiple categories in the database
    WHEN a GET request is made to /api/categories/
    THEN the response should contain all categories.
    """
    categories = [Category(name="History"), Category(name="Biography"), Category(name="Fantasy")]
    db_session.add_all(categories)
    db_session.commit()
    response = client.get('/api/categories/')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 3
    assert {cat['name'] for cat in data} == {"History", "Biography", "Fantasy"}

def test_post_category_success(client, db_session, auth_headers):
    """
    GIVEN a valid category payload
    WHEN a POST request is made to /api/categories/
    THEN check the response is 201 and the category is in the database.
    """
    category_data = {"name": "History"}
    response = client.post('/api/categories/', data=json.dumps(category_data), content_type='application/json', headers=auth_headers)
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['name'] == category_data['name']
    assert db_session.query(Category).filter_by(name="History").first() is not None

def test_post_category_duplicate(client, db_session, auth_headers):
    """
    GIVEN a category that already exists in the database
    WHEN a POST request is made with the same category name
    THEN check the response is 409 Conflict.
    """
    db_session.add(Category(name="Travel"))
    db_session.commit()
    category_data = {"name": "Travel"}
    response = client.post('/api/categories/', data=json.dumps(category_data), content_type='application/json', headers=auth_headers)
    assert response.status_code == 409

def test_patch_category_success(client, db_session, auth_headers):
    """
    GIVEN an existing category
    WHEN a PATCH request is made to update the category's name
    THEN check the response is 200 and the name is updated in the database.
    """
    category = Category(name="Self-Help")
    db_session.add(category)
    db_session.commit()
    update_data = {"name": "Self-Improvement"}
    response = client.patch(f'/api/categories/{category.id}', data=json.dumps(update_data), content_type='application/json', headers=auth_headers)
    assert response.status_code == 200
    # MODIFIED: Use modern db.session.get(Model, id) syntax
    updated_category = db_session.get(Category, category.id)
    assert updated_category.name == "Self-Improvement"

def test_delete_category_success(client, db_session, auth_headers):
    """
    GIVEN an existing category not tied to any books
    WHEN a DELETE request is made
    THEN check the response is 204 and the category is removed from the database.
    """
    category = Category(name="Biography")
    db_session.add(category)
    db_session.commit()
    response = client.delete(f'/api/categories/{category.id}', headers=auth_headers)
    assert response.status_code == 204
    # MODIFIED: Use modern db.session.get(Model, id) syntax
    assert db.session.get(Category, category.id) is None

def test_delete_category_in_use_fails(client, db_session, auth_headers):
    """
    SCENARIO: Attempt to delete a category that is currently assigned to a book.
    GIVEN: A category and a book linked to it.
    WHEN: A DELETE request is sent for that category.
    THEN: The request should fail with a 409 Conflict status.
    """
    # 1. Setup: Create a category and a book using it
    category = Category(name="Category In Use")
    db_session.add(category)
    db_session.commit() # Commit to get the category.id

    book = Book(
        title="Book Using Category",
        author="Test Author",
        isbn="978-in-use",
        total_quantity=1,
        available_quantity=1,
        category_id=category.id
    )
    db_session.add(book)
    db_session.commit()

    # 2. Action: Attempt to delete the category
    response = client.delete(f'/api/categories/{category.id}', headers=auth_headers)

    # 3. Assertion: Check for 409 Conflict and error message
    assert response.status_code == 409
    data = json.loads(response.data)
    assert "error" in data
    assert "Cannot delete category. It is currently in use" in data["error"]

    # 4. Verify that the category was NOT deleted
    category_in_db = db_session.get(Category, category.id)
    assert category_in_db is not None
