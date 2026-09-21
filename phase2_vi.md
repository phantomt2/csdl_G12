 - PHASE 2: LOGICAL DESIGN & NORMALIZATION
**Đối tượng phân tích:** `WATCHLIST`, `WATCH_HISTORY`, `AUDIO_SUBTITLE_TRACK`

---

## 1. Ánh xạ Lược đồ quan hệ (Relational Schema Mapping)

### A. Thực thể: WATCHLIST (Danh sách phát cá nhân)
- **Ký hiệu hình thức:**
  $$WATCHLIST(\underline{watchlist\_id}, content\_id, profile\_id, added\_date)$$
- **Khóa chính (PK):** `watchlist_id`
- **Khóa tự nhiên phụ (Alternate Key/UK):** `(profile_id, content_id)`
- **Thuộc tính chi tiết:**
  - `watchlist_id` (INT, Auto Increment): Mã định danh bản ghi lưu trữ
  - `profile_id` (INT, Not Null): Mã hồ sơ người dùng (FK)
  - `content_id` (INT, Not Null): Mã nội dung phim (FK)
  - `added_date` (TIMESTAMP, Default Current Timestamp): Dấu thời gian ghi nhận hành động lưu

### B. Thực thể: WATCH_HISTORY (Tiến độ và Lịch sử xem)
- **Ký hiệu hình thức:**
  $$WATCH\_HISTORY(\underline{history\_id}, profile\_id, content\_id, progress\_minute, last\_watched)$$
- **Khóa chính (PK):** `history_id`
- **Khóa tự nhiên phụ (Alternate Key/UK):** `(profile_id, content_id)`
- **Thuộc tính chi tiết:**
  - `history_id` (INT, Auto Increment): Mã định danh phiên xem phim
  - `profile_id` (INT, Not Null): Mã hồ sơ người dùng (FK)
  - `content_id` (INT, Not Null): Mã nội dung đang xem (FK)
  - `progress_minute` (INT, Default 0): Thời lượng đã xem dở dang (tính bằng phút)
  - `last_watched` (TIMESTAMP, Default Current Timestamp): Dấu thời gian cập nhật lần cuối

### C. Thực thể: AUDIO_SUBTITLE_TRACK (Tùy chọn Ngôn ngữ & Phụ đề)
- **Ký hiệu hình thức:**
  $$AUDIO\_SUBTITLE\_TRACK(\underline{track\_id}, content\_id, track\_type, language\_code, file\_url)$$
- **Khóa chính (PK):** `track_id`
- **Thuộc tính chi tiết:**
  - `track_id` (INT, Auto Increment): Mã định danh file track
  - `content_id` (INT, Not Null): Mã bộ phim chứa track này (FK)
  - `track_type` (VARCHAR(50), Not Null): Phân loại (Audio / Subtitle)
  - `language_code` (VARCHAR(10), Not Null): Mã ngôn ngữ theo chuẩn (VD: vi-VN, en-US)
  - `file_url` (VARCHAR(500), Not Null): Đường dẫn lưu trữ tài nguyên tĩnh

---

## 2. Định nghĩa Khóa ngoại và Toàn vẹn tham chiếu (Referential Integrity Definition)

| Bảng nguồn | Cột khóa ngoại (FK) | Bảng đích tham chiếu | Cột khóa chính (PK) | ON DELETE | ON UPDATE | Ý nghĩa nghiệp vụ / Ràng buộc |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `WATCHLIST` | `profile_id` | `USER_PROFILE` | `profile_id` | CASCADE | CASCADE | Khi một Profile bị xóa, toàn bộ danh sách phim đã lưu của Profile đó sẽ tự động bị dọn dẹp. |
| `WATCHLIST` | `content_id` | `CONTENT` | `content_id` | CASCADE | CASCADE | Khi nền tảng gỡ bỏ một bộ phim, bộ phim đó tự động biến mất khỏi Watchlist của tất cả người dùng. |
| `WATCH_HISTORY`| `profile_id` | `USER_PROFILE` | `profile_id` | CASCADE | CASCADE | Lịch sử xem là dữ liệu gắn liền với Profile. Hủy Profile đồng nghĩa hủy toàn bộ lịch sử xem. |
| `WATCH_HISTORY`| `content_id` | `CONTENT` | `content_id` | CASCADE | CASCADE | Khi nội dung bị gỡ, lịch sử và tiến độ xem của người dùng đối với nội dung đó sẽ bị xóa. |
| `AUDIO_SUBTITLE_TRACK`| `content_id` | `CONTENT` | `content_id` | CASCADE | CASCADE | Các file âm thanh/phụ đề là thực thể yếu phụ thuộc vào Content. Xóa phim thì phải xóa luôn các file track đi kèm để giải phóng dung lượng. |

---

## 3. Chứng minh Chuẩn hóa hình thức (Formal Normalization Proofs)

### A. Chuẩn hóa quan hệ `WATCHLIST`
- **Tập thuộc tính:** $R = \{watchlist\_id, profile\_id, content\_id, added\_date\}$
- **Tập phụ thuộc hàm (F):**
  - $f_1: watchlist\_id \rightarrow \{profile\_id, content\_id, added\_date\}$
  - $f_2: \{profile\_id, content\_id\} \rightarrow \{watchlist\_id, added\_date\}$
- **Tập khóa ứng viên (CK):** $CK_1 = \{watchlist\_id\}$; $CK_2 = \{profile\_id, content\_id\}$
- **Chứng minh:**
  - **1NF:** Mọi thuộc tính đều mang giá trị đơn nguyên (Atomic).
  - **2NF:** Khóa chính được chọn là khóa đơn $watchlist\_id$. Mọi thuộc tính không khóa đều phụ thuộc hàm đầy đủ vào khóa chính.
  - **3NF:** Không tồn tại phụ thuộc hàm bắc cầu giữa các thuộc tính không khóa.
  - **BCNF:** Trong mọi phụ thuộc hàm không tầm thường ($f_1, f_2$), vế trái đều là Siêu khóa (Superkey). 
- **Kết luận:** Quan hệ đạt dạng chuẩn **BCNF**.

### B. Chuẩn hóa quan hệ `WATCH_HISTORY`
- **Tập thuộc tính:** $R = \{history\_id, profile\_id, content\_id, progress\_minute, last\_watched\}$
- **Tập phụ thuộc hàm (F):**
  - $f_1: history\_id \rightarrow \{profile\_id, content\_id, progress\_minute, last\_watched\}$
  - $f_2: \{profile\_id, content\_id\} \rightarrow \{history\_id, progress\_minute, last\_watched\}$
- **Tập khóa ứng viên (CK):** $CK_1 = \{history\_id\}$; $CK_2 = \{profile\_id, content\_id\}$
- **Chứng minh:**
  - **1NF:** Dữ liệu thời gian, thời lượng đều là các giá trị nguyên tố.
  - **2NF:** Khóa chính $history\_id$ là thuộc tính đơn. Xét với $CK_2$, cả `progress_minute` và `last_watched` phụ thuộc vào toàn bộ cặp `{profile_id, content_id}`, không phụ thuộc một phần vào ai.
  - **3NF:** Thuộc tính `last_watched` và `progress_minute` không có sự phụ thuộc lẫn nhau. Đạt 3NF.
  - **BCNF:** Các vế quyết định ($history\_id$ và tập $\{profile\_id, content\_id\}$) đều là Siêu khóa.
- **Kết luận:** Quan hệ đạt dạng chuẩn **BCNF**.

### C. Chuẩn hóa quan hệ `AUDIO_SUBTITLE_TRACK`
- **Tập thuộc tính:** $R = \{track\_id, content\_id, track\_type, language\_code, file\_url\}$
- **Tập phụ thuộc hàm (F):**
  - $f_1: track\_id \rightarrow \{content\_id, track\_type, language\_code, file\_url\}$
- **Khóa chính (PK):** $PK = \{track\_id\}$
- **Chứng minh:**
  - **1NF:** Không chứa thuộc tính đa trị (mỗi dòng chỉ có 1 `file_url`).
  - **2NF:** Khóa chính đơn, không tồn tại phụ thuộc hàm một phần.
  - **3NF:** Các thuộc tính loại track, ngôn ngữ và đường dẫn chỉ mô tả cho `track_id`, không suy ra lẫn nhau. Đạt 3NF.
  - **BCNF:** Phụ thuộc hàm duy nhất có vế trái `track_id` là Siêu khóa.
- **Kết luận:** Quan hệ đạt dạng chuẩn **BCNF**.