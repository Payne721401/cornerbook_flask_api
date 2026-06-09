#!/bin/bash

# API 測試腳本
# 使用方式: ./test_api.sh [base_url]
# 例如: ./test_api.sh http://localhost:5001
#      ./test_api.sh https://cornerbook.inwave-studio.com

# 設定基礎 URL（預設為本地）
BASE_URL=${1:-"http://localhost:5001"}
API_BASE="${BASE_URL}/api"

# API Key（根據您的應用程式配置，請替換為實際使用的金鑰）
API_KEY="75bb7ba3e0e2dfeaad80281c63bc80b9"

# 顏色設定
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 測試計數器
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# 臨時檔案來儲存測試 ID
TEMP_FILE="/tmp/api_test_ids.tmp"
> $TEMP_FILE

# 輔助函數
print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_test() {
    echo -e "${YELLOW}測試: $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ PASS: $1${NC}"
    ((PASSED_TESTS++))
}

print_error() {
    echo -e "${RED}✗ FAIL: $1${NC}"
    echo -e "${RED}   Response: $2${NC}"
    ((FAILED_TESTS++))
}

print_info() {
    echo -e "${BLUE}INFO: $1${NC}"
}

# 測試函數
test_request() {
    local method=$1
    local url=$2
    local data=$3
    local expected_status=$4
    local description=$5
    
    ((TOTAL_TESTS++))
    
    print_test "$description"
    
    if [ "$method" = "GET" ] || [ "$method" = "DELETE" ]; then
        response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
                       -X $method \
                       -H "Api-Key: $API_KEY" \
                       "$url")
    else
        response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
                       -X $method \
                       -H "Content-Type: application/json" \
                       -H "Api-Key: $API_KEY" \
                       -d "$data" \
                       "$url")
    fi
    
    http_code=$(echo "$response" | grep "HTTP_STATUS:" | cut -d: -f2)
    body=$(echo "$response" | sed '/HTTP_STATUS:/d')
    
    if [ "$http_code" = "$expected_status" ]; then
        print_success "$method $url - Status: $http_code"
        echo "$body"
        return 0
    else
        print_error "$method $url - Expected: $expected_status, Got: $http_code" "$body"
        return 1
    fi
}

# 從回應中提取 ID
extract_id() {
    echo "$1" | grep -o '"id":[0-9]*' | cut -d: -f2
}

# 開始測試
print_header "Corner Book Flask API 測試"
print_info "測試 URL: $API_BASE"
print_info "開始時間: $(date)"

# ==================== 分類 API 測試 ====================
print_header "測試分類 (Categories) API"

# 測試創建分類 - 使用沒有斜線的 URL
print_test "創建新分類 (無斜線)"
create_category_response=$(test_request "POST" "$API_BASE/categories" \
    '{"name": "測試小說"}' "201" "創建分類")

if [ $? -eq 0 ]; then
    CATEGORY_ID=$(extract_id "$create_category_response")
    echo "CATEGORY_ID=$CATEGORY_ID" >> $TEMP_FILE
    print_info "分類 ID: $CATEGORY_ID"
fi

# 測試重複創建分類（應該失敗）
test_request "POST" "$API_BASE/categories" \
    '{"name": "測試小說"}' "409" "創建重複分類 (應該失敗)"

# 測試獲取所有分類
test_request "GET" "$API_BASE/categories" "" "200" "獲取所有分類"

# 測試獲取單一分類
if [ ! -z "$CATEGORY_ID" ]; then
    test_request "GET" "$API_BASE/categories/$CATEGORY_ID" "" "200" "獲取單一分類"
fi

# 測試更新分類
if [ ! -z "$CATEGORY_ID" ]; then
    test_request "PATCH" "$API_BASE/categories/$CATEGORY_ID" \
        '{"name": "更新的測試小說"}' "200" "更新分類名稱"
fi

# ==================== 書籍 API 測試 ====================
print_header "測試書籍 (Books) API"

# 測試創建書籍 - 使用沒有斜線的 URL
if [ ! -z "$CATEGORY_ID" ]; then
    print_test "創建新書籍 (無斜線)"
    create_book_response=$(test_request "POST" "$API_BASE/books" \
        "{\"title\": \"測試書籍\", \"author\": \"測試作者\", \"isbn\": \"1234567890\", \"total_quantity\": 5, \"category_id\": $CATEGORY_ID, \"image_url\": \"https://example.com/book.jpg\"}" \
        "201" "創建書籍")
    
    if [ $? -eq 0 ]; then
        BOOK_ID=$(extract_id "$create_book_response")
        echo "BOOK_ID=$BOOK_ID" >> $TEMP_FILE
        print_info "書籍 ID: $BOOK_ID"
    fi
fi

# 測試重複 ISBN（應該失敗）
if [ ! -z "$CATEGORY_ID" ]; then
    test_request "POST" "$API_BASE/books" \
        "{\"title\": \"另一本書\", \"author\": \"測試作者2\", \"isbn\": \"1234567890\", \"total_quantity\": 3, \"category_id\": $CATEGORY_ID}" \
        "409" "創建重複 ISBN 書籍 (應該失敗)"
fi

# 測試獲取所有書籍
test_request "GET" "$API_BASE/books" "" "200" "獲取所有書籍"

# 測試書籍搜尋
test_request "GET" "$API_BASE/books?search=測試" "" "200" "搜尋書籍"

# 測試分類篩選
if [ ! -z "$CATEGORY_ID" ]; then
    test_request "GET" "$API_BASE/books?category=$CATEGORY_ID" "" "200" "按分類篩選書籍"
fi

# 測試可借閱篩選
test_request "GET" "$API_BASE/books?available=true" "" "200" "篩選可借閱書籍"

# 測試獲取單一書籍
if [ ! -z "$BOOK_ID" ]; then
    test_request "GET" "$API_BASE/books/$BOOK_ID" "" "200" "獲取單一書籍"
fi

# 測試更新書籍
if [ ! -z "$BOOK_ID" ]; then
    test_request "PATCH" "$API_BASE/books/$BOOK_ID" \
        '{"title": "更新的測試書籍", "total_quantity": 10}' "200" "更新書籍資訊"
fi

# ==================== 借書 API 測試 ====================
print_header "測試借書 (Borrowings) API"

# 測試借書
if [ ! -z "$BOOK_ID" ]; then
    print_test "借書"
    borrow_response=$(test_request "POST" "$API_BASE/borrowings/borrow" \
        "{\"book_id\": $BOOK_ID, \"borrower_name\": \"測試借書人\", \"borrower_room_number\": \"101\", \"borrower_hotel\": \"測試飯店\"}" \
        "201" "借書")
    
    if [ $? -eq 0 ]; then
        BORROWING_ID=$(extract_id "$borrow_response")
        echo "BORROWING_ID=$BORROWING_ID" >> $TEMP_FILE
        print_info "借書記錄 ID: $BORROWING_ID"
    fi
fi

# 測試獲取所有借書記錄
test_request "GET" "$API_BASE/borrowings" "" "200" "獲取所有借書記錄"

# 測試篩選未還書記錄
test_request "GET" "$API_BASE/borrowings?is_returned=false" "" "200" "獲取未還書記錄"

# 測試篩選已還書記錄
test_request "GET" "$API_BASE/borrowings?is_returned=true" "" "200" "獲取已還書記錄"

# 測試分頁
test_request "GET" "$API_BASE/borrowings?page=1&per_page=10" "" "200" "測試分頁功能"

# 測試獲取單一借書記錄
if [ ! -z "$BORROWING_ID" ]; then
    test_request "GET" "$API_BASE/borrowings/$BORROWING_ID" "" "200" "獲取單一借書記錄"
fi

# 測試還書
if [ ! -z "$BORROWING_ID" ]; then
    test_request "PATCH" "$API_BASE/borrowings/return/$BORROWING_ID" "" "200" "還書"
fi

# ==================== 錯誤處理測試 ====================
print_header "測試錯誤處理"

# 測試不存在的資源
test_request "GET" "$API_BASE/categories/99999" "" "404" "獲取不存在的分類"
test_request "GET" "$API_BASE/books/99999" "" "404" "獲取不存在的書籍"
test_request "GET" "$API_BASE/borrowings/99999" "" "404" "獲取不存在的借書記錄"

# 測試無效的分類 ID
test_request "POST" "$API_BASE/books/" \
    '{"title": "無效分類書籍", "author": "作者", "isbn": "9999999999", "total_quantity": 1, "category_id": 99999}' \
    "404" "使用不存在的分類 ID 創建書籍"

# 測試無效的書籍 ID 借書
test_request "POST" "$API_BASE/borrowings/borrow" \
    '{"book_id": 99999, "borrower_name": "測試", "borrower_room_number": "101", "borrower_hotel": "飯店"}' \
    "404" "借不存在的書籍"

# 測試無效 JSON
test_request "POST" "$API_BASE/categories/" \
    '{"name":}' "400" "發送無效 JSON"

# ==================== 清理測試資料 ====================
print_header "清理測試資料"

# 讀取測試 ID
if [ -f $TEMP_FILE ]; then
    source $TEMP_FILE
fi

# 刪除測試書籍
if [ ! -z "$BOOK_ID" ]; then
    test_request "DELETE" "$API_BASE/books/$BOOK_ID" "" "204" "刪除測試書籍"
fi

# 刪除測試分類
if [ ! -z "$CATEGORY_ID" ]; then
    test_request "DELETE" "$API_BASE/categories/$CATEGORY_ID" "" "204" "刪除測試分類"
fi

# 清理臨時檔案
rm -f $TEMP_FILE

# ==================== 測試結果統計 ====================
print_header "測試結果"
print_info "總測試數: $TOTAL_TESTS"
print_success "通過: $PASSED_TESTS"
# print_error "失敗: $FAILED_TESTS" ""
print_info "失敗: $FAILED_TESTS"
print_info "結束時間: $(date)"

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}🎉 所有測試通過！${NC}"
    exit 0
else
    echo -e "${RED}❌ 有 $FAILED_TESTS 個測試失敗${NC}"
    exit 1
fi
