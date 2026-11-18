# Kết quả Kiểm chứng Tự động Hệ thống CSDL Mini-Netflix (Nhóm G12)

- **Môi trường kiểm thử thực tế:** MySQL Server `8.0.46`, Python `Flask test_client()`, dữ liệu đầy đủ `86.895` bản ghi trên 13 bảng (`8.817` tựa phim, `6.950` tài khoản, `13.694` hồ sơ, `13.697` lịch sử xem).
- **Lệnh chạy lại kiểm chứng:**
  ```powershell
  python "database_Phase 3/verify_database.py"
  ```
- **Kết quả tổng thể:** **56 / 56 ca kiểm thử ĐẠT (`0` thất bại)** — mọi kiểm thử DML đều dùng `START TRANSACTION ... ROLLBACK` và dọn sạch user RBAC tạm nên dữ liệu gốc không bị biến đổi.

---

## 1. Tóm tắt Kết quả theo Nhóm Kiểm thử

| Nhóm kiểm thử | Số ca | Kết quả | Phạm vi đã xác minh |
| :--- | :---: | :---: | :--- |
| **1. Schema & EER Integrity** (`SCH-01..04`, `EXT-EER-01..03`) | 7 | **7/7 PASS** | Đủ 13 bảng, 2 Views, 2 Triggers, 4 B-Tree Indexes; `0` chồng lấn `MOVIE ∩ TV_SERIES`; `0` content mồ côi trên toàn bộ 8.817 tựa phim; `0` sai lệch `episode_id → content_id` (`f3`). |
| **2. Negative Cases trong Báo cáo** (`TC-01..05`) | 5 | **5/5 PASS** | Khớp 100% Bảng 5.1 báo cáo: Error `1644` (BR-01, BR-09), `1062` (Weak Entity season), `1451` (ON DELETE RESTRICT), `3819` (CHECK duration). |
| **3. Positive & Boundary Cases** (`EXT-POS-01..04`) | 4 | **4/4 PASS** | Gói Standard thêm được hồ sơ thứ 3 và chặn thứ 4 (`1644`); hồ sơ Kids xem được `PG-13` và bị chặn `NC-17` (`1644`); TV Series lưu được nhiều tập khác nhau và chặn trùng tập (`1062`); cận biên năm `1888` / `duration=1` / `stopped=0` hợp lệ. |
| **4. Extended Negative Constraints** (`EXT-NEG-01..12`) | 13 | **13/13 PASS** | Phủ bổ sung `UNIQUE` (`email`, `profile_name`, `episode_number`, `watchlist` → `1062`), `CHECK` (`account_status`, `rating_age`, `content_type`, `release_year`, `stopped_pos`, `max_profiles_allowed` → `3819`), `ON DELETE RESTRICT` (`language`, `genre` → `1451`), và khóa ngoại không tồn tại (`1452`). |
| **5. Referential Integrity `ON DELETE CASCADE`** (`EXT-CAS-01..02`) | 2 | **2/2 PASS** | Xóa `USER_ACCOUNT` tự xóa sạch `PROFILE`, `WATCHLIST`, `WATCH_HISTORY`; xóa `CONTENT` tự xóa sạch `TV_SERIES`, `SEASON`, `TV_EPISODE`, `CONTENT_GENRE`. |
| **6. Bảo mật RBAC thực tế** (`EXT-RBAC-01..03`) | 3 | **3/3 PASS** | Thực thi thật bằng tài khoản gán `role_streaming_client` (chặn `DELETE watch_history` và `UPDATE content` với MySQL Error `1142`) và `role_content_manager` (chặn `SELECT user_account` với Error `1142`). |
| **7. Truy vấn (`03_queries.sql`), Views & 4 Indexes** (`QRY-01..10`, `VIEW-01..02`, `IDX-01..04`) | 16 | **16/16 PASS** | Cả 10 truy vấn đều trả dữ liệu và chạy dưới ngưỡng **< 200ms** (`3.62 ms` đến `117.29 ms`) trên 86.895 dòng; cả 4 B-Tree Indexes đều được MySQL Optimizer sử dụng (`0.25 ms` – `1.19 ms`). |
| **8. Tích hợp 3-Tier Flask REST API** (`API-01..06`) | 6 | **6/6 PASS** | `/api/health`, truyền thông điệp Trigger `45000` (`is_trigger=True`), chặn xóa hồ sơ cuối cùng (`BR-01`), lọc an toàn trẻ em (`/api/catalog?kids=true`), và Read-Only SQL Sandbox chặn `DROP TABLE`. |
| **Tổng cộng** | **56** | **56/56 PASS** | **100% ca kiểm thử đạt trên MySQL 8.0.46 thật** |

---

## 2. Kết quả đo Hiệu năng 10 Truy vấn & 4 Chỉ mục trên 86.895 Bản ghi

| Mã | Đối tượng kiểm thử | Số dòng kết quả | Thời gian đo thực tế | Ghi chú EXPLAIN / Đánh giá |
| :---: | :--- | :---: | :---: | :--- |
| `QRY-01` | Phim lẻ 4K kèm ngôn ngữ & thể loại | 2.458 | `41.50 ms` | Đạt (< 200ms) |
| `QRY-02` | Phân cấp 4 bảng EER TV Series → Episode | 7.128 | `39.86 ms` | Đạt (< 200ms) |
| `QRY-03` | Continue Watching (`is_completed = FALSE`) | 141 | `3.62 ms` | Đạt (< 200ms) |
| `QRY-04` | Top 5 nội dung lượt xem cao nhất | 5 | `30.06 ms` | Đạt (< 200ms) |
| `QRY-05` | Doanh thu & thuê bao ACTIVE theo gói | 3 | `16.69 ms` | Đạt (< 200ms) |
| `QRY-06` | Tổng phút xem & tỷ lệ hoàn tất theo Profile | 13.692 | `117.29 ms` | Đạt (< 200ms) |
| `QRY-07` | Phim trong Watchlist chưa từng xem (`NOT EXISTS`) | 4.817 | `15.54 ms` | Đạt (< 200ms) |
| `QRY-08` | Phim lẻ dài hơn thời lượng trung bình | 2.930 | `6.04 ms` | Đạt (< 200ms) |
| `QRY-09` | Mức độ phổ biến từng Thể loại (`HAVING`) | 48 | `32.45 ms` | Đạt (< 200ms) |
| `QRY-10` | Lọc danh mục an toàn Trẻ em (`NOT IN R, NC-17`) | 4.720 | `109.26 ms` | Đạt (< 200ms) |
| `IDX-01` | `idx_content_title` (`WHERE title LIKE 'Inception%'`) | 2 | `0.38 ms` | `type=range`, `key=idx_content_title` |
| `IDX-02` | `idx_watch_history_last_watched` (`profile_id = 1`) | 2 | `0.25 ms` | `type=ref`, `key=idx_watch_history_last_watched` |
| `IDX-03` | `idx_content_type_year` (`MOVIE` & `>= 2020`) | 797 | `1.19 ms` | `type=range`, `key=idx_content_type_year` |
| `IDX-04` | `idx_content_rating` (`rating_age = 'G'`) | 569 | `1.13 ms` | `type=ref`, `key=idx_content_rating` |

---

## 3. Ghi chú Ranh giới Thiết kế (Để trả lời Vấn đáp)

1. **Ràng buộc cận dưới `BR-01` (tối thiểu 1 Profile) & Khử trùng lặp phim lẻ (`episode_id IS NULL`):** Do trong MySQL chuẩn ràng buộc `UNIQUE (profile_id, content_id, episode_id)` cho phép nhiều giá trị `NULL` và Trigger `BEFORE DELETE` trên bảng con dễ xung đột với `ON DELETE CASCADE` khi xóa tài khoản cha, hệ thống kiểm soát 2 quy tắc này trong tầng ứng dụng (`web-ui/server.py`, đã xác minh qua `API-04` và Transaction `DELETE + INSERT`).
2. **Phạm vi Trigger:** 2 Trigger (`trg_check_profile_limit_before_insert`, `trg_check_kids_rating_before_watch`) bảo vệ thao tác `INSERT`. Với thao tác `UPDATE` (ví dụ đổi gói thuê bao hoặc đổi `is_kids`), có thể mở rộng thêm `BEFORE UPDATE` Trigger ở phiên bản sau.
3. **Thuộc tính dẫn xuất `tv_series.total_seasons`:** Được giữ có chủ đích theo chiến lược *Controlled Denormalization* nhằm tăng tốc đọc danh mục phim và được đồng bộ tự động tại tầng ứng dụng khi thêm mùa mới (`POST /api/admin/seasons`).
