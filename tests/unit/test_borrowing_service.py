# tests/unit/test_borrowing_service.py
import pytest
from services.borrowing_service import borrow_book_service, return_book_service
from models.book import Book
from models.borrowing import Borrowing
from unittest.mock import MagicMock
from datetime import datetime

def test_borrow_successful_logic(mocker):
    """
    Unit test for the borrow book service logic.
    It should decrease the book's available quantity and create a borrowing record.
    """
    mock_db_session = mocker.MagicMock()
    mock_book = Book(id=1, title="Testable", available_quantity=1)
    
    mock_db_session.query.return_value.filter_by.return_value.with_for_update.return_value.first.return_value = mock_book
    
    mocker.patch('services.borrowing_service.db.session', mock_db_session)
    
    data = {"book_id": 1, "borrower_name": "Unit Tester", "borrower_room_number": "U1", "borrower_hotel": "Test"}
    result, error = borrow_book_service(data)
    
    assert error is None
    assert result.book_id == 1
    assert mock_book.available_quantity == 0
    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()

def test_borrow_out_of_stock_logic(mocker):
    """
    Unit test for borrowing a book that is out of stock.
    It should return an error and not create a borrowing record.
    """
    mock_db_session = mocker.MagicMock()
    mock_book = Book(id=1, title="Empty Shelf", available_quantity=0)
    
    mock_db_session.query.return_value.filter_by.return_value.with_for_update.return_value.first.return_value = mock_book
    mocker.patch('services.borrowing_service.db.session', mock_db_session)
    
    data = {"book_id": 1, "borrower_name": "Late Comer", "borrower_room_number": "U2", "borrower_hotel": "Test"}
    result, error = borrow_book_service(data)
    
    assert result is None
    assert error == "Book is not available for borrowing"
    mock_db_session.commit.assert_not_called()

def test_return_successful_logic(mocker):
    """
    Unit test for the return book service logic.
    It should mark the record as returned and increase book quantity.
    """
    mock_db_session = mocker.MagicMock()
    mock_book = Book(id=1, title="To Return", total_quantity=2, available_quantity=0)
    mock_borrowing = Borrowing(id=1, book_id=1, is_returned=False, book=mock_book)

    # MODIFIED: A more precise mock is needed for the two separate queries.
    # We mock the final call in the chain, `first()`, to return different
    # values on consecutive calls, simulating the two queries in the service.
    mock_query = mocker.MagicMock()
    mock_first = mocker.MagicMock()
    mock_first.side_effect = [mock_borrowing, mock_book] # 1st call gets borrowing, 2nd gets book
    
    # Reconstruct the chain for the mock
    mock_query.filter_by.return_value.with_for_update.return_value.first = mock_first
    mock_db_session.query.return_value = mock_query

    # Mock datetime.utcnow to control the returned_at value for reliable assertion
    mock_now = datetime(2024, 1, 1, 12, 0, 0)
    mocker.patch('services.borrowing_service.datetime', mocker.MagicMock(utcnow=lambda: mock_now))
    mocker.patch('services.borrowing_service.db.session', mock_db_session)

    # Call the service with the borrowing_id directly
    result, error = return_book_service(1)

    assert error is None
    assert result.is_returned is True
    assert result.returned_at == mock_now
    assert mock_book.available_quantity == 1
    mock_db_session.commit.assert_called_once()
