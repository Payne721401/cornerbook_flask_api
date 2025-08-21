# models/book.py
from extensions import db
from sqlalchemy.sql import func
from sqlalchemy import Index, CheckConstraint

class Book(db.Model):
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    isbn = db.Column(db.String(20), nullable=False, unique=True)
    image_url = db.Column(db.Text, nullable=True)
    total_quantity = db.Column(db.Integer, nullable=False, default=0)
    available_quantity = db.Column(db.Integer, nullable=False, default=0)
    
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id', ondelete='SET NULL'), nullable=True)
    
    created_at = db.Column(db.TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at = db.Column(db.TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    category = db.relationship('Category', back_populates='books')
    borrowings = db.relationship('Borrowing', back_populates='book', cascade="all, delete-orphan")

    # Table arguments for indexes and constraints
    __table_args__ = (
        CheckConstraint('available_quantity >= 0 AND available_quantity <= total_quantity', name='chk_available_quantity'),
        Index('idx_books_title', 'title'),
        Index('idx_books_author', 'author'),
        Index('idx_books_category_id', 'category_id'),
    )

    def to_dict(self):
        """Converts the model to a dictionary, including category name."""
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "isbn": self.isbn,
            "image_url": self.image_url,
            "total_quantity": self.total_quantity,
            "available_quantity": self.available_quantity,
            "category_id": self.category_id,
            "category_name": self.category.name if self.category else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
