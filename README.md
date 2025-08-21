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

**Base URL**: `http://127.0.0.1:5001`

All endpoints are prefixed with `/api`. The API returns data in JSON format and follows RESTful conventions (e.g., no trailing slashes on collection endpoints).

### General Error Response Format
Errors are returned in a standardized JSON format:
```json
{
  "error": "A descriptive error message.",
  "details": [ /* Optional: Specific validation error details from Pydantic */ ]
}
```

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
  curl -X DELETE http://127.0.0.1:5001/api/categories/1
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
  -d '{"title": "Dune", "author": "Frank Herbert", "isbn": "9780441013593", "total_quantity": 5, "category_id": 1}' \
  http://127.0.0.1:5001/api/books
  ```
- **Success Response (201)**: The full book object.

#### 2. Get books with filtering
- **Endpoint**: `GET /api/books`
- **Description**: Retrieves a list of books, with optional query parameters for filtering and pagination.
- **Query Parameters**:
  - `search` (string, optional): Fuzzy search on the book's `title` and `author`.
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

  # Get all available books in the "Sci-Fi" category without pagination
  curl "http://127.0.0.1:5001/api/books?category=Sci-Fi&available=true&per_page=0"

- **Success Response (200)**: {
  "books": [
    {
      "id": 1,
      "title": "Dune",
      "author": "Frank Herbert",
      "isbn": "9780441013593",
      "total_quantity": 5,
      "available_quantity": 5,
      "category_id": 1,
      "image_url": "http://example.com/dune.jpg",
      "created_at": "2023-01-01T10:00:00Z",
      "updated_at": "2023-01-01T10:00:00Z"
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
  curl -X DELETE http://127.0.0.1:5001/api/books/1
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
  - `borrower_room_number` (string, required): The borrower's hotel room number.
  - `borrower_hotel` (string, required): The name of the hotel.
- **Body Example**:
  ```json
  {
    "book_id": 1,
    "borrower_name": "John Doe",
    "borrower_room_number": "101",
    "borrower_hotel": "Grand Hotel"
  }
  ```
- **`curl` Example**:
  ```bash
  curl -X POST -H "Content-Type: application/json" \
  -d '{"book_id": 1, "borrower_name": "John Doe", "borrower_room_number": "101", "borrower_hotel": "Grand Hotel"}' \
  http://127.0.0.1:5001/api/borrowings/borrow
  ```
- **Success Response (201)**: The new borrowing record object.

#### **2. Return a book**
- **Endpoint**: `POST /api/borrowings/return`
- **Description**: Marks an existing borrowing record as returned, increasing the book's available quantity.
- **Request Body**:
  - `borrowing_id` (integer, required): The ID of the borrowing record to mark as returned.
- **Body Example**: `{"borrowing_id": 1}`
- **`curl` Example**:
  ```bash
  curl -X POST -H "Content-Type: application/json" \
  -d '{"borrowing_id": 1}' \
  http://127.0.0.1:5001/api/borrowings/return
  ```
- **Success Response (200)**: The updated borrowing record object.

#### 3. Get borrowing records
- **Endpoint**: `GET /api/borrowings`
- **Description**: Retrieves a list of borrowing records, with optional filters and pagination.
- **Query Parameters**:
  - `is_returned` (boolean, optional): Set to `false` to get all currently borrowed (active) records. Set to `true` to get all returned records. If omitted, all records are returned.
  - `page` (integer, optional): Page number for pagination. Defaults to 1.
  - `per_page` (integer, optional): Number of items per page for pagination. Defaults to 50. Set to `0` to retrieve all items without pagination.
- **`curl` Examples**:
  ```bash
  # Get all borrowing records (paginated with defaults)
  curl http://127.0.0.1:5001/api/borrowings

  # Get unreturned borrowings on page 1, 5 per page
  curl "http://127.0.0.1:5001/api/borrowings?is_returned=false&page=1&per_page=5"

  # Get all returned records without pagination
  curl "http://127.0.0.1:5001/api/borrowings?is_returned=true&per_page=0"

- **Success Response (200)**: {
  "borrowings": [
    {
      "id": 1,
      "book_id": 1,
      "borrower_name": "John Doe",
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


---

# 繁體中文說明文件

## 專案概述

這個專案為飯店短期借書系統提供後端 RESTful API 服務。它旨在作為管理書籍庫存、分類和借閱紀錄的唯一資料來源。此 API 使用 Python、Flask 和 SQLAlchemy 建構，並遵循結構化、可擴展的架構以及 RESTful 最佳實踐。

---

## 開始與本地開發

請依照以下步驟在您的本地開發機器上設定和運行專案。

### 1. 先決條件

- Python 3.8+
- PostgreSQL 資料庫
- `git` 用於版本控制
- Docker (可選，如果用於測試的 Testcontainers)

### 2. 設定

**複製儲存庫：**
```bash
git clone <您的儲存庫網址>
cd <專案目錄>
```

**建立並啟用 Python 虛擬環境：**
```bash
python -m venv .venv
source .venv/bin/activate
```

**安裝依賴套件：**
```bash
pip install -r requirements.txt
```

**設定環境變數：**
在專案根目錄下建立一個 `.env` 檔案。您可以複製 `.env.example`（如果存在），或建立一個新檔案。請確保其中包含您**本地** PostgreSQL 資料庫的正確憑證。

**初始化本地資料庫 (首次設定或完整重置)：**
使用提供的腳本來初始化/重置您的本地開發和測試資料庫。
```bash
chmod +x init_db.sh # 僅需執行一次
./init_db.sh
```

### 3. 運行開發伺服器

啟動本地開發伺服器：
```bash
python dev_server.py
```
API 將在 `http://127.0.0.1:5001` 上可用。

### 4. 運行測試

運行全面的測試套件：
```bash
pytest -v
```

---

## API 端點文件

**基礎網址 (Base URL)**: `http://127.0.0.1:5001`

所有端點都以 `/api` 為前綴。API 回傳 JSON 格式的資料，並遵循 RESTful 慣例（例如，集合端點的路徑結尾不加斜線）。

### 通用錯誤回應格式
錯誤將以標準化的 JSON 格式回傳：
```json
{
  "error": "一個描述性的錯誤訊息。",
  "details": [ /* 可選：Pydantic 驗證錯誤的詳細資訊 */ ]
}
```

### 日誌設定

日誌透過 `config.py` 設定並在 `app.py` 中初始化。在非偵錯模式（例如，生產環境）下，日誌將寫入到檔案中。

- **`LOG_FILE`**：日誌檔案路徑（例如，`logs/app.log`）。透過環境變數或 `config.py` 設定。
- **`LOG_LEVEL`**：最低日誌級別（例如，`INFO`、`WARNING`、`ERROR`、`CRITICAL`）。透過環境變數或 `config.py` 設定。
- **`LOG_TO_STDOUT`**：布林值，`True` 表示也將日誌輸出到標準輸出（控制台）。透過環境變數或 `config.py` 設定。

---

### **分類管理 (`/api/categories`)**

#### **1. 建立新分類**
- **端點 (Endpoint)**: `POST /api/categories`
- **說明 (Description)**: 新增一個書籍分類。
- **請求主體 (Request Body)**:
  - `name` (字串, 必要): 分類的名稱，必須是唯一的。
- **請求主體範例**: `{"name": "科幻小說"}`
- **`curl` 範例**:
  ```bash
  curl -X POST -H "Content-Type: application/json" \
  -d '{"name": "科幻小說"}' \
  http://127.0.0.1:5001/api/categories
  ```
- **成功回應 (201)**: `{"id": 1, "name": "科幻小說"}`

#### **2. 取得所有分類**
- **端點**: `GET /api/categories`
- **說明**: 檢索所有分類的列表。
- **參數**: 無。
- **`curl` 範例**:
  ```bash
  curl http://127.0.0.1:5001/api/categories
  ```
- **成功回應 (200)**: `[{"id": 1, "name": "科幻小說"}, {"id": 2, "name": "經典文學"}]`

#### **3. 取得單一分類**
- **端點**: `GET /api/categories/<id>`
- **說明**: 根據 ID 檢索單一分類。
- **路徑參數 (Path Parameters)**:
  - `id` (整數, 必要): 分類的唯一識別碼。
- **`curl` 範例** (ID 為 1 的分類):
  ```bash
  curl http://127.0.0.1:5001/api/categories/1
  ```
- **成功回應 (200)**: `{"id": 1, "name": "科幻小說"}`

#### **4. 更新分類**
- **端點**: `PATCH /api/categories/<id>`
- **說明**: 更新現有分類的名稱。
- **路徑參數**:
  - `id` (整數, 必要): 要更新的分類的唯一識別碼。
- **請求主體**:
  - `name` (字串, 必要): 分類的新名稱，必須是唯一的。
- **請求主體範例**: `{"name": "奇幻小說"}`
- **`curl` 範例** (更新 ID 為 1 的分類):
  ```bash
  curl -X PATCH -H "Content-Type: application/json" \
  -d '{"name": "奇幻小說"}' \
  http://127.0.0.1:5001/api/categories/1
  ```
- **成功回應 (200)**: `{"id": 1, "name": "奇幻小說"}`

#### **5. 刪除分類**
- **端點**: `DELETE /api/categories/<id>`
- **說明**: 根據 ID 刪除分類。
- **路徑參數**:
  - `id` (整數, 必要): 要刪除的分類的唯一識別碼。
- **`curl` 範例** (刪除 ID 為 1 的分類):
  ```bash
  curl -X DELETE http://127.0.0.1:5001/api/categories/1
  ```
- **成功回應 (204)**: 無內容。

---

### **書籍管理 (`/api/books`)**

#### **1. 新增書籍**
- **端點**: `POST /api/books`
- **說明**: 新增一本新書到庫存。
- **請求主體**:
  - `title` (字串, 必要): 書籍的標題。
  - `author` (字串, 必要): 書籍的作者。
  - `isbn` (字串, 必要): 書籍的 ISBN，必須是唯一的。
  - `total_quantity` (整數, 必要): 這本書的總副本數。
  - `category_id` (整數, 必要): 這本書所屬分類的 ID。
  - `image_url` (字串, 可選): 書籍封面的圖片 URL。
- **請求主體範例**:
  ```json
  {
    "title": "沙丘",
    "author": "法蘭克·赫伯特",
    "isbn": "9780441013593",
    "total_quantity": 5,
    "category_id": 1,
    "image_url": "http://example.com/dune.jpg"
  }
  ```
- **`curl` 範例**:
  ```bash
  curl -X POST -H "Content-Type: application/json" \
  -d '{"title": "沙丘", "author": "法蘭克·赫伯特", "isbn": "9780441013593", "total_quantity": 5, "category_id": 1}' \
  http://127.0.0.1:5001/api/books
  ```
- **成功回應 (201)**: 完整的書籍物件。

#### 2. 取得帶篩選條件的書籍列表
- **端點**: `GET /api/books`
- **說明**: 檢索書籍列表，可選查詢參數用於篩選和分頁。
- **查詢參數 (Query Parameters)**:
  - `search` (字串, 可選): 根據書名或作者進行模糊搜尋。
  - `category` (字串, 可選): 根據精確的分類名稱篩選 (例如 "科幻小說")。
  - `available` (布林值, 可選): 設為 `true` 以篩選 `available_quantity > 0` 的可借閱書籍。
  - `page` (整數, 可選): 分頁頁碼，預設為 1。
  - `per_page` (整數, 可選): 每頁顯示的項目數，預設為 50。設為 `0` 可取得所有項目，不進行分頁。
- **`curl` 範例**:
  ```bash
  # 取得所有書籍 (使用預設值分頁)
  curl http://127.0.0.1:5001/api/books

  # 取得第 2 頁書籍，每頁 10 本
  curl "http://127.0.0.1:5001/api/books?page=2&per_page=10"
  
  # 取得所有書籍，不進行分頁
  curl "http://127.0.0.1:5001/api/books?per_page=0"

- **成功回應 (200)**: {
  "books": [
    {
      "id": 1,
      "title": "沙丘",
      "author": "法蘭克·赫伯特",
      "isbn": "9780441013593",
      "total_quantity": 5,
      "available_quantity": 5,
      "category_id": 1,
      "image_url": "http://example.com/dune.jpg",
      "created_at": "2023-01-01T10:00:00Z",
      "updated_at": "2023-01-01T10:00:00Z"
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

#### **3. 取得單一書籍**
- **端點**: `GET /api/books/<id>`
- **說明**: 根據 ID 檢索單一書籍。
- **路徑參數**:
  - `id` (整數, 必要): 書籍的唯一識別碼。
- **`curl` 範例** (ID 為 1 的書籍):
  ```bash
  curl http://127.0.0.1:5001/api/books/1
  ```
- **成功回應 (200)**: `{"book": {...}}`

#### **4. 更新書籍 (部分更新)**
- **端點**: `PATCH /api/books/<id>`
- **說明**: 部分更新書籍詳細資訊。僅需包含您要更改的欄位。
- **路徑參數**:
  - `id` (整數, 必要): 要更新的書籍的唯一識別碼。
- **請求主體** (所有欄位皆為可選):
  - `title` (字串): 新的書名。
  - `author` (字串): 新的作者。
  - `isbn` (字串): 新的 ISBN，必須是唯一的。
  - `total_quantity` (整數): 新的總數量。
  - `category_id` (整數): 新的分類 ID。
  - `image_url` (字串): 新的圖片 URL。
- **請求主體範例**: `{"total_quantity": 6, "image_url": "http://new-url.com/dune.jpg"}`
- **`curl` 範例** (更新 ID 為 1 的書籍):
  ```bash
  curl -X PATCH -H "Content-Type: application/json" \
  -d '{"total_quantity": 6}' \
  http://127.0.0.1:5001/api/books/1
  ```
- **成功回應 (200)**: 更新後的書籍物件。

#### **5. 刪除書籍**
- **端點**: `DELETE /api/books/<id>`
- **說明**: 根據 ID 刪除書籍。如果書籍有活躍借閱紀錄，則刪除失敗。
- **路徑參數**:
  - `id` (整數, 必要): 要刪除的書籍的唯一識別碼。
- **`curl` 範例** (刪除 ID 為 1 的書籍):
  ```bash
  curl -X DELETE http://127.0.0.1:5001/api/books/1
  ```
- **成功回應 (204)**: 無內容。

---

### **借閱管理 (`/api/borrowings`)**

#### **1. 借書**
- **端點**: `POST /api/borrowings/borrow`
- **說明**: 為書籍建立新的借閱紀錄，並減少其可借閱數量。
- **請求主體**:
  - `book_id` (整數, 必要): 要借閱的書籍 ID。
  - `borrower_name` (字串, 必要): 借書人的姓名。
  - `borrower_room_number` (字串, 必要): 借書人的飯店房號。
  - `borrower_hotel` (字串, 必要): 飯店名稱。
- **請求主體範例**:
  ```json
  {
    "book_id": 1,
    "borrower_name": "王小明",
    "borrower_room_number": "101",
    "borrower_hotel": "君悅飯店"
  }
  ```
- **`curl` 範例**:
  ```bash
  curl -X POST -H "Content-Type: application/json" \
  -d '{"book_id": 1, "borrower_name": "王小明", "borrower_room_number": "101", "borrower_hotel": "君悅飯店"}' \
  http://127.0.0.1:5001/api/borrowings/borrow
  ```
- **成功回應 (201)**: 新的借閱紀錄物件。

#### **2. 還書**
- **端點**: `POST /api/borrowings/return`
- **說明**: 將現有借閱紀錄標記為已歸還，並增加書籍的可借閱數量。
- **請求主體**:
  - `borrowing_id` (整數, 必要): 要標記為已歸還的借閱紀錄 ID。
- **請求主體範例**: `{"borrowing_id": 1}`
- **`curl` 範例**:
  ```bash
  curl -X POST -H "Content-Type: application/json" \
  -d '{"borrowing_id": 1}' \
  http://127.0.0.1:5001/api/borrowings/return
  ```
- **成功回應 (200)**: 更新後的借閱紀錄物件。

#### 3. 取得借閱紀錄
- **端點**: `GET /api/borrowings`
- **說明**: 檢索借閱紀錄列表，可選篩選和分頁條件。
- **查詢參數**:
  - `is_returned` (布林值, 可選): 設為 `false` 可取得所有目前已借出（活躍）的紀錄。設為 `true` 可取得所有已歸還的紀錄。若省略，則回傳所有紀錄。
  - `page` (整數, 可選): 分頁頁碼，預設為 1。
  - `per_page` (整數, 可選): 每頁顯示的項目數，預設為 50。設為 `0` 可取得所有項目，不進行分頁。
- **`curl` 範例**:
  ```bash
  # 取得所有借閱紀錄 (使用預設值分頁)
  curl http://127.0.0.1:5001/api/borrowings

  # 取得所有尚未歸還的書籍紀錄，第 1 頁，每頁 5 筆
  curl "http://127.0.0.1:5001/api/borrowings?is_returned=false&page=1&per_page=5"
  
  # 取得所有借閱紀錄，不進行分頁
  curl "http://127.0.0.1:5001/api/borrowings?per_page=0"

- **成功回應 (200)**: {
  "borrowings": [
    {
      "id": 1,
      "book_id": 1,
      "borrower_name": "王小明",
      "borrower_room_number": "101",
      "borrower_hotel": "君悅飯店",
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

#### **4. 取得單一借閱紀錄**
- **端點**: `GET /api/borrowings/<id>`
- **說明**: 根據 ID 檢索單一借閱紀錄。
- **路徑參數**:
  - `id` (整數, 必要): 借閱紀錄的唯一識別碼。
- **`curl` 範例** (ID 為 1 的借閱紀錄):
  ```bash
  curl http://127.0.0.1:5001/api/borrowings/1
  ```
- **成功回應 (200)**: `{...}` (借閱紀錄物件)
