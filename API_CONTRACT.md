# API CONTRACT – Mini-Netflix (Nhóm G12)

Tài liệu này định nghĩa cấu trúc giao tiếp REST API thực tế giữa Frontend (`web-ui/index.html`, `web-ui/admin.html`) và Backend (`web-ui/server.py`). Mọi endpoint JSON đều có tiền tố `/api`.

## Quy ước chung
- **Base URL:** `/api` (mặc định `http://localhost:5000/api`)
- **Content-Type:** `application/json`
- **Định dạng lỗi thực tế:**
  ```json
  {
    "success": false,
    "error": "Vi pham BR-01/FR-02: Tai khoan da dat gioi han so luong Profile toi da cua goi cuoc!",
    "is_trigger": true,
    "rule": "BR-01 / FR-02: Giới hạn số lượng Profile theo gói cước"
  }
  ```
  *Lưu ý:* Khi MySQL Trigger ném ra `SIGNAL SQLSTATE '45000'` (`errno = 1644`), trường `error` giữ **nguyên văn thông điệp từ Trigger MySQL** để phục vụ demo đồ án CSDL, kèm cờ `"is_trigger": true`.

---

## 1. Health & Authentication

### 1.1 Kiểm tra kết nối Backend & MySQL
- **Method:** `GET`
- **Endpoint:** `/api/health`
- **Response 200:** `{"status": "healthy", "database": "mini_netflix", "connected": true}`

### 1.2 Lấy danh sách tài khoản mẫu (Demo Account Switcher)
- **Method:** `GET`
- **Endpoint:** `/api/accounts`
- **Mô tả:** Trả về danh sách tài khoản `user_account` kết hợp `subscription_tier` và số lượng hồ sơ hiện có (`current_profile_count`).

### 1.3 Đăng nhập
- **Method:** `POST`
- **Endpoint:** `/api/auth/login`
- **Request Body:**
  ```json
  {
    "email": "an.nguyen@gmail.com",
    "password": "123456"
  }
  ```
- **Response 200:** Trả về `{ "success": true, "account": {...}, "is_admin": false, "redirect": "/" }`. Nếu là `admin@netflix.com` / `admin@mininetflix.com`, trả về `"is_admin": true`, `"redirect": "/admin"`.
- **Lỗi:**
  - `400 Bad Request`: Thiếu email hoặc mật khẩu.
  - `401 Unauthorized`: Sai mật khẩu.
  - `403 Forbidden`: Tài khoản có `account_status` khác `ACTIVE` (`SUSPENDED` / `CANCELED`).
  - `404 Not Found`: Email không tồn tại trong hệ thống.

### 1.4 Đăng ký tài khoản mới
- **Method:** `POST`
- **Endpoint:** `/api/auth/register`
- **Request Body:** `{ "email": "...", "password": "...", "tier_id": 1, "profile_name": "...", "is_kids": false }`
- **Mô tả:** Băm mật khẩu bằng `werkzeug.security.generate_password_hash` và thực hiện transaction thêm vào `user_account` + `profile`.
- **Response 201:** `{ "success": true, "account": {...}, "redirect": "/" }`

---

## 2. Profiles (Hồ sơ người xem — BR-01, BR-02, FR-02)

### 2.1 Lấy danh sách Profile của tài khoản
- **Method:** `GET`
- **Endpoint:** `/api/profiles?account_id={id}`

### 2.2 Tạo Profile mới (Kích hoạt Trigger BR-01)
- **Method:** `POST`
- **Endpoint:** `/api/profiles`
- **Request Body:** `{ "account_id": 1, "profile_name": "Anh Hai", "is_kids": false, "avatar_url": "..." }`
- **Response 201:** `{ "success": true, "message": "Khởi tạo hồ sơ thành công!", "profile_id": 10 }`
- **Lỗi đặc biệt (`400 Bad Request`):** Trigger `trg_check_profile_limit_before_insert` chặn khi đạt giới hạn `max_profiles_allowed`, trả về `"is_trigger": true`.

### 2.3 Cập nhật Profile
- **Method:** `PUT`
- **Endpoint:** `/api/profiles/{profile_id}`
- **Request Body:** `{ "profile_name": "...", "is_kids": false, "avatar_url": "..." }`

### 2.4 Xóa Profile
- **Method:** `DELETE`
- **Endpoint:** `/api/profiles/{profile_id}`
- **Mô tả:** Ràng buộc tối thiểu mỗi tài khoản phải còn ít nhất 1 hồ sơ.

---

## 3. Catalog, Metadata & Watchlist (FR-03, FR-04, FR-06, FR-07)

### 3.1 Lấy danh mục phim (Bộ lọc đa chiều)
- **Method:** `GET`
- **Endpoint:** `/api/catalog`
- **Query Params:** `q` (tìm theo tên/mô tả), `genre` / `genres` (hỗ trợ nhiều thể loại cách nhau bởi dấu phẩy), `type` (`MOVIE` | `TV_SERIES`), `lang` (`en`, `vi`, `ja`...), `kids` (`true`/`false` — lọc bỏ `R`, `NC-17` theo `BR-09`), `resolution` (`1080p`, `2K`, `4K`), `limit` (mặc định `60`).

### 3.2 Lấy chi tiết nội dung (Phân cấp Season/Episode & tiến trình từng tập)
- **Method:** `GET`
- **Endpoint:** `/api/content/{content_id}?profile_id={id}`
- **Mô tả:** Lấy thông tin từ `vw_content_full_catalog`; nếu là `TV_SERIES`, trả kèm mảng `seasons` chứa danh sách `episodes` cùng `stopped_position_seconds` và `is_episode_completed` của từng tập.

### 3.3 Danh mục tham chiếu (Thể loại, Ngôn ngữ, Gói cước)
- `GET /api/genres`
- `GET /api/languages`
- `GET /api/tiers`

### 3.4 Watchlist (Danh sách xem sau)
- `GET /api/watchlist?profile_id={id}`
- `POST /api/watchlist` — Body: `{ "profile_id": 1, "content_id": 5 }`
- `DELETE /api/watchlist` — Body: `{ "profile_id": 1, "content_id": 5 }`

---

## 4. Watch History (Nhật ký & Tiến trình xem — BR-06, BR-09, FR-05)

### 4.1 Lấy lịch sử xem của một Profile
- **Method:** `GET`
- **Endpoint:** `/api/watch-history?profile_id={id}`

### 4.2 Lưu tiến trình xem (Kích hoạt Trigger BR-09)
- **Method:** `POST`
- **Endpoint:** `/api/watch-history`
- **Request Body:**
  ```json
  {
    "profile_id": 1,
    "content_id": 7,
    "episode_id": 12,
    "stopped_position_seconds": 600,
    "is_completed": false,
    "mark_episode_completed": false,
    "episodes_progress": []
  }
  ```
- **Mô tả:**
  - Nếu là `MOVIE`: Giới hạn `stopped_position_seconds` trong `[0, duration_minutes * 60]`; nếu `is_completed = true` thì tự đặt lên 100% thời lượng.
  - Nếu là `TV_SERIES`: Lưu tiến trình độc lập cho từng `episode_id` theo khóa `uq_watch_history_profile_content_ep (profile_id, content_id, episode_id)`. Chỉ cho phép `is_completed = true` cho Series khi mọi tập thuộc tất cả các mùa đều hoàn tất.
- **Lỗi đặc biệt (`400 Bad Request`):** Trigger `trg_check_kids_rating_before_watch` chặn khi hồ sơ `is_kids = TRUE` xem phim `R` / `NC-17`, trả về `"is_trigger": true`.

### 4.3 Xóa một dòng lịch sử xem
- **Method:** `DELETE`
- **Endpoint:** `/api/watch-history/{history_id}`

---

## 5. Admin Console & Analytics API

### 5.1 Doanh thu theo gói cước (View `vw_subscription_revenue_summary`)
- `GET /api/admin/revenue`

### 5.2 Quản lý tài khoản người dùng
- `GET /api/admin/users`
- `PATCH /api/admin/users/{account_id}` — Body: `{ "account_status": "SUSPENDED", "tier_id": 2 }`

### 5.3 Quản lý kho nội dung phân cấp EER & Danh mục
- `POST /api/admin/content` — Thêm mới `CONTENT`, phân lớp `MOVIE` hoặc `TV_SERIES` (kèm Season 1 & Tập 1) và `CONTENT_GENRE`.
- `DELETE /api/admin/content/{content_id}` — Xóa lan truyền (`ON DELETE CASCADE`) toàn bộ dữ liệu liên quan.
- `POST /api/admin/seasons` — Thêm `SEASON` và tự động đồng bộ `tv_series.total_seasons`.
- `POST /api/admin/episodes` — Thêm `TV_EPISODE` vào `SEASON`.
- `POST /api/admin/genres` — Thêm thể loại mới.
- `POST /api/admin/languages` — Thêm ngôn ngữ mới (`iso_code` / `language_code`, `language_name`).

### 5.4 Chạy 10 truy vấn mẫu Phase 3 (`03_queries.sql`)
- `GET /api/admin/queries` — Danh sách 10 truy vấn mẫu.
- `GET /api/admin/queries/{query_id}` (`1` đến `10`) — Thực thi và trả về SQL + kết quả.

### 5.5 Trình khám phá bảng, Dynamic Query Builder & Read-Only SQL Sandbox
- `GET /api/admin/tables/{table_name}?limit=100` — Whitelist 13 bảng và 2 Views, `limit` trong `[1, 300]`.
- `POST /api/admin/query-builder` — Động cơ truy vấn động 4 phân hệ (`content`, `watch_behavior`, `subscription`, `raw_table`), tham số hóa an toàn `%s`, hỗ trợ `GROUP BY`, `HAVING`, `ORDER BY` và `LIMIT 1..300`.
- `POST /api/admin/sql-runner` — Request Body: `{ "sql": "SELECT * FROM content LIMIT 10" }`. Chỉ cho phép `SELECT`, `SHOW`, `DESCRIBE`, `EXPLAIN`, `WITH`; chặn các từ khóa thay đổi dữ liệu (`INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, `TRUNCATE`, `CREATE`, `GRANT`, `REVOKE`, `RENAME`, `REPLACE`, `LOCK`, `UNLOCK`).
