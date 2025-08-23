# services/book_service.py
from extensions import db
from models.book import Book
from models.category import Category
from sqlalchemy import or_

def get_all_books_service(filters, page=1, per_page=50):
    """
    Service to retrieve a list of books with optional filters and pagination.
    If per_page is 0, all items will be returned without pagination.
    """
    query = db.session.query(Book).join(Category, Book.category_id == Category.id, isouter=True)

    if filters.get('search'):
        search_term = f"%{filters['search']}%"
        query = query.filter(
            or_(
                Book.title.ilike(search_term), 
                Book.author.ilike(search_term),
                Book.isbn.ilike(search_term)
            )
        )

    if filters.get('category'):
        query = query.filter(Category.name == filters['category'])

    if filters.get('available'):
        if filters['available'].lower() == 'true':
            query = query.filter(Book.available_quantity > 0)

    # Apply pagination or return all items if per_page is 0
    if per_page == 0:
        items = query.all()
        # Simulate a pagination object for consistency in return type
        class AllItemsPagination:
            def __init__(self, items):
                self.items = items
                self.total = len(items)
                self.pages = 1  # When all items are returned, it's effectively 1 page
                self.page = 1
                self.per_page = self.total # Per page is the actual total count
                self.has_next = False
                self.has_prev = False
                self.next_num = None
                self.prev_num = None

        return AllItemsPagination(items)

    else:
        pagination_obj = query.paginate(page=page, per_page=per_page, error_out=False)
        return pagination_obj
