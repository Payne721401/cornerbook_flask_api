# tests/conftest.py
import pytest
import os
from dotenv import load_dotenv

from app import create_app 
from extensions import db as _db
from config import Config
from models.borrowing import Borrowing
from models.book import Book
from models.category import Category

# Load environment variables from .env file to get credentials
load_dotenv()

# --- Custom Config for Testing ---
class TestingConfig(Config):
    """Configuration for testing with a local database."""
    TESTING = True
    
    # Construct the Test Database URL from existing .env variables
    DB_USER = os.environ.get('DB_USER')
    DB_PASSWORD = os.environ.get('DB_PASSWORD')
    DB_HOST = os.environ.get('DB_HOST')
    DB_PORT = os.environ.get('DB_PORT', 5432)
    DB_NAME = os.environ.get('DB_NAME') + '_test' if os.environ.get('DB_NAME') else 'test_db'

    SQLALCHEMY_DATABASE_URI = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    # Disable CSRF protection in tests
    WTF_CSRF_ENABLED = False
    
    # Get the real API Key from .env for testing protected endpoints
    API_KEY = os.environ.get("API_KEY")


# --- Pytest Fixtures ---
@pytest.fixture(scope='session')
def app():
    """Session-wide test `Flask` application."""
    os.environ['FLASK_ENV'] = 'testing'
    app = create_app(TestingConfig)
    
    with app.app_context():
        yield app

@pytest.fixture(scope='session')
def db(app):
    """Session-wide database setup and teardown."""
    with app.app_context():
        # Create all tables for the test database
        _db.create_all()
        yield _db
        # Drop all tables after the test session finishes
        _db.drop_all()

@pytest.fixture(scope='function')
def db_session(db):
    """
    Creates a new database session for each test function.
    Rolls back any changes after the test completes to ensure test isolation.
    """
    connection = db.engine.connect()
    transaction = connection.begin()
    
    session = db.session

    # Clean up all tables before each test to ensure isolation
    session.query(Borrowing).delete()
    session.query(Book).delete()
    session.query(Category).delete()
    session.commit()

    yield session

    session.remove()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope='function')
def client(app, db_session):
    """A test client for the app for each function."""
    return app.test_client()

@pytest.fixture(scope='function')
def auth_headers(app):
    """Fixture for creating authorization headers with the real API key."""
    api_key = app.config.get('API_KEY')
    if not api_key:
        pytest.fail("API_KEY not configured for testing in conftest.py.")
    return {"Api-Key": api_key}
