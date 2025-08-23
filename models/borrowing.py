# models/borrowing.py
from extensions import db
from sqlalchemy.sql import func
from sqlalchemy import Index

class Borrowing(db.Model):
    __tablename__ = 'borrowings'

    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id', ondelete='RESTRICT'), nullable=False)
    borrower_name = db.Column(db.String(255), nullable=False)
    borrower_email = db.Column(db.String(255), nullable=True)
    borrower_phone = db.Column(db.String(20), nullable=True)
    borrower_room_number = db.Column(db.String(10), nullable=False)
    borrower_hotel = db.Column(db.String(255), nullable=False)
    borrowed_at = db.Column(db.TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    returned_at = db.Column(db.TIMESTAMP(timezone=True), nullable=True)
    is_returned = db.Column(db.Boolean, nullable=False, default=False)

    # Relationships
    book = db.relationship('Book', back_populates='borrowings')

    # Table arguments for indexes
    __table_args__ = (
        Index('idx_borrowings_book_id', 'book_id'),
        Index('idx_borrowings_is_returned', 'is_returned'),
        Index('idx_borrowings_borrower_room_number', 'borrower_room_number'),
        Index('idx_borrowings_borrowed_at', 'borrowed_at'),
    )

    def to_dict(self):
        """Converts the model to a dictionary."""
        return {
            "id": self.id,
            "book_id": self.book_id,
            "book_title": self.book.title if self.book else None,
            "borrower_name": self.borrower_name,
            "borrower_email": self.borrower_email,
            "borrower_phone": self.borrower_phone,
            "borrower_room_number": self.borrower_room_number,
            "borrower_hotel": self.borrower_hotel,
            "borrowed_at": self.borrowed_at.isoformat(),
            "returned_at": self.returned_at.isoformat() if self.returned_at else None,
            "is_returned": self.is_returned
        }
