# Tập dữ liệu Dự án Mini-Netflix (Nhóm G12)

Thư mục này lưu trữ các tệp dữ liệu nguồn thô từ Kaggle cùng thống kê chi tiết dữ liệu đã chuẩn hóa và nạp vào MySQL qua kịch bản [`database_Phase 3/02_mock_data.sql`](../database_Phase%203/02_mock_data.sql).

## 1. Nguồn dữ liệu gốc (Raw Kaggle Datasets)

| Tên tệp | Nguồn gốc | Số bản ghi gốc | Vai trò trong đồ án |
| :--- | :--- | :---: | :--- |
| `netflix_titles.csv.zip` (`netflix_titles.csv`) | Kaggle — Netflix Movies and TV Shows | **8.807** | Cung cấp danh mục phim lẻ (`MOVIE`), phim bộ (`TV_SERIES`), năm phát hành, phân loại độ tuổi MPAA, mô tả và thể loại để chuẩn hóa vào `content`, `movie`, `tv_series`, `season`, `tv_episode`, `genre`, `content_genre`, `language`. |
| `netflix_users.csv` | Kaggle — Netflix Users Database | **13.685** | Cung cấp thông tin người dùng, gói thuê bao, thể loại ưa thích và hành vi xem để tổng hợp thành `user_account`, `profile`, `watchlist`, `watch_history`. |

## 2. Thống kê quy mô dữ liệu trong `02_mock_data.sql` (86.895 bản ghi)

Tệp [`database_Phase 3/02_mock_data.sql`](../database_Phase%203/02_mock_data.sql) kết hợp **tập dữ liệu mẫu cốt lõi** (dùng minh họa trực quan trong báo cáo & kiểm thử ràng buộc) và **dữ liệu mở rộng chuẩn hóa từ Kaggle**:

| STT | Bảng CSDL | Tổng số dòng | Ghi chú thành phần |
| :---: | :--- | :---: | :--- |
| 1 | `subscription_tier` | 3 | 3 gói cước chuẩn (`Basic`, `Standard`, `Premium`) |
| 2 | `language` | 11 | Danh mục mã ngôn ngữ chuẩn ISO 639-1 (`vi`, `en`, `ko`, `ja`, `es`, `fr`, `hi`, `zh`, `de`, `th`, `it`) |
| 3 | `genre` | 48 | 6 thể loại cốt lõi + 42 thể loại chuẩn hóa từ cột `listed_in` của Kaggle |
| 4 | `user_account` | 6.950 | 5 tài khoản mẫu cốt lõi (`1..5`) + 6.945 tài khoản mở rộng |
| 5 | `profile` | 13.694 | 9 hồ sơ mẫu cốt lõi + 13.685 hồ sơ từ Kaggle Users |
| 6 | `content` | 8.817 | 10 tựa phim mẫu cốt lõi + 8.807 tựa phim từ `netflix_titles.csv` |
| 7 | `content_genre` | 19.343 | Bảng tách đa trị M:N giữa `CONTENT` và `GENRE` (chuẩn 1NF) |
| 8 | `movie` | 6.137 | 6 phim mẫu cốt lõi + 6.131 Movie từ Kaggle |
| 9 | `tv_series` | 2.680 | 4 series mẫu cốt lõi + 2.676 TV Show từ Kaggle |
| 10 | `season` | 3.565 | Các mùa phim được chuẩn hóa cho các `TV_SERIES` |
| 11 | `tv_episode` | 7.128 | Các tập phim thuộc từng `SEASON` (thực thể yếu) |
| 12 | `watchlist` | 4.822 | Danh sách xem sau theo từng `PROFILE` |
| 13 | `watch_history` | 13.697 | 12 lịch sử xem mẫu cốt lõi + 13.685 lịch sử xem mở rộng |
| — | **Tổng cộng** | **86.895** | Toàn bộ tuân thủ đầy đủ ràng buộc PK, FK, CHECK, UNIQUE |

## 3. Cách nạp dữ liệu vào MySQL

- **Cách tự động (Python):** Chạy `python web-ui/setup_database.py --reset` để tự động tạo schema (`01_schema.sql`) và nạp toàn bộ `02_mock_data.sql`.
- **Cách thủ công (MySQL Workbench):** Chạy `database_Phase 3/01_schema.sql` trước, sau đó mở và chạy `database_Phase 3/02_mock_data.sql`.
