# routes/categories.py
from flask import Blueprint, request, jsonify
from app import db
from models.category import Category
from routes.pydantic_models import CategoryCreate, CategoryUpdate
from flask_pydantic import validate

categories_bp = Blueprint('categories_bp', __name__)

@categories_bp.route('/', methods=['POST'])
@validate()
def create_category(body: CategoryCreate):
    """Create a new category."""
    if db.session.query(Category).filter_by(name=body.name).first():
        return jsonify({"error": "Category with this name already exists"}), 409
    
    new_category = Category(name=body.name)
    db.session.add(new_category)
    db.session.commit()
    return jsonify(new_category.to_dict()), 201

@categories_bp.route('/', methods=['GET'])
def get_categories():
    """Get a list of all categories."""
    categories = db.session.query(Category).all()
    return jsonify([category.to_dict() for category in categories]), 200

@categories_bp.route('/<int:id>', methods=['GET'])
def get_category(id):
    """Get a single category by ID."""
    category = db.session.get(Category, id) # UPDATED
    if not category:
        return jsonify({"error": "Category not found"}), 404
    return jsonify(category.to_dict()), 200

@categories_bp.route('/<int:id>', methods=['PATCH'])
@validate()
def update_category(id, body: CategoryUpdate):
    """Update a category's name."""
    category = db.session.get(Category, id) # UPDATED
    if not category:
        return jsonify({"error": "Category not found"}), 404

    existing_category = db.session.query(Category).filter(Category.name == body.name, Category.id != id).first()
    if existing_category:
        return jsonify({"error": "Category name already in use"}), 409

    category.name = body.name
    db.session.commit()
    return jsonify(category.to_dict()), 200

@categories_bp.route('/<int:id>', methods=['DELETE'])
def delete_category(id):
    """Delete a category."""
    category = db.session.get(Category, id) # UPDATED
    if not category:
        return jsonify({"error": "Category not found"}), 404
    
    db.session.delete(category)
    db.session.commit()
    return '', 204
