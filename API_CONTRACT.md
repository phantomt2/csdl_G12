--- API_CONTRACT.md ---

# API CONTRACT – Mini-Netflix (Nhóm G12)

Tài liệu này định nghĩa cấu trúc giao tiếp giữa Frontend và Backend. Mọi endpoint JSON đều có tiền tố `/api` để phân biệt với các route render HTML (nếu có).

## Quy ước chung
- **Base URL:** `/api`
- **Content-Type:** `application/json`
- **Xác thực:** Bearer Token (JWT) trong header `Authorization: Bearer <token>`.
- **Định dạng lỗi:**
  ```json
  {
    "error": {
      "code": "BR-01_VIOLATION",
      "message": "Vi pham BR-01/FR-02: Tai khoan da dat gioi han so luong Profile toi da cua goi cuoc!"
    }
  }
  ```
  *Lưu ý:* Trường `message` phải giữ **nguyên văn** thông báo từ trigger MySQL để phục vụ demo đồ án. Frontend có trách nhiệm hiển thị chuỗi này.

---

## 1. Authentication & Session

### 1.1 Lấy danh sách tài khoản mẫu (Dùng cho màn hình Login Demo)
- **Method:** `GET`
- **Endpoint:** `/api/auth/accounts`
- **Mô tả:** Trả về danh sách rút gọn của tất cả `user_account` để người dùng chọn nhanh trên giao diện đăng nhập (giống `st.selectbox` trong Streamlit).
- **Response 200:**
  ```json
  [
    {
      "account_id": 1,
      "email": "user1@example.com",
      "tier_name": "Premium",
      "account_status": "ACTIVE"
    }
  ]
  ```

### 1.2 Đăng nhập
- **Method:** `POST`
- **Endpoint:** `/api/auth/login`
- **Request Body:**
  ```json
  {
    "email": "user1@example.com",
    "password": "123456"
  }
  ```
- **Response 200:**
  ```json
  {
    "token": "eyJhbGciOi...",
    "account_id": 1,
    "email": "user1@example.com",
    "role": "role_streaming_client",
    "tier": { ... }
  }
  ```
- **Lỗi:**
  - `401 Unauthorized`: Sai email hoặc mật khẩu.
  - `403 Forbidden`: Tài khoản có `account_status` khác `ACTIVE` (SUSPENDED/CANCELED). Message: `"Tài khoản hiện đang ở trạng thái ... Hệ thống từ chối truy cập."`

---

## 2. Profiles (Hồ sơ người xem)

### 2.1 Lấy danh sách Profile của tài khoản
- **Method:** `GET`
- **Endpoint:** `/api/profiles?account_id={id}`
- **Response 200:**
  ```json
  [
    {
      "profile_id": 1,
      "profile_name": "Bé Na",
      "is_kids": true,
      "avatar_url": "..."
    }
  ]
  ```

### 2.2 Tạo Profile mới (Có kiểm tra BR-01)
- **Method:** `POST`
- **Endpoint:** `/api/profiles`
- **Request Body:**
  ```json
  {
    "account_id": 1,
    "profile_name": "Anh Hai",
    "is_kids": false
  }
  ```
- **Response 201:** Trả về object Profile vừa tạo.
- **Lỗi đặc biệt:**
  - `409 Conflict`: Trigger `trg_check_profile_limit_before_insert` chặn (vượt quá `max_profiles_allowed`). Trả về message nguyên văn từ MySQL.
  - `400 Bad Request`: Tên profile trống hoặc trùng (`UNIQUE constraint`).

### 2.3 Xóa Profile
- **Method:** `DELETE`
- **Endpoint:** `/api/profiles/{profile_id}`
- **Response 200:** `{"message": "Xóa thành công"}`

---

## 3. Catalog & Streaming (Dành cho User)

### 3.1 Lấy danh mục phim (Có bộ lọc)
- **Method:** `GET`
- **Endpoint:** `/api/catalog`
- **Query Params:**
  - `q`: Tìm kiếm theo tên hoặc mô tả (LIKE).
  - `genre`: Tên thể loại.
  - `type`: `MOVIE` hoặc `TV_SERIES`.
  - `lang`: Mã ngôn ngữ (VD: `en`, `ja`).
  - `kids`: `true`/`false`. Nếu `true`, Backend tự động loại bỏ phim `R` và `NC-17` khỏi kết quả (BR-09).
- **Response 200:** Mảng các object từ View `vw_content_full_catalog` kèm `description` và `language_code`.

### 3.2 Lấy chi tiết nội dung (bao gồm Seasons/Episodes nếu là TV Series)
- **Method:** `GET`
- **Endpoint:** `/api/content/{content_id}`
- **Response 200:**
  ```json
  {
    "content_id": 1,
    "title": "Inception",
    "type": "MOVIE",
    "description": "...",
    "seasons": [] 
  }
  ```
  *(Ghi chú: Nếu là TV Series sẽ trả về mảng các mùa và tập)*

### 3.3 Lưu tiến trình xem (Watch History)
- **Method:** `POST`
- **Endpoint:** `/api/watch-history`
- **Request Body:**
  ```json
  {
    "profile_id": 1,
    "content_id": 1,
    "episode_id": null,
    "stopped_position_seconds": 300,
    "is_completed": false
  }
  ```
- **Response 200:** `{"message": "Đã lưu tiến trình"}`
- **Lỗi đặc biệt:**
  - `409 Conflict`: Trigger `trg_check_kids_rating_before_watch` chặn (Hồ sơ trẻ em xem phim R/NC-17). Trả về message nguyên văn.

---

## 4. Watchlist (Danh sách xem sau)

### 4.1 Lấy Watchlist
- **Method:** `GET`
- **Endpoint:** `/api/watchlist?profile_id={id}`

### 4.2 Thêm vào Watchlist
- **Method:** `POST`
- **Endpoint:** `/api/watchlist`
- **Request Body:** `{ "profile_id": 1, "content_id": 5 }`

### 4.3 Xóa khỏi Watchlist
- **Method:** `DELETE`
- **Endpoint:** `/api/watchlist?profile_id={id}&content_id={id}`

---

## 5. Admin Portal (Yêu cầu Role `system_admin`)

### 5.1 Quản lý Người dùng (Dữ liệu nhạy cảm)
- **Method:** `GET`
- **Endpoint:** `/api/admin/users`
- **Mô tả:** Trả về bảng `user_account` join `subscription_tier`, bao gồm cả `password_hash`.
- **Cập nhật tài khoản:**
  - `PATCH /api/admin/users/{account_id}`
  - Body: `{ "account_status": "SUSPENDED", "tier_id": 2 }`

### 5.2 Thêm nội dung mới (MOVIE / TV_SERIES)
- **Method:** `POST`
- **Endpoint:** `/api/admin/content`
- **Mô tả:** Thực hiện INSERT vào bảng `content`, sau đó INSERT vào `movie` hoặc `tv_series`, và cuối cùng là `content_genre`.

### 5.3 Chạy 10 truy vấn phân tích
- **Method:** `GET`
- **Endpoint:** `/api/admin/analytics/{query_id}` (query_id từ 1 đến 10)
- **Mô tả:** Trả về kết quả của câu SQL tương ứng trong `queries_dict` (đã có trong `app.py`).

### 5.4 Trình khám phá DB & Chạy SQL (Dành cho DBA)
- **Method:** `GET`
- **Endpoint:** `/api/admin/tables/{table_name}`
- **Method:** `POST`
- **Endpoint:** `/api/admin/sql`
- **Request Body:** `{ "sql": "SELECT * FROM content" }`
- **Bảo mật:** Endpoint này phải được Backend whitelist, chỉ cho phép các lệnh `SELECT`, `EXPLAIN`, `SHOW`, `DESC`. Từ chối mọi lệnh thay đổi dữ liệu (`INSERT`, `UPDATE`, `DELETE`, `DROP`).