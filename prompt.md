## **專案總覽**

* **專案名稱**：飯店短期借書系統後端 API (MVP)  
* **專案目標**：建立一個最小可行性產品 (MVP) 後端服務，支援由書店人員手動處理的書籍借閱與歸還流程，確保資料完整性。核心在於建立一套可信賴的 RESTful API，作為書店後台系統與資料庫之間的唯一介面。

## **程式碼架構與環境設定**

* **專案結構**：遵循標準 Flask 專案架構。  
  books\_api\_project/  
  ├── app.py                      \# 主程式入口，建立 Flask app。  
  ├── config.py                   \# 設定檔，讀取環境變數。  
  ├── requirements.txt            \# Python 套件相依性清單。  
  ├── passenger\_wsgi.py           \# cPanel WSGI 啟動檔案。  
  │  
  ├── models/                     \# 資料模型與資料庫互動層  
  │   ├── \_\_init\_\_.py  
  │   ├── book.py                 \# 定義書籍資料模型與操作。  
  │   ├── category.py             \# 定義分類資料模型與操作。  
  │   └── borrowing.py            \# 定義借閱紀錄資料模型與操作。  
  │  
  ├── routes/                     \# API 路由層  
  │   ├── \_\_init\_\_.py  
  │   ├── books.py                \# 書籍與搜尋 API 路由 (藍圖)。  
  │   ├── categories.py           \# 分類 API 路由 (藍圖)。  
  │   └── borrowings.py           \# 借閱 API 路由 (藍圖)。  
  │  
  └── services/                   \# 核心業務邏輯層  
      ├── \_\_init\_\_.py  
      ├── book\_service.py         \# 包含書籍相關的業務邏輯。  
      └── borrowing\_service.py    \# 包含借閱相關的業務邏輯。

* **技術棧**：  
  * **後端框架**：Python 3.8+ / Flask  
  * **資料庫**：PostgreSQL  
  * **WSGI 伺服器**：Uvicorn (透過 Passenger)  
  * **套件**：Flask, psycopg2, pydantic, SQLAlchemy (推薦用於 ORM)

## **資料庫規格**

資料庫名稱和使用者需從環境變數中讀取。所有資料表皆為 PostgreSQL，並包含索引和觸發器。

### **categories 資料表**

* **用途**：管理書籍分類。  
* **結構**：  
  CREATE TABLE categories (  
      id SERIAL PRIMARY KEY,  
      name VARCHAR(100) NOT NULL UNIQUE  
  );

### **books 資料表**

* **用途**：管理書籍庫存與資訊。  
* **結構**：  
  CREATE TABLE books (  
      id SERIAL PRIMARY KEY,  
      title VARCHAR(255) NOT NULL,  
      author VARCHAR(255) NOT NULL,  
      isbn VARCHAR(20) NOT NULL UNIQUE,  
      image\_url TEXT,  
      total\_quantity INTEGER NOT NULL DEFAULT 0,  
      available\_quantity INTEGER NOT NULL DEFAULT 0,  
      category\_id INTEGER,  
      created\_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),  
      updated\_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),  
      CONSTRAINT fk\_category FOREIGN KEY (category\_id) REFERENCES categories(id) ON DELETE SET NULL  
  );

* **觸發器與索引**：  
  \-- 觸發器：自動更新 updated\_at  
  CREATE OR REPLACE FUNCTION set\_updated\_at()  
  RETURNS TRIGGER AS $$  
  BEGIN  
      NEW.updated\_at \= NOW();  
      RETURN NEW;  
  END;  
  $$ LANGUAGE plpgsql;

  CREATE TRIGGER set\_updated\_at\_trigger  
  BEFORE UPDATE ON books  
  FOR EACH ROW  
  EXECUTE FUNCTION set\_updated\_at();

  \-- 索引  
  CREATE UNIQUE INDEX idx\_books\_isbn ON books(isbn);  
  CREATE INDEX idx\_books\_title ON books(title);  
  CREATE INDEX idx\_books\_category\_id ON books(category\_id);

### **borrowings 資料表**

* **用途**：記錄每一筆借閱事件。  
* **結構**：  
  CREATE TABLE borrowings (  
      id SERIAL PRIMARY KEY,  
      book\_id INTEGER NOT NULL,  
      borrower\_name VARCHAR(255) NOT NULL,  
      borrower\_room\_number VARCHAR(10) NOT NULL,  
      borrower\_hotel VARCHAR(255) NOT NULL,  
      borrowed\_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),  
      returned\_at TIMESTAMPTZ,  
      is\_returned BOOLEAN NOT NULL DEFAULT FALSE,  
      CONSTRAINT fk\_book\_borrowed FOREIGN KEY(book\_id) REFERENCES books(id) ON DELETE RESTRICT  
  );

* **索引**：  
  \-- 索引  
  CREATE INDEX idx\_borrowings\_book\_id ON borrowings(book\_id);  
  CREATE INDEX idx\_borrowings\_is\_returned ON borrowings(is\_returned);  
  CREATE INDEX idx\_borrowings\_borrower\_room\_number ON borrowings(borrower\_room\_number);  
  CREATE INDEX idx\_borrowings\_borrowed\_at ON borrowings(borrowed\_at);

## **API 端點規格**

所有 API 應回傳 JSON 格式回應，並由 routes 層呼叫 services 層處理核心邏輯。

### **1\. 書籍管理 API (routes/books.py)**

* **GET /api/books**：取得書籍列表。  
  * **用途**：提供書籍搜尋與篩選功能。  
  * **查詢參數**：  
    * search=\<關鍵字\>：根據書名或作者模糊搜尋。  
    * category=\<分類名\>：按分類名稱精確篩選。後端需透過 JOIN 操作實現。  
    * available=true：篩選 available\_quantity \> 0 的可借閱書籍。  
  * **成功回應**：200 OK，{"books": \[...\]}  
* **GET /api/books/\<int:id\>**：取得單本書詳細資訊。  
  * **用途**：取得單一書籍的所有資訊。  
  * **成功回應**：200 OK，{"book": {...}}  
  * **失敗回應**：404 Not Found (書籍不存在)。  
* **POST /api/books**：新增書籍。  
  * **用途**：新增一本新書到庫存。  
  * **請求主體**：{"title": "...", "author": "...", "isbn": "...", "total\_quantity": "...", "category\_id": "..."}  
  * **成功回應**：201 Created。  
* **PUT /api/books/\<int:id\>**：更新書籍資訊。  
  * **用途**：更新現有書籍的資訊。  
  * **請求主體**：與 POST 類似。  
  * **成功回應**：200 OK。  
  * **失敗回應**：404 Not Found (書籍不存在)。  
* **DELETE /api/books/\<int:id\>**：刪除書籍。  
  * **用途**：從庫存中移除書籍。  
  * **成功回應**：204 No Content。

### **2\. 分類管理 API (routes/categories.py)**

* **GET /api/categories**：取得所有分類列表。  
  * **用途**：提供給前端顯示分類選項。  
* **POST /api/categories**：新增分類。  
  * **用途**：新增一個書籍分類。  
* **PUT /api/categories/\<int:id\>**：更新分類。  
* **DELETE /api/categories/\<int:id\>**：刪除分類。

### **3\. 借閱核心 API (routes/borrowings.py)**

* **POST /api/borrowings/borrow**：**借書操作**。  
  * **用途**：為住客借出一本書。  
  * **核心邏輯**：在 services 層實現**原子性更新與資料庫交易**。  
    1. 根據 book\_identifier 查找 books 資料表的 id。  
    2. **原子性**減少 books 表的 available\_quantity。  
    3. 新增一筆紀錄到 borrowings 資料表。  
  * **請求主體**：{"book\_identifier": "ISBN或書名", "borrower\_name": "姓名", "borrower\_room\_number": "房號", "borrower\_hotel": "飯店名"}  
  * **成功回應**：201 Created。  
  * **失敗回應**：404 Not Found (書本不存在)、409 Conflict (庫存不足)。  
* **POST /api/borrowings/return**：**還書操作**。  
  * **用途**：確認書籍歸還。  
  * **核心邏輯**：在 services 層實現**資料庫交易**。  
    1. 根據請求資訊查找 borrowings 紀錄。  
    2. 更新該紀錄的 is\_returned 和 returned\_at。  
    3. 增加 books 表的 available\_quantity。  
  * **請求主體**：{"book\_identifier": "ISBN或書名", "borrower\_room\_number": "房號"}  
  * **成功回應**：200 OK。  
  * **失敗回應**：404 Not Found (借閱紀錄不存在)。  
* **GET /api/borrowings**：取得所有借閱紀錄列表。  
  * **用途**：提供借閱歷史和未歸還書籍列表。  
  * **查詢參數**：is\_returned=false (取得所有未歸還的書籍)。  
* **GET /api/borrowings/\<int:id\>**：取得單筆借閱紀錄詳細資訊。  
  * **用途**：供後台追蹤單一借閱事件。