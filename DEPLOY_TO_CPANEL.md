# 部署到 cPanel 生產環境指南 (繁體中文)

本指南提供將 Flask 後端 API 部署到 cPanel 主機的詳細步驟。請確保您已完成本地開發和測試，並且所有程式碼都已準備好部署。

## 1. 前提條件

*   一個擁有 SSH 存取權限的 cPanel 帳戶。
*   在 cPanel 中已創建 PostgreSQL 或 MySQL 資料庫，並擁有資料庫名稱、使用者名稱和密碼。
*   您的專案程式碼已推送到 Git 儲存庫（如果 cPanel 支援 Git 部署）或可壓縮為 `.zip` 檔案。

## 2. 上傳專案檔案

您有多種方式可以將專案檔案上傳到 cPanel 的「應用程式根目錄」。

**應用程式根目錄**: 根據您的 cPanel 設定截圖，應為 `cornerbook_flask_api`。

### 方式一：使用 cPanel 檔案管理器 (推薦)

1.  **在本地壓縮專案**: 將您的整個專案資料夾（排除 `.git/`, `.venv/`, `.env`, `__pycache__/` 等被 `.gitignore` 忽略的檔案）壓縮為 `.zip` 檔案（例如 `my_flask_api.zip`）。
    *   **重要**: 確保您的 `.env` 檔案**絕對不要**包含在 `.zip` 中，因為它含有敏感資訊。
2.  **登錄 cPanel**: 進入「檔案管理器 (File Manager)」。
3.  **導航至應用程式根目錄**: 進入 `public_html/` 下的 `cornerbook_flask_api/` 目錄（或您在 cPanel 中設定的應用程式根目錄）。
4.  **上傳壓縮檔**: 點擊「上傳 (Upload)」按鈕，將 `my_flask_api.zip` 上傳到此目錄。
5.  **解壓縮**: 上傳完成後，選中 `.zip` 檔案，點擊「解壓縮 (Extract)」，將檔案解壓縮到當前目錄。

### 方式二：使用 FTP 客戶端

1.  使用 FileZilla 等 FTP 客戶端，透過您的 cPanel FTP 憑證連接到您的伺服器。
2.  將本地的專案資料夾內容（排除不需要部署的檔案）拖曳到遠程的應用程式根目錄。

### 方式三：使用 Git 部署 (如果 cPanel 支援)

1.  在 cPanel 中找到「Git™ Version Control」功能。
2.  輸入您的 Git 儲存庫 URL，並設定部署路徑為 `cornerbook_flask_api`。
3.  依照 cPanel 介面指示進行部署。

## 3. cPanel Python 應用程式設定

進入 cPanel 的「Setup Python App」介面，點擊「CREATE APPLICATION」或編輯現有應用程式：

1.  **Python 版本**: 選擇 `3.11.13` (或您專案實際使用的版本，保持與本地開發一致)。
2.  **應用程式根目錄 (Application root)**: `cornerbook_flask_api` (您上傳專案檔案的路徑)。
3.  **應用程式 URL (Application URL)**: 設定您希望 API 響應的 URL 路徑，例如 `https://cornerbook.inwave-studio.com/api`。
4.  **應用程式啟動檔案 (Application startup file)**: `passenger_wsgi.py`。
5.  **應用程式入口點 (Application Entry point)**: `application`。
6.  **點擊「CREATE」或「SAVE APPLICATION」**：這會初始化您的 Python 應用程式和其虛擬環境。

## 4. 配置環境變數

**【重要】切勿將您的 `.env` 檔案上傳到生產伺服器。** 所有敏感憑證和配置都應透過 cPanel 介面設定為環境變數。

在「Setup Python App」介面中，找到您應用程式的「環境變數 (Environment Variables)」區塊，並添加以下變數：

*   **資料庫憑證** (請替換為您在 cPanel 中創建的資料庫實際憑證):
    *   `DB_USER`: `your_cpanel_user_prefix_yourdbuser` (例: `mrsportt_cornerbook`)
    *   `DB_PASSWORD`: `your_db_password`
    *   `DB_HOST`: `localhost` (或 cPanel 提供的資料庫主機名)
    *   `DB_PORT`: `5432` (PostgreSQL 預設) 或 `3306` (MySQL 預設)
    *   `DB_NAME`: `your_cpanel_user_prefix_yourdbname` (例: `mrsportt_cornerbook_db`)

*   **應用程式密鑰**:
    *   `SECRET_KEY`: `a_very_long_and_random_secret_key_for_production` (建議生成一個新的、更安全的密鑰，不要使用本地的開發密鑰)

*   **API 金鑰**:
    *   `API_KEY`: `your_secure_api_key_for_production` (請使用您的實際 API 金鑰)

*   **日誌配置**:
    *   `LOG_FILE`: `/home/your_cpanel_username/logs/cornerbook_api.log` (建議將日誌放在應用程式根目錄之外的專用日誌目錄，替換 `your_cpanel_username`)。
    *   `LOG_LEVEL`: `WARNING` 或 `ERROR` (生產環境通常使用較高日誌級別，以減少日誌量)。
    *   `LOG_TO_STDOUT`: `False` (生產環境下日誌通常寫入文件而非標準輸出)。

*   **Flask 環境** (可選，但推薦):
    *   `FLASK_ENV`: `production` (指示 Flask 以生產模式運行)。

配置完畢後，點擊「SAVE」儲存環境變數。

## 5. 安裝專案依賴套件

在 cPanel 介面中，找到您應用程式的設定頁面：

1.  點擊「**Run Pip Install**」按鈕。
2.  這會自動根據您專案根目錄下的 `requirements.txt` 安裝所有依賴到您的虛擬環境中。

**手動安裝 (如果需要通過 SSH)**:

1.  透過 SSH 連接到您的 cPanel 帳戶。
2.  找到虛擬環境的路徑（通常在應用程式設定頁面顯示），並激活它：
    ```bash
    source /home/your_cpanel_username/virtualenv/python/3.11/cornerbook_flask_api/bin/activate
    ```
3.  切換到您的專案根目錄：
    ```bash
    cd /home/your_cpanel_username/cornerbook_flask_api
    ```
4.  運行 Pip 安裝命令：
    ```bash
    pip install -r requirements.txt
    ```

## 6. 初始化和遷移資料庫

您需要運行 Flask-Migrate 命令來在生產資料庫中創建資料表。這通常需要透過 SSH 執行。

1.  透過 SSH 連接到您的 cPanel 帳戶。
2.  激活應用程式的虛擬環境 (參見第 5 點手動安裝步驟)。
3.  切換到您的專案根目錄。
4.  執行資料庫遷移：
    ```bash
    flask db upgrade
    ```
    這會根據您的遷移腳本創建或更新資料庫 Schema。

## 7. 啟動應用程式

在 cPanel 的「Setup Python App」介面中，點擊藍色的「**START APP**」按鈕來啟動您的 Flask 應用程式。如果應用程式已經運行，您可以點擊「RESTART APP」來應用新的更改。

## 8. 查看應用程式日誌

您可以透過兩種方式查看日誌：

1.  **日誌檔案**: 如果您在環境變數中設定了 `LOG_FILE`，您可以透過 cPanel 的檔案管理器或 SSH 訪問該路徑來查看日誌檔案。
    ```bash
    cat /home/your_cpanel_username/logs/cornerbook_api.log
    ```
2.  **cPanel 錯誤日誌**: 檢查 cPanel 的「錯誤 (Errors)」日誌或「Apache 存取日誌 (Apache Access Logs)」，有時應用程式的錯誤會被記錄在那裡。

## 9. API 端點文件 (生產環境)

**基礎網址 (Base URL)**: `https://cornerbook.inwave-studio.com/api`

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
  https://cornerbook.inwave-studio.com/api/categories
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
  curl https://cornerbook.inwave-studio.com/api/categories
  ```
- **前端 (JavaScript fetch) 範例**: (無需 API 金鑰)
  ```
  URL: ${BASE_URL}/categories
  Headers: {}
  Body: (無)
  ```
- **成功回應 (200)**: `[{"id": 1, "name": "科幻小說"}, {"id": 2, "name": "經典文學"}]`

#### **3. 取得單一分類**
- **端點**: `GET /api/categories/<id>`
- **說明**: 根據 ID 檢索單一分類。
- **路徑參數 (Path Parameters)**:
  - `id` (整數, 必要): 分類的唯一識別碼。
- **`curl` 範例** (ID 為 1 的分類): (無需 API 金鑰)
  ```bash
  curl https://cornerbook.inwave-studio.com/api/categories/1
  ```
- **前端 (JavaScript fetch) 範例**: (無需 API 金鑰)
  ```
  URL: ${BASE_URL}/categories/1
  Headers: {}
  Body: (無)
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
- **`curl` 範例** (更新 ID 為 1 的分類): (需要 API 金鑰)
  ```bash
  curl -X PATCH -H "Content-Type: application/json" \
  -H "Api-Key: YOUR_API_KEY" \
  -d '{"name": "奇幻小說"}' \
  https://cornerbook.inwave-studio.com/api/categories/1
  ```
- **前端 (JavaScript fetch) 範例**: (需要 API 金鑰)
  ```
  URL: ${BASE_URL}/categories/1
  Headers: { 'Content-Type': 'application/json', 'Api-Key': API_KEY }
  Body: JSON.stringify({ name: '奇幻小說' })
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
  https://cornerbook.inwave-studio.com/api/categories/1
  ```
- **前端 (JavaScript fetch) 範例**: (需要 API 金鑰)
  ```
  URL: ${BASE_URL}/categories/1
  Headers: { 'Api-Key': API_KEY }
  Body: (無)
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
  https://cornerbook.inwave-studio.com/api/books
  ```
- **前端 (JavaScript fetch) 範例**: (需要 API 金鑰)
  ```
  URL: ${BASE_URL}/books
  Headers: { 'Content-Type': 'application/json', 'Api-Key': API_KEY }
  Body: JSON.stringify({ title: '沙丘', author: '法蘭克·赫伯特', isbn: '9780441013593', total_quantity: 5, category_id: 1, image_url: 'http://example.com/dune.jpg' })
  ```
- **成功回應 (201)**: 完整的書籍物件。

#### **2. 取得帶篩選條件的書籍列表**
- **端點**: `GET /api/books`
- **說明**: 檢索書籍列表，可選查詢參數用於篩選和分頁。
- **查詢參數 (Query Parameters)**:
  - `search` (字串, 可選): 根據書名或作者進行模糊搜尋。
  - `category` (字串, 可選): 根據精確的分類名稱篩選 (例如 "科幻小說")。
  - `available` (布林值, 可選): 設為 `true` 以篩選 `available_quantity > 0` 的可借閱書籍。
  - `page` (整數, 可選): 分頁頁碼，預設為 1。
  - `per_page` (整數, 可選): 每頁顯示的項目數，預設為 50。設為 `0` 可取得所有項目，不進行分頁。
- **`curl` 範例**: (無需 API 金鑰)
  ```bash
  # 取得所有書籍 (使用預設值分頁)
  curl https://cornerbook.inwave-studio.com/api/books

  # 取得第 2 頁書籍，每頁 10 本
  curl "https://cornerbook.inwave-studio.com/api/books?page=2&per_page=10"

  # 取得所有書籍，不進行分頁
  curl "https://cornerbook.inwave-studio.com/api/books?per_page=0"
  ```
- **前端 (JavaScript fetch) 範例**: (無需 API 金鑰)
  ```
  // 取得所有書籍 (使用預設值分頁)
  URL: ${BASE_URL}/books
  Headers: {}
  Body: (無)

  // 取得第 2 頁書籍，每頁 10 本
  URL: ${BASE_URL}/books?page=2&per_page=10
  Headers: {}
  Body: (無)

  // 取得所有書籍，不進行分頁
  URL: ${BASE_URL}/books?per_page=0
  Headers: {}
  Body: (無)
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
  ```

#### **3. 取得單一書籍**
- **端點**: `GET /api/books/<id>`
- **說明**: 根據 ID 檢索單一書籍。
- **路徑參數**:
  - `id` (整數, 必要): 書籍的唯一識別碼。
- **`curl` 範例** (ID 為 1 的書籍): (無需 API 金鑰)
  ```bash
  curl https://cornerbook.inwave-studio.com/api/books/1
  ```
- **前端 (JavaScript fetch) 範例**: (無需 API 金鑰)
  ```
  URL: ${BASE_URL}/books/1
  Headers: {}
  Body: (無)
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
  https://cornerbook.inwave-studio.com/api/books/1
  ```
- **前端 (JavaScript fetch) 範例**: (需要 API 金鑰)
  ```
  URL: ${BASE_URL}/books/1
  Headers: { 'Content-Type': 'application/json', 'Api-Key': API_KEY }
  Body: JSON.stringify({ total_quantity: 6, image_url: 'http://new-url.com/dune.jpg' })
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
  https://cornerbook.inwave-studio.com/api/books/1
  ```
- **前端 (JavaScript fetch) 範例**: (需要 API 金鑰)
  ```
  URL: ${BASE_URL}/books/1
  Headers: { 'Api-Key': API_KEY }
  Body: (無)
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
- **請求主體範例**: `{"book_id": 1, "borrower_name": "王小明", "borrower_room_number": "101", "borrower_hotel": "君悅飯店"}`
- **`curl` 範例**: (需要 API 金鑰)
  ```bash
  curl -X POST -H "Content-Type: application/json" \
  -H "Api-Key: YOUR_API_KEY" \
  -d '{"book_id": 1, "borrower_name": "王小明", "borrower_room_number": "101", "borrower_hotel": "君悅飯店"}' \
  https://cornerbook.inwave-studio.com/api/borrowings/borrow
  ```
- **前端 (JavaScript fetch) 範例**: (需要 API 金鑰)
  ```
  URL: ${BASE_URL}/borrowings/borrow
  Headers: { 'Content-Type': 'application/json', 'Api-Key': API_KEY }
  Body: JSON.stringify({ book_id: 1, borrower_name: '王小明', borrower_room_number: '101', borrower_hotel: '君悅飯店' })
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
  https://cornerbook.inwave-studio.com/api/borrowings/return/1 
  ```
- **前端 (JavaScript fetch) 範例**: (需要 API 金鑰)
  ```
  URL: ${BASE_URL}/borrowings/return/1
  Headers: { 'Api-Key': API_KEY }
  Body: (無)
  ```
- **成功回應 (200)**: 更新後的借閱紀錄物件。

#### 3. 取得借閱紀錄
- **端點**: `GET /api/borrowings`
- **說明**: 檢索借閱紀錄列表，可選篩選和分頁條件。
- **查詢參數**:
  - `is_returned` (布林值, 可選): 設為 `false` 可取得所有目前已借出（活躍）的紀錄。設為 `true` 可取得所有已歸還的紀錄。若省略，則回傳所有紀錄。
  - `page` (整數, 可選): 分頁頁碼，預設為 1。
  - `per_page` (整數, 可選): 每頁顯示的項目數，預設為 50。設為 `0` 可取得所有項目，不進行分頁。
- **`curl` 範例**: (無需 API 金鑰)
  ```bash
  # 取得所有借閱紀錄 (使用預設值分頁)
  curl https://cornerbook.inwave-studio.com/api/borrowings

  # 取得所有尚未歸還的書籍紀錄，第 1 頁，每頁 5 筆
  curl "https://cornerbook.inwave-studio.com/api/borrowings?is_returned=false&page=1&per_page=5"

  # 取得所有借閱紀錄，不進行分頁
  curl "https://cornerbook.inwave-studio.com/api/borrowings?per_page=0"
  ```
- **前端 (JavaScript fetch) 範例**: (無需 API 金鑰)
  ```
  // 取得所有借閱紀錄 (使用預設值分頁)
  URL: ${BASE_URL}/borrowings
  Headers: {}
  Body: (無)

  // 取得所有尚未歸還的書籍紀錄，第 1 頁，每頁 5 筆
  URL: ${BASE_URL}/borrowings?is_returned=false&page=1&per_page=5
  Headers: {}
  Body: (無)

  // 取得所有借閱紀錄，不進行分頁
  URL: ${BASE_URL}/borrowings?per_page=0
  Headers: {}
  Body: (無)
  ```
- **成功回應 (200)**:
  ```json
  {
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
  ```

#### **4. 取得單一借閱紀錄**
- **端點**: `GET /api/borrowings/<id>`
- **說明**: 根據 ID 檢索單一借閱紀錄。
- **路徑參數**:
  - `id` (整數, 必要): 借閱紀錄的唯一識別碼。
- **`curl` 範例** (ID 為 1 的借閱紀錄): (無需 API 金鑰)
  ```bash
  curl https://cornerbook.inwave-studio.com/api/borrowings/1
  ```
- **前端 (JavaScript fetch) 範例**: (無需 API 金鑰)
  ```
  URL: ${BASE_URL}/borrowings/1
  Headers: {}
  Body: (無)
  ```
- **成功回應 (200)**: `{...}` (借閱紀錄物件)

## 疑難排解 (Troubleshooting)

*   **應用程式無法啟動**: 檢查 cPanel 應用程式頁面上的錯誤訊息。嘗試點擊「Restart App」。檢查日誌檔案 (`LOG_FILE` 設定的路徑) 和 cPanel 的錯誤日誌。
*   **500 Internal Server Error**: 檢查應用程式的日誌 (`LOG_FILE` 設定的路徑) 以獲取詳細的錯誤堆疊追蹤。這通常是程式碼錯誤、環境變數未正確設定或資料庫連接問題導致的。
*   **401 Unauthorized**: 確認您在 cPanel 環境變數中設定的 `API_KEY` 與請求中使用的金鑰一致。
*   **資料庫連接問題**: 再次檢查環境變數 `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME` 是否正確，特別是 cPanel 可能會在用戶名和資料庫名前添加前綴。
