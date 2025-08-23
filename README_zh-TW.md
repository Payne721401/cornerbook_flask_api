# 飯店短期借書系統 - 後端 API

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

**基礎網址 (Base URL)**: `http://127.0.0.1:5001/api`

所有端點都以 `/api` 為前綴。API 回傳 JSON 格式的資料，並遵循 RESTful 慣例（例如，集合端點的路徑結尾不加斜線）。

### 通用錯誤回應格式
錯誤將以標準化的 JSON 格式回傳：
```json
{
  "error": "一個描述性的錯誤訊息。",
  "details": [ /* 可選：Pydantic 驗證錯誤的詳細資訊 */ ]
}
```

### 認證 (Authentication)
修改資料的端點 (POST, PATCH, DELETE) 需要 API 金鑰。請將 API 金鑰包含在 `Api-Key` HTTP 標頭中。
**範例**: `-H "Api-Key: YOUR_API_KEY"`

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
- **`curl` 範例**: (需要 API 金鑰)
  ```bash
  curl -X POST -H "Content-Type: application/json" \
  -H "Api-Key: YOUR_API_KEY" \
  -d '{"name": "科幻小說"}' \
  http://127.0.0.1:5001/api/categories
  ```
- **前端 (JavaScript fetch) 範例**: (需要 API 金鑰)
  ```
  URL: ${BASE_URL}/categories
  Headers: { 'Content-Type': 'application/json', 'Api-Key': API_KEY }
  Body: JSON.stringify({ name: '科幻小說' })
  ```
- **成功回應 (201)**: `{"id": 1, "name": "科幻小說"}`

#### **2. 取得所有分類**
- **端點**: `GET /api/categories`
- **說明**: 檢索所有分類的列表。
- **參數**: 無。
- **`curl` 範例**: (無需 API 金鑰)
  ```bash
  curl http://127.0.0.1:5001/api/categories
  ```
- **成功回應 (200)**: `[{"id": 1, "name": "科幻小說"}, {"id": 2, "name": "經典文學"}]`

#### **3. 取得單一分類**
- **端點**: `GET /api/categories/<id>`
- **說明**: 根據 ID 檢索單一分類。
- **路徑參數 (Path Parameters)**:
  - `id` (整數, 必要): 分類的唯一識別碼。
- **`curl` 範例** (ID 為 1 的分類): (無需 API 金鑰)
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
- **`curl` 範例**: (需要 API 金鑰)
  ```bash
  curl -X PATCH -H "Content-Type: application/json" \
  -H "Api-Key: YOUR_API_KEY" \
  -d '{"name": "奇幻小說"}' \
  http://127.0.0.1:5001/api/categories/1
  ```
- **成功回應 (200)**: `{"id": 1, "name": "奇幻小說"}`

#### **5. 刪除分類**
- **端點**: `DELETE /api/categories/<id>`
- **說明**: 根據 ID 刪除分類。
- **路徑參數**:
  - `id` (整數, 必要): 要刪除的分類的唯一識別碼。
- **`curl` 範例** (刪除 ID 為 1 的分類): (需要 API 金鑰)
  ```bash
  curl -X DELETE -H "Api-Key: YOUR_API_KEY" \
  http://127.0.0.1:5001/api/categories/1
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
- **請求主體範例**: `{"title": "沙丘", "author": "法蘭克·赫伯特", "isbn": "9780441013593", "total_quantity": 5, "category_id": 1, "image_url": "http://example.com/dune.jpg"}`
- **`curl` 範例**: (需要 API 金鑰)
  ```bash
  curl -X POST -H "Content-Type: application/json" \
  -H "Api-Key: YOUR_API_KEY" \
  -d '{"title": "沙丘", "author": "法蘭克·赫伯特", "isbn": "9780441013593", "total_quantity": 5, "category_id": 1}' \
  http://127.0.0.1:5001/api/books
  ```
- **成功回應 (201)**: 完整的書籍物件。

#### 2. 取得帶篩選條件的書籍列表
- **端點**: `GET /api/books`
- **說明**: 檢索書籍列表，可選查詢參數用於篩選和分頁。
- **查詢參數 (Query Parameters)**:
  - `search` (字串, 可選): 根據書名、作者或 ISBN 進行模糊搜尋。
  - `category` (字串, 可選): 根據精確的分類名稱篩選 (例如 "科幻小說")。
  - `available` (布林值, 可選): 設為 `true` 以篩選 `available_quantity > 0` 的可借閱書籍。
  - `page` (整數, 可選): 分頁頁碼，預設為 1。
  - `per_page` (整數, 可選): 每頁顯示的項目數，預設為 50。設為 `0` 可取得所有項目，不進行分頁。
- **`curl` 範例**: (無需 API 金鑰)
  ```bash
  # 取得所有書籍 (使用預設值分頁)
  curl http://127.0.0.1:5001/api/books

  # 取得第 2 頁書籍，每頁 10 本
  curl "http://127.0.0.1:5001/api/books?page=2&per_page=10"

  # 根據書名模糊搜尋
  curl "http://127.0.0.1:5001/api/books?search=沙丘"

  # 取得所有書籍，不進行分頁
  curl "http://127.0.0.1:5001/api/books?per_page=0"
  ```
- **成功回應 (200)**:
  ```json
  {
    "books": [
      {
        "id": 1,
        "title": "沙丘",
        "author": "法蘭克·赫伯特",
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

#### **3. 取得單一書籍**
- **端點**: `GET /api/books/<id>`
- **說明**: 根據 ID 檢索單一書籍。
- **路徑參數**:
  - `id` (整數, 必要): 書籍的唯一識別碼。
- **`curl` 範例** (ID 為 1 的書籍): (無需 API 金鑰)
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
- **`curl` 範例** (更新 ID 為 1 的書籍): (需要 API 金鑰)
  ```bash
  curl -X PATCH -H "Content-Type: application/json" \
  -H "Api-Key: YOUR_API_KEY" \
  -d '{"total_quantity": 6}' \
  http://127.0.0.1:5001/api/books/1
  ```
- **成功回應 (200)**: 更新後的書籍物件。

#### **5. 刪除書籍**
- **端點**: `DELETE /api/books/<id>`
- **說明**: 根據 ID 刪除書籍。如果書籍有活躍借閱紀錄，則刪除失敗。
- **路徑參數**:
  - `id` (整數, 必要): 要刪除的書籍的唯一識別碼。
- **`curl` 範例** (刪除 ID 為 1 的書籍): (需要 API 金鑰)
  ```bash
  curl -X DELETE -H "Api-Key: YOUR_API_KEY" \
  http://127.0.0.1:5001/api/books/1
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
  - `borrower_email` (字串, 可選): 借書人的電子郵件地址。
  - `borrower_phone` (字串, 可選): 借書人的手機號碼（若提供，長度需介於 1 到 20 個字元）。
  - `borrower_room_number` (字串, 必要): 借書人的飯店房號。
  - `borrower_hotel` (字串, 必要): 飯店名稱。
- **請求主體範例**: `{"book_id": 1, "borrower_name": "王小明", "borrower_email": "xiaoming.wang@example.com", "borrower_phone": "0912345678", "borrower_room_number": "101", "borrower_hotel": "君悅飯店"}`
- **`curl` 範例**: (需要 API 金鑰)
  ```bash
  curl -X POST -H "Content-Type: application/json" \
  -H "Api-Key: YOUR_API_KEY" \
  -d '{"book_id": 1, "borrower_name": "王小明", "borrower_email": "xiaoming.wang@example.com", "borrower_phone": "0912345678", "borrower_room_number": "101", "borrower_hotel": "君悅飯店"}' \
  http://127.0.0.1:5001/api/borrowings/borrow
  ```
- **成功回應 (201)**: 新的借閱紀錄物件。

#### **2. 還書**
- **端點**: `PATCH /api/borrowings/return/<borrowing_id>`
- **說明**: 將現有借閱紀錄標記為已歸還，並增加書籍的可借閱數量。
- **路徑參數**:
  - `borrowing_id` (整數, 必要): 要標記為已歸還的借閱紀錄 ID。
- **`curl` 範例**: (需要 API 金鑰)
  ```bash
  curl -X PATCH -H "Api-Key: YOUR_API_KEY" \
  http://127.0.0.1:5001/api/borrowings/return/1 
  ```
- **成功回應 (200)**: 更新後的借閱紀錄物件。

#### 3. 取得借閱紀錄
- **端點**: `GET /api/borrowings`
- **說明**: 檢索借閱紀錄列表，可選篩選和分頁條件。
- **查詢參數**:
  - `search` (字串, 可選): 根據借閱人姓名、電子郵件、電話、飯店名稱或書名進行模糊搜尋。
  - `is_returned` (布林值, 可選): 設為 `false` 可取得所有目前已借出（活躍）的紀錄。設為 `true` 可取得所有已歸還的紀錄。若省略，則回傳所有紀錄。
  - `page` (整數, 可選): 分頁頁碼，預設為 1。
  - `per_page` (整數, 可選): 每頁顯示的項目數，預設為 50。設為 `0` 可取得所有項目，不進行分頁。
- **`curl` 範例**: (無需 API 金鑰)
  ```bash
  # 取得所有借閱紀錄 (使用預設值分頁)
  curl http://127.0.0.1:5001/api/borrowings

  # 取得所有尚未歸還的書籍紀錄，第 1 頁，每頁 5 筆
  curl "http://127.0.0.1:5001/api/borrowings?is_returned=false&page=1&per_page=5"

  # 根據借閱人姓名模糊搜尋
  curl "http://127.0.0.1:5001/api/borrowings?search=王小明"

  # 取得所有借閱紀錄，不進行分頁
  curl "http://127.0.0.1:5001/api/borrowings?per_page=0"
  ```
- **成功回應 (200)**:
  ```json
  {
    "borrowings": [
      {
        "id": 1,
        "book_id": 1,
        "book_title": "沙丘",
        "borrower_name": "王小明",
        "borrower_email": "xiaoming.wang@example.com",
        "borrower_phone": "0912345678",
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
  ```

#### **4. 取得單一借閱紀錄**
- **端點**: `GET /api/borrowings/<id>`
- **說明**: 根據 ID 檢索單一借閱紀錄。
- **路徑參數**:
  - `id` (整數, 必要): 借閱紀錄的唯一識別碼。
- **`curl` 範例** (ID 為 1 的借閱紀錄): (無需 API 金鑰)
  ```bash
  curl http://127.0.0.1:5001/api/borrowings/1
  ```
- **成功回應 (200)**: `{...}` (借閱紀錄物件)

## 疑難排解 (Troubleshooting)

*   **應用程式無法啟動**: 檢查 cPanel 應用程式頁面上的錯誤訊息。嘗試點擊「Restart App」。檢查日誌檔案 (`LOG_FILE` 設定的路徑) 和 cPanel 的錯誤日誌。
*   **500 Internal Server Error**: 檢查應用程式的日誌 (`LOG_FILE` 設定的路徑) 以獲取詳細的錯誤堆疊追蹤。這通常是程式碼錯誤、環境變數未正確設定或資料庫連接問題導致的。
*   **401 Unauthorized**: 確認您在 cPanel 環境變數中設定的 `API_KEY` 與請求中使用的金鑰一致。
*   **資料庫連接問題**: 再次檢查環境變數 `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME` 是否正確，特別是 cPanel 可能會在用戶名和資料庫名前添加前綴。
