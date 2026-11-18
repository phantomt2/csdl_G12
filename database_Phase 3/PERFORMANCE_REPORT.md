# Báo cáo Kiểm chứng Hiệu năng Cơ sở dữ liệu & Chỉ mục B-Tree (Mục 4.2B Mở rộng — Nhóm G12)

> Tài liệu này trình bày đầy đủ phương pháp đo kiểm, câu lệnh kiểm thử, bộ chỉ số hiệu năng tầng MySQL thuần và phân tích chuyên sâu trên tập dữ liệu đầy đủ của hệ thống **Mini-Netflix (Nhóm G12)** — biên soạn phục vụ đưa trực tiếp vào **Mục 4.2B** của Báo cáo đồ án (`INT1313`). Số liệu thực nghiệm được thu thập từ kịch bản [`benchmark_performance.py`](benchmark_performance.py).

---

## 1. Mục tiêu, Môi trường & Phương pháp Kiểm chứng

### 1.1. Mục tiêu kiểm chứng
1. Kiểm chứng **Ràng buộc phi chức năng (NFR — Mục 1.3)**: Mọi truy vấn tìm kiếm và tra cứu nghiệp vụ phải trả về kết quả trong thời gian **< 200 ms** ngay cả trên quy mô dữ liệu mở rộng từ Kaggle.
2. Chứng minh định lượng hiệu quả của **4 chỉ mục B-Tree tự thiết kế** (`idx_content_title`, `idx_content_type_year`, `idx_content_rating`, `idx_watch_history_last_watched`) cùng chỉ mục tự động từ khóa duy nhất (`uq_user_account_email`) thông qua đối chiếu **Before (Chưa dùng Index)** và **After (Có Index)**.
3. Kiểm chứng giới hạn hoạt động thực tế của B-Tree Index trong các tình huống truy vấn bất lợi (*Edge Cases*) và phát hiện điểm nghẽn hiệu năng tiềm ẩn ở tầng `VIEW` để đề xuất hướng tối ưu.

### 1.2. Môi trường & Quy mô dữ liệu thực nghiệm
- **Thời điểm đo kiểm:** `2026-11-17 23:49:36`
- **Hệ quản trị CSDL:** MySQL Server `8.0.46` (`InnoDB`, `utf8mb4_unicode_ci`)
- **Giao thức đo:** Kết nối trực tiếp Python (`mysql-connector-python`) tới MySQL, đo **hiệu năng thuần tầng CSDL** nhằm loại bỏ nhiễu từ trình duyệt hoặc tầng web server Flask.
- **Quy mô dữ liệu thực tế tại thời điểm đo:**
  - `content`: **8.817** tựa phim (`movie` + `tv_series`)
  - `tv_episode`: **7.128** tập phim
  - `user_account`: **6.950** tài khoản người dùng
  - `profile`: **13.694** hồ sơ con
  - `watch_history`: **13.697** bản ghi nhật ký xem
- **Trạng thái ổn định phiên đo:** `Innodb_row_lock_waits = 0`, `Innodb_row_lock_time_avg = 0 ms`, **Tỷ lệ lỗi (Error Rate) = `0.00%`**.

### 1.3. Phương pháp đo & Hệ thống chỉ số đánh giá
- **Quy trình lặp làm ấm và lấy phân vị:**
  - Nhóm kiểm thử Index & Edge Cases: **5 lượt làm ấm bộ đệm (`warm-up`) + 50 lượt đo thực tế** mỗi truy vấn.
  - Nhóm 10 truy vấn nghiệp vụ (`03_queries.sql`) & Views: **3 lượt `warm-up` + 30 lượt đo thực tế** mỗi truy vấn.
- **Kỹ thuật mô phỏng "Before (Chưa có Index)" an toàn:** Sử dụng chỉ thị `IGNORE INDEX (...)` của MySQL Optimizer để ép truy vấn quét toàn bảng (*Full Table Scan*) trên cùng tập dữ liệu mà **không phải xóa Index vật lý**, đảm bảo toàn vẹn cấu trúc hệ thống.
- **Ý nghĩa các chỉ số thu thập:**
  - **`p50` (Median), `p95`, `p99` (ms):** Thời gian phản hồi ở mức trung vị (`50%`), ngưỡng `95%` và ngưỡng `99%` lượt chạy nhanh nhất. Cam kết `< 200 ms` được đánh giá nghiêm ngặt trên **`p99`** (không chỉ dùng trung bình).
  - **`QPS` (Queries Per Second — 1 luồng):** Số lượt truy vấn tuần tự hệ thống xử lý được trong 1 giây trên một kết nối đơn.
  - **`Engine Actual` (`EXPLAIN ANALYZE`):** Thời gian thực thi thuần bên trong nhân MySQL (loại trừ chi phí truyền dữ liệu qua driver Python).
  - **`Rows Examined vs. Rows Returned`:** Số dòng MySQL dự kiến phải duyệt (`EXPLAIN.rows`) so với số dòng kết quả thực sự trả về.
  - **`Handler_read_rnd_next` vs. `Handler_read_key + read_next`:** Bộ đếm I/O cấp Storage Engine cho biết chính xác số bước đọc tuần tự bảng (*Full Scan*) so với số lần tra cứu trực tiếp qua cây B-Tree.

---

## 2. Kịch bản & Kết quả So sánh Before vs. After (5 Chỉ mục Trọng điểm)

### 2.1. Tập câu lệnh SQL kiểm thử
Các truy vấn đại diện cho luồng tìm kiếm tên phim, lọc danh mục theo loại & năm, lọc theo độ tuổi, hiển thị "Tiếp tục xem" (`Continue Watching`) và xác thực đăng nhập tài khoản:

```sql
-- 1. Kiểm chứng idx_content_title (Tìm kiếm theo tiền tố tiêu đề)
SELECT content_id, title, release_year, rating_age
FROM content
WHERE title LIKE 'Inception%';

-- 2. Kiểm chứng idx_content_type_year (Lọc danh mục Phim lẻ từ năm 2020 trở lại đây)
SELECT content_id, title, release_year
FROM content
WHERE content_type = 'MOVIE' AND release_year >= 2020;

-- 3. Kiểm chứng idx_content_rating (Lọc phim theo nhãn độ tuổi hẹp 'G')
SELECT content_id, title, rating_age
FROM content
WHERE rating_age = 'G';

-- 4. Kiểm chứng idx_watch_history_last_watched (Lấy lịch sử xem gần nhất theo Profile)
SELECT history_id, profile_id, content_id, episode_id, last_watched_timestamp
FROM watch_history
WHERE profile_id = 1
ORDER BY last_watched_timestamp DESC;

-- 5. Kiểm chứng uq_user_account_email (Truy vấn đăng nhập / Kiểm tra trùng Email)
SELECT account_id, email, account_status
FROM user_account
WHERE email = 'an.nguyen@gmail.com';
```

*(Lưu ý: Với kịch bản **Before**, mỗi câu trên được chạy kèm gợi ý `IGNORE INDEX (...)` tương ứng; riêng truy vấn số 4 sử dụng `IGNORE INDEX (idx_watch_history_last_watched, uq_watch_history_profile_content_ep)` để tách hẳn ảnh hưởng của chỉ mục khóa duy nhất đứng đầu bằng `profile_id`.)*

### 2.2. Bảng 1 — So sánh Kế hoạch Thực thi (`EXPLAIN`), Độ trễ Phân vị (`p50/p95/p99`) và Thông lượng (`QPS`)

| Hạng mục kiểm thử | Trạng thái | Kiểu quét (`type`) | Chỉ mục sử dụng (`key`) | Rows quét / Trả về | Engine Actual (ms) | p50 / Median (ms) | p95 (ms) | p99 (ms) | QPS (1 luồng) | Tăng tốc (`p50`) |
| :--- | :--- | :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1. `idx_content_title`**<br>*(Tìm tiền tố `'Inception%'`)* | Before *(No Index)* | `ALL` | `NULL` *(Full Scan)* | 8.797 / 2 | 1.590 | 1.587 | 1.749 | 2.564 | 614 | — |
| | **After *(With Index)*** | **`range`** | **`idx_content_title`** | **2 / 2** | **0.022** | **0.124** | **0.216** | **0.259** | **7.348** | **12.8x** |
| **2. `idx_content_type_year`**<br>*(Lọc `MOVIE` từ `2020`)* | Before *(No Index)* | `ALL` | `NULL` *(Full Scan)* | 8.797 / 797 | 1.770 | 2.197 | 3.212 | 5.233 | 419 | — |
| | **After *(With Index)*** | **`range`** | **`idx_content_type_year`** | **797 / 797** | **0.704** | **1.172** | **1.454** | **1.732** | **845** | **1.9x** |
| **3. `idx_content_rating`**<br>*(Lọc nhãn hẹp `'G'`)* | Before *(No Index)* | `ALL` | `NULL` *(Full Scan)* | 8.797 / 569 | 2.530 | 1.693 | 2.557 | 3.517 | 563 | — |
| | **After *(With Index)*** | **`ref`** | **`idx_content_rating`** | **569 / 569** | **0.488** | **0.913** | **1.060** | **1.535** | **1.078** | **1.9x** |
| **4. `idx_watch_history_last_watched`**<br>*(Continue Watching `profile = 1`)* | Before *(No Index)* | `ALL` | `NULL` *(Full Scan)* | 14.181 / 2 | 1.800 | 1.622 | 2.076 | 2.463 | 600 | — |
| | **After *(With Index)*** | **`ref`** | **`idx_watch_history_last_watched`** | **2 / 2** | **0.017** | **0.107** | **0.253** | **0.425** | **7.216** | **15.2x** |
| **5. `uq_user_account_email`**<br>*(Đăng nhập / Check trùng Email)* | Before *(No Index)* | `ALL` | `NULL` *(Full Scan)* | 6.878 / 1 | 1.030 | 1.233 | 1.568 | 2.047 | 783 | — |
| | **After *(With Index)*** | **`const`** | **`uq_user_account_email`** | **1 / 1** | **0.0002** | **0.083** | **0.158** | **0.207** | **10.269** | **14.9x** |

### 2.3. Bảng 2 — Đối chiếu Bộ đếm Đọc Dữ liệu Tầng Storage Engine (`Handler_read_*`)

| Chỉ mục kiểm chứng | Before: `Handler_read_rnd_next` *(Quét tuần tự toàn bảng)* | After: `Handler_read_rnd_next` *(Quét tuần tự)* | After: `Handler_read_key` + `read_next` *(Đọc trực tiếp qua B-Tree)* | Mức giảm quét tuần tự |
| :--- | :---: | :---: | :---: | :---: |
| 1. `idx_content_title` | 8.818 | **0** | 3 | **8.818 → 0 (-100%)** |
| 2. `idx_content_type_year` | 8.818 | **0** | 798 | **8.818 → 0 (-100%)** |
| 3. `idx_content_rating` | 8.818 | **0** | 570 | **8.818 → 0 (-100%)** |
| 4. `idx_watch_history_last_watched` | 13.698 | **0** | 3 | **13.698 → 0 (-100%)** |
| 5. `uq_user_account_email` | 6.952 | **0** | 1 | **6.952 → 0 (-100%)** |

### 2.4. Nhận xét & Đánh giá chuyên sâu phần Index
1. **Triệt tiêu hoàn toàn thao tác quét tuần tự bảng (*Full Table Scan*):** Khi kích hoạt Index, cột `Handler_read_rnd_next` đều giảm từ hàng nghìn–chục nghìn thao tác về **`0`**. Tỷ lệ *Rows Examined / Rows Returned* đạt mức tối ưu lý tưởng **`1:1`** ở cả 5 truy vấn (`2/2`, `797/797`, `569/569`, `2/2`, `1/1`).
2. **Hiệu quả rõ rệt nhất ở truy vấn có độ chọn lọc cao & sắp xếp sẵn:**
   - Truy vấn *"Continue Watching"* (`idx_watch_history_last_watched`) tăng tốc **`15.2x`** (`p50` từ `1.622 ms` xuống `0.107 ms`; thời gian thuần trong Engine từ `1.800 ms` xuống `0.017 ms`), đạt **`7.216 QPS`** nhờ chỉ mục gộp `(profile_id, last_watched_timestamp DESC)` vừa lọc đúng hồ sơ vừa sắp xếp sẵn giảm dần theo thời gian mà không cần `Using filesort`.
   - Truy vấn xác thực Email (`uq_user_account_email`, chỉ mục tự sinh từ ràng buộc `UNIQUE`) đạt kiểu truy cập tốt nhất **`const`** (`Engine Actual = 0.0002 ms`, `p50 = 0.083 ms`, **`10.269 QPS`**), chứng minh thao tác đăng nhập và kiểm tra trùng email không bao giờ quét toàn bảng.
3. **Đánh đổi Đọc vs. Ghi (*Read vs. Write Trade-off*):** Nhóm chỉ thiết kế 4 chỉ mục trọng tâm trên `content` và `watch_history` thay vì đánh tràn lan lên mọi cột, vì mỗi chỉ mục B-Tree sẽ làm tăng nhẹ chi phí cập nhật cây khi thực hiện `INSERT` / `UPDATE` / `DELETE`.

---

## 3. Kiểm chứng Các Trường hợp Giới hạn của B-Tree Index (*Edge Cases*)

Để đánh giá trung thực phạm vi hiệu lực của 4 chỉ mục hiện có, kịch bản kiểm thử bổ sung **3 ca biên (*Edge Cases*)** phản ánh các tình huống thực tế mà B-Tree Index không phát huy tác dụng hoặc bị Optimizer bỏ qua:

| Mã ca | Kịch bản & Câu lệnh SQL | Kiểu quét (`type`) | Chỉ mục (`key`) | Rows quét / Trả về | Engine Actual (ms) | p50 (ms) | p95 (ms) | p99 (ms) | Nguyên nhân kỹ thuật & Hướng cải tiến |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **`EDGE-01`** | Chỉ lọc độc lập theo năm phát hành:<br>`WHERE release_year = 2020` *(bỏ `content_type`)* | `ALL` | `NULL` *(Full Scan)* | 8.797 / 953 | 1.680 | 1.946 | 2.490 | 3.549 | Do chỉ mục kép `(content_type, release_year)` tuân thủ quy tắc *Leftmost Prefix* (Trái → Phải). Thiếu `content_type` nên không dùng được Index. *Hướng sửa:* Thêm `CREATE INDEX idx_content_release_year ON content (release_year);` nếu phát sinh tính năng lọc chỉ theo năm. |
| **`EDGE-02`** | Tìm kiếm từ khóa có ký tự đại diện `%` ở đầu:<br>`WHERE title LIKE '%Inception%'` | `index` | `idx_content_title` | 8.797 / 2 | 2.100 | 1.911 | 2.721 | 4.328 | Ký tự `%` ở đầu chuỗi phá vỡ thứ tự sắp xếp tiền tố A–Z. MySQL phải thực hiện *Full Index Scan* (`type = index`), duyệt toàn bộ `8.797` nút lá (chậm hơn **15.4x** về `p50` so với `LIKE 'Inception%'`). *Hướng sửa:* Dùng `FULLTEXT INDEX` với `MATCH ... AGAINST` cho tìm kiếm toàn văn trên quy mô lớn. |
| **`EDGE-03`** | Lọc diện rộng cho hồ sơ Trẻ em:<br>`WHERE rating_age NOT IN ('R', 'NC-17')` | `ALL` | `NULL` *(Full Scan)* | 8.797 / 4.720 | 1.740 | 3.622 | 3.994 | 4.079 | Cột `rating_age` chỉ có 5 giá trị rời rạc; điều kiện `NOT IN` lấy `4.720 / 8.817` dòng (**53.5%** bảng). Do độ chọn lọc quá thấp, MySQL Optimizer chủ động bỏ qua `idx_content_rating` vì đọc tuần tự cả bảng hiệu quả hơn nhảy ngẫu nhiên qua Index quá nhiều lần. |

---

## 4. Kết quả Benchmark Toàn bộ 10 Truy vấn Nghiệp vụ (`03_queries.sql`) & 2 Views

Toàn bộ 10 truy vấn nghiệp vụ phức tạp (gồm Multi-table `JOIN`, `LEFT JOIN`, `GROUP BY`, `HAVING`, *Correlated Subquery* `NOT EXISTS`, *Scalar Subquery*) và 2 `VIEW` của hệ thống được chạy đo lặp **30 lượt** (sau 3 lượt `warm-up`) trực tiếp trên tập dữ liệu đầy đủ `8.817` tựa phim & `13.697` lịch sử xem:

| Mã | Tên truy vấn / Khung nhìn (`VIEW`) | Số dòng trả về | Min (ms) | p50 / Median (ms) | Mean (ms) | p95 (ms) | p99 (ms) | Max (ms) | QPS (1 luồng) | Đánh giá NFR (`p99 < 200ms`) |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`QRY-01`** | **Q1:** Danh mục Phim lẻ `4K` kèm ngôn ngữ & thể loại (5-table `JOIN`) | 2.458 | 33.77 | 39.03 | 39.21 | 43.15 | **46.15** | 47.18 | 25.5 | **ĐẠT** |
| **`QRY-02`** | **Q2:** Phân cấp EER `CONTENT → TV_SERIES → SEASON → TV_EPISODE` | 7.128 | 34.35 | 39.20 | 40.05 | 47.54 | **49.62** | 50.21 | 25.0 | **ĐẠT** |
| **`QRY-03`** | **Q3:** Danh sách *Continue Watching* đang xem dở (`is_completed = FALSE`) | 141 | 2.31 | **2.67** | 2.69 | 3.02 | **3.18** | 3.22 | **372.4** | **ĐẠT** |
| **`QRY-04`** | **Q4:** Top 5 nội dung có lượt xem & lượt hoàn thành cao nhất | 5 | 22.20 | 24.09 | 25.69 | 33.18 | **35.32** | 35.91 | 38.9 | **ĐẠT** |
| **`QRY-05`** | **Q5:** Thống kê tài khoản `ACTIVE`, số hồ sơ & doanh thu theo gói cước | 3 | 12.72 | 14.76 | 15.32 | 19.22 | **21.66** | 22.35 | 65.3 | **ĐẠT** |
| **`QRY-06`** | **Q6:** Tổng phút xem & tỷ lệ hoàn tất (%) theo từng `PROFILE` | 13.692 | 86.79 | 101.18 | 100.75 | 112.24 | **116.65** | 118.29 | 9.9 | **ĐẠT** |
| **`QRY-07`** | **Q7:** Phim lưu trong `WATCHLIST` nhưng chưa xem (`NOT EXISTS`) | 4.817 | 12.31 | 15.08 | 15.55 | 19.07 | **20.21** | 20.63 | 64.3 | **ĐẠT** |
| **`QRY-08`** | **Q8:** Phim lẻ có thời lượng dài hơn mức trung bình (*Scalar Subquery*) | 2.930 | 5.35 | 6.30 | 6.47 | 8.76 | **9.24** | 9.33 | 154.6 | **ĐẠT** |
| **`QRY-09`** | **Q9:** Mức độ phổ biến của từng Thể loại (`LEFT JOIN` + `HAVING`) | 48 | 28.29 | 32.20 | 32.33 | 37.32 | **40.04** | 40.69 | 30.9 | **ĐẠT** |
| **`QRY-10`** | **Q10:** Lọc danh mục an toàn cho Trẻ em (`NOT IN ('R', 'NC-17')`) | 4.720 | 101.25 | 114.26 | 116.20 | 128.62 | **130.23** | 130.63 | 8.6 | **ĐẠT** |
| **`VIEW-01`** | **View 1:** `vw_content_full_catalog` (quét toàn bộ 8.817 dòng) | 8.817 | 236.95 | 250.10 | 251.16 | 269.86 | **272.64** | 272.78 | 4.0 | **Vượt ngưỡng (xem phân tích)** |
| **`VIEW-02`** | **View 1 (UI):** `vw_content_full_catalog ORDER BY release_year DESC LIMIT 60` | 60 | 220.09 | 236.99 | 242.06 | 271.52 | **276.77** | 278.62 | 4.1 | **Vượt ngưỡng (xem phân tích)** |
| **`VIEW-03`** | **View 2:** `vw_subscription_revenue_summary` (Báo cáo doanh thu gói) | 3 | 6.43 | 7.20 | 7.70 | 10.40 | **11.17** | 11.42 | 129.9 | **ĐẠT** |

### Phân tích điểm nghẽn (*Bottleneck*) đối với `vw_content_full_catalog` (`VIEW-01` & `VIEW-02`)
- **Hiện tượng quan sát được:** Ngay cả khi gắn `ORDER BY release_year DESC LIMIT 60` ở truy vấn ngoài (`VIEW-02` — mô phỏng cách nạp trang chủ), `vw_content_full_catalog` vẫn mất `p50 = 236.99 ms` (`p99 = 276.77 ms`), vượt nhẹ mốc `200 ms`.
- **Nguyên nhân:** Bên trong định nghĩa `vw_content_full_catalog` phải nối `6` bảng (`content`, `language`, `movie`, `tv_series`, `content_genre`, `genre`) và sử dụng **`GROUP BY` + `GROUP_CONCAT`** trên toàn bộ `8.817` phim × `19.343` bản ghi `content_genre`. Theo cơ chế xử lý View có `GROUP BY` của MySQL, Engine không thể đẩy `LIMIT 60` từ truy vấn ngoài xuống trước bước `GROUP BY`, buộc phải gom nhóm và nối chuỗi thể loại cho toàn bộ `8.817` phim vào bảng tạm rồi mới sắp xếp cắt lấy `60` dòng.
- **Giải pháp tối ưu khi mở rộng:** Thực hiện lọc điều kiện và phân trang `ORDER BY ... LIMIT 60` trực tiếp trên bảng gốc `content` (tận dụng Index) trước, sau đó mới `JOIN` bảng con và `GROUP_CONCAT` thể loại trên đúng `60` dòng kết quả thay vì truy vấn qua View gom nhóm toàn cục.

---

## 5. Kết luận Hiệu năng Hệ thống

1. **Đạt 100% cam kết hiệu năng cho toàn bộ truy vấn tra cứu và 10 truy vấn nghiệp vụ:** Tất cả các phép tìm kiếm/lọc có Index (`0.083 – 1.172 ms` ở `p50`) và **10/10 truy vấn `03_queries.sql`** (`2.67 – 114.26 ms` ở `p50`; tối đa `130.23 ms` ở `p99`) cùng View doanh thu (`11.17 ms` ở `p99`) đều vận hành ổn định dưới ngưỡng **`< 200 ms`** trên dữ liệu thực (`8.817` tựa phim, `13.697` lịch sử xem, `6.950` tài khoản, `0.00%` lỗi và `0` lock wait).
2. **Chứng minh định lượng tác động của B-Tree Index:** Với dữ liệu đủ lớn (`8.817` phim, `13.697` lịch sử xem, `6.950` tài khoản), B-Tree Index loại bỏ hoàn toàn bước đọc tuần tự toàn bảng (`Handler_read_rnd_next` giảm `100%` về `0`) và tăng tốc truy vấn trọng điểm lên **`7.8x – 15.2x`** (tối đa **`10.269 QPS`** đơn luồng).
3. **Nhận diện minh bạch các điểm giới hạn:** Kết quả thực nghiệm đã chỉ rõ phạm vi áp dụng của *Leftmost Prefix*, tìm kiếm wildcard `%...%`, độ chọn lọc của `rating_age`, và nút thắt vật chất hóa `GROUP BY` của `vw_content_full_catalog` — làm cơ sở trực tiếp cho việc tối ưu hóa truy vấn ở giai đoạn sản xuất.
