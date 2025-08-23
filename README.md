# Hotel Short-Term Book Lending System - Backend API

## Project Overview

This project provides the backend RESTful API for a hotel's short-term book lending system. It is designed to be the single source of truth for managing book inventory, categories, and borrowing records. The API is built with Python, Flask, and SQLAlchemy, following a structured and scalable architecture and RESTful best practices.

---

## Getting Started & Local Development

Follow these steps to set up and run the project on your local development machine.

### 1. Prerequisites

- Python 3.8+
- PostgreSQL Database
- `git` for version control
- Docker (optional, if using Testcontainers for testing)

### 2. Setup

**Clone the repository:**
```bash
git clone <your-repository-url>
cd <project-directory>
```

**Create and activate a Python virtual environment:**
```bash
python -m venv .venv
source .venv/bin/activate
```

**Install dependencies:**
```bash
pip install -r requirements.txt
```

**Configure Environment Variables:**
Create a `.env` file in the project root. You can copy the `.env.example` if it exists, or create a new one. Ensure it contains the correct credentials for your **local** PostgreSQL database.

**Initialize Local Database (First time setup or full reset):**
Use the provided script to initialize/reset your local development and test databases.
```bash
chmod +x init_db.sh # Only needed once
./init_db.sh
```

### 3. Running the Development Server

To start the local development server:
```bash
python dev_server.py
```
The API will be available at `http://127.0.0.1:5001`.

### 4. Running Tests

To run the comprehensive test suite:
```bash
pytest -v
```

---

## API Endpoint Documentation

**Base URL**: `http://127.0.0.1:5001/api`

All endpoints are prefixed with `/api`. The API returns data in JSON format and follows RESTful conventions (e.g., no trailing slashes on collection endpoints).

### General Error Response Format
Errors are returned in a standardized JSON format:
```json
{
  "error": "A descriptive error message.",
  "details": [ /* Optional: Specific validation error details from Pydantic */ ]
}
```

### Authentication
Endpoints that modify data (POST, PATCH, DELETE) require an API Key. Include the API Key in the `Api-Key` HTTP header.
**Example**: `-H "Api-Key: YOUR_API_KEY"`

### Logging Configuration

Logging is configured via `config.py` and initialized in `app.py`. In non-debug (e.g., production) environments, logs will be written to a file.

- **`LOG_FILE`**: Path to the log file (e.g., `logs/app.log`). Configured via environment variable or `config.py`.
- **`LOG_LEVEL`**: Minimum logging level (e.g., `INFO`, `WARNING`, `ERROR`, `CRITICAL`). Configured via environment variable or `config.py`.
- **`LOG_TO_STDOUT`**: Boolean, `True` to also log to standard output (console). Configured via environment variable or `config.py`.

---

### **Category Management (`/api/categories`)**

#### **1. Create a new category**
- **Endpoint**: `POST /api/categories`
- **Description**: Adds a new book category.
- **Request Body**:
  - `name` (string, required): The name of the category. Must be unique.
- **Body Example**: `{"name": "Science Fiction"}`
- **`curl` Example**:
  ```bash
  curl -X POST -H "Content-Type: application/json" \
  -H "Api-Key: YOUR_API_KEY" \
  -d '{"name": "Science Fiction"}' \
  http://127.0.0.1:5001/api/categories
  ```
- **Success Response (201)**: `{"id": 1, "name": "Science Fiction"}`

#### **2. Get all categories**
- **Endpoint**: `GET /api/categories`
- **Description**: Retrieves a list of all categories.
- **Parameters**: None.
- **`curl` Example**:
  ```bash
  curl http://127.0.0.1:5001/api/categories
  ```
- **Success Response (200)**: `[{"id": 1, "name": "Science Fiction"}, {"id": 2, "name": "Classic Literature"}]`

#### **3. Get a single category**
- **Endpoint**: `GET /api/categories/<id>`
- **Description**: Retrieves a single category by its ID.
- **Path Parameters**:
  - `id` (integer, required): The unique identifier of the category.
- **`curl` Example** (for category with ID 1):
  ```bash
  curl http://127.0.0.1:5001/api/categories/1
  ```
- **Success Response (200)**: `{"id": 1, "name": "Science Fiction"}`

#### **4. Update a category**
- **Endpoint**: `PATCH /api/categories/<id>`
- **Description**: Updates an existing category's name.
- **Path Parameters**:
  - `id` (integer, required): The unique identifier of the category to update.
- **Request Body**:
  - `name` (string, required): The new name for the category. Must be unique.
- **Body Example**: `{"name": "Sci-Fi"}`
- **`curl` Example** (updates category with ID 1):
  ```bash
  curl -X PATCH -H "Content-Type: application/json" \
  -H "Api-Key: YOUR_API_KEY" \
  -d '{"name": "Sci-Fi"}' \
  http://127.0.0.1:5001/api/categories/1
  ```
- **Success Response (200)**: `{"id": 1, "name": "Sci-Fi"}`

#### **5. Delete a category**
- **Endpoint**: `DELETE /api/categories/<id>`
- **Description**: Deletes a category by its ID.
- **Path Parameters**:
  - `id` (integer, required): The unique identifier of the category to delete.
- **`curl` Example** (deletes category with ID 1):
  ```bash
  curl -X DELETE -H "Api-Key: YOUR_API_KEY" \
  http://127.0.0.1:5001/api/categories/1
  ```
- **Success Response (204)**: No content.

---

### **Book Management (`/api/books`)**

#### **1. Add a new book**
- **Endpoint**: `POST /api/books`
- **Description**: Adds a new book to the inventory.
- **Request Body**:
  - `title` (string, required): The title of the book.
  - `author` (string, required): The author of the book.
  - `isbn` (string, required): The ISBN of the book. Must be unique.
  - `total_quantity` (integer, required): The total number of copies of this book.
  - `category_id` (integer, required): The ID of the category this book belongs to.
  - `image_url` (string, optional): A URL for the book's cover image.
- **Body Example**:
  ```json
  {
    "title": "Dune",
    "author": "Frank Herbert",
    "isbn": "9780441013593",
    "total_quantity": 5,
    "category_id": 1,
    "image_url": "http://example.com/dune.jpg"
  }
  ```
- **`curl` Example**:
  ```bash
  curl -X POST -H "Content-Type: application/json" \
  -H "Api-Key: YOUR_API_KEY" \
  -d '{"title": "Dune", "author": "Frank Herbert", "isbn": "9780441013593", "total_quantity": 5, "category_id": 1}' \
  http://127.0.0.1:5001/api/books
  ```
- **Success Response (201)**: The full book object.

#### 2. Get books with filtering
- **Endpoint**: `GET /api/books`
- **Description**: Retrieves a list of books, with optional query parameters for filtering and pagination.
- **Query Parameters**:
  - `search` (string, optional): Fuzzy search on the book's `title`, `author`, or `isbn`.
  - `category` (string, optional): Filter by the exact category name (e.g., "Sci-Fi").
  - `available` (boolean, optional): Set to `true` to filter for books with `available_quantity > 0`.
  - `page` (integer, optional): Page number for pagination. Defaults to 1.
  - `per_page` (integer, optional): Number of items per page for pagination. Defaults to 50. Set to `0` to retrieve all items without pagination.
- **`curl` Examples**:
  ```bash
  # Get all books (paginated with defaults)
  curl http://127.0.0.1:5001/api/books

  # Get books on page 2, 10 per page
  curl "http://127.0.0.1:5001/api/books?page=2&per_page=10"

  # Fuzzy search by book title
  curl "http://127.0.0.1:5001/api/books?search=Dune"

  # Get all records without pagination
  curl "http://127.0.0.1:5001/api/books?per_page=0"
  ```
- **Success Response (200)**: 
  ```json
  {
    "books": [
      {
        "id": 1,
        "title": "Dune",
        "author": "Frank Herbert",
        "isbn": "9780441013593",
        "total_quantity": 5,
        "available_quantity": 5,
        "category_id": 1,
        "image_url": "http://example.com/dune.jpg"
      }
    ],
    "pagination": {
      "total": 100,
      "pages": 10,
      "page": 2,
      "per_page": 10,
      "has_next": true,
      "has_prev": true,
      "next_num": 3,
      "prev_num": 1
    }
  }
  ```

#### **3. Get a single book**
- **Endpoint**: `GET /api/books/<id>`
- **Description**: Retrieves a single book by its ID.
- **Path Parameters**:
  - `id` (integer, required): The unique identifier of the book.
- **`curl` Example** (for book with ID 1):
  ```bash
  curl http://127.0.0.1:5001/api/books/1
  ```
- **Success Response (200)**: `{"book": {...}}`

#### **4. Update a book**
- **Endpoint**: `PATCH /api/books/<id>`
- **Description**: Partially updates a book's details. Only include the fields you want to change.
- **Path Parameters**:
  - `id` (integer, required): The unique identifier of the book to update.
- **Request Body** (all fields are optional):
  - `title` (string): The new title.
  - `author` (string): The new author.
  - `isbn` (string): The new ISBN. Must be unique.
  - `total_quantity` (integer): The new total quantity.
  - `category_id` (integer): The new category ID.
  - `image_url` (string): The new image URL.
- **Body Example**: `{"total_quantity": 6, "image_url": "http://new-url.com/dune.jpg"}`
- **`curl` Example** (updates book with ID 1):
  ```bash
  curl -X PATCH -H "Content-Type: application/json" \
  -d '{"total_quantity": 6}' \
  http://127.0.0.1:5001/api/books/1
  ```
- **Success Response (200)**: The updated book object.

#### **5. Delete a book**
- **Endpoint**: `DELETE /api/books/<id>`
- **Description**: Deletes a book by its ID. Fails if the book has active borrowings.
- **Path Parameters**:
  - `id` (integer, required): The unique identifier of the book to delete.
- **`curl` Example** (deletes book with ID 1):
  ```bash
  curl -X DELETE -H "Api-Key: YOUR_API_KEY" \
  http://127.0.0.1:5001/api/books/1
  ```
- **Success Response (204)**: No content.

---

### **Borrowing Management (`/api/borrowings`)**

#### **1. Borrow a book**
- **Endpoint**: `POST /api/borrowings/borrow`
- **Description**: Creates a new borrowing record for a book, decreasing its available quantity.
- **Request Body**:
  - `book_id` (integer, required): The ID of the book to borrow.
  - `borrower_name` (string, required): The name of the person borrowing the book.
  - `borrower_email` (string, optional): The borrower's email address.
  - `borrower_phone` (string, optional): The borrower's phone number (if provided, length between 1 and 20 characters).
  - `borrower_room_number` (string, required): The borrower's hotel room number.
  - `borrower_hotel` (string, required): The name of the hotel.
- **Body Example**:
  ```json
  {
    "book_id": 1,
    "borrower_name": "John Doe",
    "borrower_email": "john.doe@example.com",
    "borrower_phone": "1234567890",
    "borrower_room_number": "101",
    "borrower_hotel": "Grand Hotel"
  }
  ```
- **`curl` Example**:
  ```bash
  curl -X POST -H "Content-Type: application/json" \
  -H "Api-Key: YOUR_API_KEY" \
  -d '{"book_id": 1, "borrower_name": "John Doe", "borrower_email": "john.doe@example.com", "borrower_phone": "1234567890", "borrower_room_number": "101", "borrower_hotel": "Grand Hotel"}' \
  http://127.0.0.1:5001/api/borrowings/borrow
  ```
- **Success Response (201)**: The new borrowing record object.

#### **2. Return a book**
- **Endpoint**: `PATCH /api/borrowings/return/<borrowing_id>`
- **Description**: Marks an existing borrowing record as returned, increasing the book's available quantity.
- **Path Parameters**:
  - `borrowing_id` (integer, required): The ID of the borrowing record to mark as returned.
- **`curl` Example**:
  ```bash
  curl -X PATCH -H "Content-Type: application/json" \
  -H "Api-Key: YOUR_API_KEY" \
  http://127.0.0.1:5001/api/borrowings/return/1 
  ```
- **Success Response (200)**: The updated borrowing record object.

#### 3. Get borrowing records
- **Endpoint**: `GET /api/borrowings`
- **Description**: Retrieves a list of borrowing records, with optional filters and pagination.
- **Query Parameters**:
  - `search` (string, optional): Fuzzy search on the borrower's `name`, `email`, `phone`, `hotel`, or the book's `title`.
  - `is_returned` (boolean, optional): Set to `false` to get all currently borrowed (active) records. Set to `true` to get all returned records. If omitted, all records are returned.
  - `page` (integer, optional): Page number for pagination. Defaults to 1.
  - `per_page` (integer, optional): Number of items per page for pagination. Defaults to 50. Set to `0` to retrieve all items without pagination.
- **`curl` Examples**:
  ```bash
  # Get all borrowing records (paginated with defaults)
  curl http://127.0.0.1:5001/api/borrowings

  # Get unreturned borrowings on page 1, 5 per page
  curl "http://127.0.0.1:5001/api/borrowings?is_returned=false&page=1&per_page=5"

  # Fuzzy search by borrower name
  curl "http://127.0.0.1:5001/api/borrowings?search=John%20Doe"

  # Get all records without pagination
  curl "http://127.0.0.1:5001/api/borrowings?per_page=0"
  ```
- **Success Response (200)**: 
  ```json
  {
    "borrowings": [
      {
        "id": 1,
        "book_id": 1,
        "book_title": "Dune",
        "borrower_name": "John Doe",
        "borrower_email": "john.doe@example.com",
        "borrower_phone": "1234567890",
        "borrower_room_number": "101",
        "borrower_hotel": "Grand Hotel",
        "borrowed_at": "2023-01-05T15:30:00Z",
        "returned_at": null,
        "is_returned": false
      }
    ],
    "pagination": {
      "total": 5,
      "pages": 1,
      "page": 1,
      "per_page": 5,
      "has_next": false,
      "has_prev": false,
      "next_num": null,
      "prev_num": null
    }
  }
  ```

#### **4. Get a single borrowing record**
- **Endpoint**: `GET /api/borrowings/<id>`
- **Description**: Retrieves a single borrowing record by its ID.
- **Path Parameters**:
  - `id` (integer, required): The unique identifier of the borrowing record.
- **`curl` Example** (for borrowing record with ID 1):
  ```bash
  curl http://127.0.0.1:5001/api/borrowings/1
  ```
- **Success Response (200)**: `{...}` (the borrowing record object)
