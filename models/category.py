# models/category.py
from app import db

class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    
    # Relationship to books
    books = db.relationship('Book', back_populates='category')

    def to_dict(self):
        """Converts the model to a dictionary."""
        return {
            "id": self.id,
            "name": self.name
        }
