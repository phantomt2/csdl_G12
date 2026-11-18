# Đồ án Cơ sở dữ liệu (INT1313) — Mini-Netflix (Nhóm G12)

Hệ thống Quản lý và Khai thác Cơ sở dữ liệu Phim Trực tuyến (*On-Demand Streaming Platform — Mini-Netflix*), xây dựng trên **MySQL 8.0** (chuẩn hóa **3NF / BCNF**, mô hình kế thừa **EER Superclass/Subclass**) kết hợp ứng dụng Web Demo kiến trúc **3-Tier** (`HTML/TailwindCSS/JS` ↔ `Python Flask REST API` ↔ `MySQL`).

---

## 1. Thông tin Dự án & Repository

| Hạng mục | Thông tin chi tiết |
| :--- | :--- |
| **Trường / Cơ sở** | Học viện Công nghệ Bưu chính Viễn thông – Cơ sở tại TP.HCM (**PTITHCM**) |
| **Học phần** | Cơ sở dữ liệu (**INT1313**) |
| **Nhóm lớp học phần** | `2627.HK1-INT1313-DB-Nhóm 2` |
| **Khóa / Lớp chính quy** | `D25CQAT02-N` |
| **Đề tài** | **#2 On-Demand Streaming Platform (Mini-Netflix)** |
| **Nhóm thực hiện** | **Nhóm G12** |
| **Giảng viên hướng dẫn** | **Lê Hà Thanh** (`lehathanh@ptithcm.edu.vn`) |
| **Liên kết Repository** | https://github.com/phantomt2/csdl_G12 |
| **Nhánh chính (Default Branch)** | `main` |

---

## 2. Thành viên Nhóm & Phân công

> **Lưu ý về thành viên trên Repository:** Theo yêu cầu của học phần, ngoài 4 sinh viên thực hiện thuộc PTITHCM, giảng viên hướng dẫn **`lehathanh@ptithcm.edu.vn`** được bổ sung làm thành viên (Collaborator) trên repository để theo dõi và chấm đồ án.

| STT | Họ và tên | MSSV | Lớp / Khóa | Email sinh viên PTITHCM | GitHub | Vai trò / Phụ trách |
| :---: | :--- | :---: | :---: | :--- | :--- | :--- |
| 1 | **Trần Thanh Tùng** | `N25DCAT120` | `D25CQAT02-N` | `n25dcat120@student.ptithcm.edu.vn` | [@phantomt2](https://github.com/phantomt2) | `[NHÓM TRƯỞNG]` |
| 2 | **Đặng Hữu Tuấn** | `N25DCAT118` | `D25CQAT02-N` | `n25dcat118@student.ptithcm.edu.vn` | [@hutun321-oss](https://github.com/hutun321-oss) | `[THÀNH VIÊN]` |
| 3 | **Lê Bích Vân** | `N25DCAT121` | `D25CQAT02-N` | `n25dcat121@student.ptithcm.edu.vn` | [@cosima-hub](https://github.com/cosima-hub) | `[THÀNH VIÊN]` |
| 4 | **Lê Trương Vĩ** | `N25DCAT122` | `D25CQAT02-N` | `n25dcat122@student.ptithcm.edu.vn` | [@letruongvi](https://github.com/letruongvi) | `[THÀNH VIÊN]` |
| GV | **Lê Hà Thanh** | — | Giảng viên PTITHCM | `lehathanh@ptithcm.edu.vn` | — | Giảng viên hướng dẫn |

---

## 3. Cấu trúc Mã nguồn, Tài liệu & Báo cáo

```text
csdl_G12/
├── README.md                          # Tài liệu tổng quan dự án, thành viên & hướng dẫn triển khai (file này)
├── API_CONTRACT.md                    # Đặc tả chi tiết các REST API endpoints giữa Frontend & Flask Backend
├── .gitignore                         # Loại trừ file môi trường (.env), cache Python và file tạm
│
├── Phase 1/                           # Tài liệu phân tích Giai đoạn 1 (Miniworld, Glossary, BR/NFR, FR)
│   ├── section 1.1-tuan.md
│   ├── section 1.2-letruongvi.md
│   ├── section1_3_van.md
│   └── section 1.4-tung.md
│
├── phase 2/                           # Tài liệu thiết kế Giai đoạn 2 (Phân tích thực thể, Ánh xạ & Chuẩn hóa)
│   ├── phase2-TVSERIES_CONTENT_MOVIE.md
│   ├── phase2_season_episode_genre.md
│   ├── phase2_subscription_user_profile.md
│   └── phase2_watchlist_audio_subtitle_track.md
│
├── database_Phase 3/                  # Bộ kịch bản SQL hoàn chỉnh cho MySQL 8.0 (tổng 13 bảng)
│   ├── 01_schema.sql                  # DDL: 13 bảng, 16 CHECK, 8 UNIQUE, 14 FK, 4 Index, 2 Trigger, 2 View
│   ├── 02_mock_data.sql               # DML: 86.895 bản ghi mẫu cốt lõi + dữ liệu mở rộng chuẩn hóa từ Kaggle
│   ├── 03_queries.sql                 # 10 truy vấn nghiệp vụ nâng cao (JOIN, GROUP BY, HAVING, Subquery)
│   ├── 04_performance_test.sql        # Kiểm thử hiệu năng Before/After 5 chỉ mục & 3 Edge Cases (EXPLAIN ANALYZE)
│   ├── 05_rbac_security.sql           # Phân quyền RBAC (3 Roles: admin, content_manager, streaming_client)
│   ├── 06_negative_test_cases.sql     # 5 kịch bản kiểm thử chặn dữ liệu sai (TC-01 đến TC-05)
│   ├── 07_extended_test_cases.sql     # Kịch bản mở rộng: Positive, CHECK/UNIQUE, CASCADE, EER & RBAC test
│   ├── verify_database.py             # Script Python tự động chạy 56 ca kiểm thử DB & Flask API (ROLLBACK an toàn)
│   ├── benchmark_performance.py       # Script Python đo hiệu năng thuần MySQL (p50/p95/p99, QPS, Handler I/O)
│   ├── TEST_RESULTS.md                # Kết quả kiểm chứng tự động 56/56 PASS trên dữ liệu đầy đủ
│   └── PERFORMANCE_REPORT.md          # Báo cáo đo kiểm hiệu năng 5 chỉ mục, 3 Edge Cases, 10 truy vấn & Views
│
├── datasets/                          # Tập dữ liệu nguồn Kaggle & mô tả quy trình nạp dữ liệu
│   ├── README.md                      # Mô tả nguồn dữ liệu, ánh xạ cột và thống kê 86.895 bản ghi
│   ├── netflix_titles.csv.zip         # Tập dữ liệu gốc 8.807 tựa phim & TV series (Kaggle)
│   └── netflix_users.csv              # Tập dữ liệu gốc 13.685 người dùng & lịch sử xem (Kaggle)
│
├── web-ui/                            # Ứng dụng Web Demo 3-Tier (Flask REST API + HTML/Tailwind/JS)
│   ├── README.md                      # Hướng dẫn chi tiết kiến trúc Web UI & AI Setup Playbook
│   ├── server.py                      # Backend Flask API, giao tiếp 2 chiều MySQL & Dynamic Query Builder
│   ├── setup_database.py              # Script tự động kết nối MySQL và nạp 01_schema.sql + 02_mock_data.sql
│   ├── index.html                     # Giao diện người dùng (Profile Gate, Lọc đa thể loại, Watch History Logger)
│   ├── admin.html                     # Giao diện DBA Admin Console (Revenue View, Query Builder, DML, Triggers)
│   ├── requirements.txt               # Thư viện Python phụ thuộc (Flask, mysql-connector-python, python-dotenv)
│   └── .env.example                   # Mẫu biến môi trường kết nối MySQL (copy thành .env trước khi chạy)
│
└── report/                            # Báo cáo chi tiết đồ án (PDF)
    └── BÁO CÁO DỰ ÁN CƠ SỞ DỮ LIỆU- HỆ THỐNG PHIM TRỰC TUYẾN (MINI-NETFLIX) - NHÓM G12.pdf
```

> **Ghi chú về tài liệu:** Các thư mục `Phase 1/` và `phase 2/` lưu giữ sản phẩm làm việc ban đầu theo từng phân công của thành viên. Bản thiết kế hợp nhất cuối cùng (13 bảng, 9 Business Rules, 7 Functional Requirements, ERD/EER và toàn bộ SQL thực thi) được thống nhất đầy đủ trong [Báo cáo chi tiết (`report/`)](report/B%C3%81O%20C%C3%81O%20D%E1%BB%B0%20%C3%81N%20C%C6%A0%20S%E1%BB%9E%20D%E1%BB%AE%20LI%E1%BB%86U-%20H%E1%BB%86%20TH%E1%BB%90NG%20PHIM%20TR%E1%BB%B0C%20TUY%E1%BA%BEN%20%28MINI-NETFLIX%29%20-%20NH%C3%93M%20G12.pdf) và [database_Phase 3/](database_Phase%203/).

---

## 4. Điểm nhấn Thiết kế Cơ sở dữ liệu

- **Mô hình EER Superclass / Subclass (`BR-03`):** `CONTENT` là lớp cha tổng quát, chuyên biệt hóa rời rạc (Disjoint) và toàn phần (Total) thành `MOVIE` và `TV_SERIES` bằng cặp khóa `content_id` vừa là `PK` vừa là `FK` tham chiếu về `CONTENT(content_id)` (`ON DELETE CASCADE`).
- **Thực thể yếu lồng nhau (`BR-02`, `BR-04`, `BR-08`):** `PROFILE` phụ thuộc `USER_ACCOUNT`; `TV_EPISODE` phụ thuộc `SEASON`, `SEASON` phụ thuộc `TV_SERIES` — bảo toàn tính duy nhất theo bộ khóa tự nhiên bằng `UNIQUE` và xóa lan truyền `ON DELETE CASCADE`.
- **Chuẩn hóa 1NF → 3NF / BCNF:** 12/13 bảng đạt chuẩn **BCNF**; riêng `WATCH_HISTORY` đạt **3NF** và lưu tiến trình xem từng tập qua khóa `UNIQUE (profile_id, content_id, episode_id)` (`BR-06`).
- **Tự động hóa & Bảo mật ở tầng CSDL:**
  - `trg_check_profile_limit_before_insert`: Chặn tạo quá `max_profiles_allowed` theo gói cước (`Basic: 1`, `Standard: 3`, `Premium: 5`) bằng `SIGNAL SQLSTATE '45000'`.
  - `trg_check_kids_rating_before_watch`: Chặn hồ sơ trẻ em (`is_kids = TRUE`) xem nội dung nhãn `R` hoặc `NC-17` (`BR-09`).
  - `vw_content_full_catalog` & `vw_subscription_revenue_summary`: Hai Views tổng hợp danh mục EER và báo cáo doanh thu thuê bao `ACTIVE`.
  - `05_rbac_security.sql`: Định nghĩa 3 Roles (`role_system_admin`, `role_content_manager`, `role_streaming_client`) và thu hồi quyền `DELETE` trên `watch_history` của Client.

---

## 5. Tập dữ liệu (Datasets)

Dữ liệu thực nghiệm được đóng gói sẵn trong [`database_Phase 3/02_mock_data.sql`](database_Phase%203/02_mock_data.sql) (nạp tự động bằng `setup_database.py` hoặc MySQL Workbench) và lưu bản nguồn tại thư mục [`datasets/`](datasets/README.md):
- **Tổng quy mô:** **86.895 bản ghi** trên 13 bảng (`8.817` nội dung gồm `6.137` Movie + `2.680` TV Series; `3.565` mùa; `7.128` tập; `6.950` tài khoản; `13.694` hồ sơ; `13.697` lịch sử xem; `4.822` mục watchlist; `19.343` liên kết thể loại).
- **Cấu trúc 2 lớp:** Bộ **dữ liệu mẫu cốt lõi** (`10` tựa phim kinh điển, `5` tài khoản phân theo 3 gói cước và `12` lịch sử xem) để kiểm thử tường minh các kịch bản báo cáo, kết hợp bộ **dữ liệu mở rộng chuẩn hóa từ Kaggle** (`netflix_titles.csv` và `netflix_users.csv`) để kiểm chứng hiệu năng truy vấn trên dữ liệu lớn.

Chi tiết ánh xạ và thống kê từng bảng xem tại [datasets/README.md](datasets/README.md).

---

## 6. Hướng dẫn Cài đặt, Triển khai & Vận hành

### Yêu cầu hệ thống
- **MySQL Server:** `8.0` trở lên (cổng mặc định `3306`, hỗ trợ `CHECK` constraints, `UTF8MB4`, `ROLE`).
- **Python:** `3.8` trở lên (nếu chạy Web Demo).
- **Công cụ gợi ý:** MySQL Workbench 8.0 hoặc trình duyệt web (Chrome / Edge / Firefox).

### Cách 1: Cài đặt & Vận hành toàn bộ Hệ thống Web 3-Tier + MySQL (Khuyên dùng)

1. **Cài đặt thư viện Python:**
   ```powershell
   cd web-ui
   pip install -r requirements.txt
   ```
2. **Tạo file cấu hình `.env`:**
   ```powershell
   Copy-Item .env.example .env
   ```
   Mở `web-ui/.env` và chỉnh `DB_USER`, `DB_PASSWORD`, `DB_PORT` khớp với máy chủ MySQL của bạn:
   ```ini
   DB_HOST=localhost
   DB_PORT=3306
   DB_USER=root
   DB_PASSWORD=1234
   DB_NAME=mini_netflix
   PORT=5000
   ```
3. **Khởi tạo CSDL `mini_netflix` tự động (13 bảng, 2 Views, 2 Triggers, 86.895 dòng dữ liệu):**
   ```powershell
   # Tạo mới nếu chưa có và kiểm tra kết nối MySQL:
   python setup_database.py

   # Hoặc xóa sạch và nạp lại toàn bộ từ đầu:
   python setup_database.py --reset
   ```
4. **Khởi chạy Web Server & truy cập hệ thống:**
   ```powershell
   python server.py
   ```
   - Giao diện Người dùng: `http://localhost:5000`
   - Giao diện Quản trị CSDL (DBA Admin Console): `http://localhost:5000/admin`
   - Kiểm tra trạng thái API & DB: `GET http://localhost:5000/api/health`

#### Tài khoản Demo khi vận hành Web UI

| Vai trò | Email đăng nhập | Mật khẩu | Mục đích kiểm thử |
| :--- | :--- | :--- | :--- |
| **User (Gói Basic)** | `an.nguyen@gmail.com` | `123456` | Tối đa **1 hồ sơ** — thử bấm *Thêm hồ sơ* để kích hoạt Trigger `BR-01`. |
| **User (Gói Standard)** | `binh.tran@gmail.com` | `123456` | Tối đa **3 hồ sơ**, có hồ sơ trẻ em `Bé Bi (is_kids = 1)` để test Trigger `BR-09`. |
| **User (Gói Premium)** | `cuong.le@gmail.com` | `123456` | Tối đa **5 hồ sơ**, chất lượng `4K`. |
| **User (Bị khóa)** | `dung.pham@gmail.com` | `123456` | Trạng thái `SUSPENDED` — bị chặn tại cổng đăng nhập. |
| **Quản trị viên (DBA)** | `admin@mininetflix.com` | `admin123` | Tự động chuyển sang **DBA Admin Console** (`/admin`). |

### Cách 2: Chạy trực tiếp các kịch bản SQL trên MySQL Workbench 8.0

Mở lần lượt các file trong thư mục [`database_Phase 3/`](database_Phase%203/) và thực thi theo đúng thứ tự:
1. `01_schema.sql` — Tạo database `mini_netflix`, 13 bảng, chỉ mục B-Tree, 2 Triggers và 2 Views.
2. `02_mock_data.sql` — Nạp 86.895 bản ghi mẫu.
3. `03_queries.sql` — Chạy kiểm thử 10 truy vấn nghiệp vụ nâng cao.
4. `04_performance_test.sql` — Chạy đối chiếu `EXPLAIN` / `EXPLAIN ANALYZE` kiểm chứng 5 chỉ mục & 3 Edge Cases.
5. `05_rbac_security.sql` — Khởi tạo 3 Roles và áp dụng `GRANT` / `REVOKE`.
6. `06_negative_test_cases.sql` — Chạy **từng câu lệnh riêng lẻ** (`TC-01` đến `TC-05`) để quan sát mã lỗi MySQL (`1644`, `1062`, `1451`, `3819`) chặn dữ liệu sai.
7. `07_extended_test_cases.sql` — Bộ kịch bản mở rộng (Positive cận biên, Extended `CHECK`/`UNIQUE`, `ON DELETE CASCADE`, kiểm toán EER, kiểm thử RBAC).

### Cách 3: Chạy kiểm thử tự động & Benchmark hiệu năng bằng Python
```powershell
# Chạy toàn bộ 56 ca kiểm thử Schema, Triggers, Cascade, RBAC, Queries & Flask API:
python "database_Phase 3/verify_database.py"

# Chạy bộ Benchmark đo p50/p95/p99, QPS, EXPLAIN ANALYZE & Handler_read_* thuần tầng MySQL:
python "database_Phase 3/benchmark_performance.py"
```

---

## 7. Tài liệu & Báo cáo Chi tiết

- **Báo cáo chi tiết đồ án (PDF):** [BÁO CÁO DỰ ÁN CƠ SỞ DỮ LIỆU - HỆ THỐNG PHIM TRỰC TUYẾN (MINI-NETFLIX) - NHÓM G12.pdf](report/B%C3%81O%20C%C3%81O%20D%E1%BB%B0%20%C3%81N%20C%C6%A0%20S%E1%BB%9E%20D%E1%BB%AE%20LI%E1%BB%86U-%20H%E1%BB%86%20TH%E1%BB%90NG%20PHIM%20TR%E1%BB%B0C%20TUY%E1%BA%BEN%20%28MINI-NETFLIX%29%20-%20NH%C3%93M%20G12.pdf)
- **Đặc tả REST API:** [API_CONTRACT.md](API_CONTRACT.md)
- **Hướng dẫn chi tiết Web UI & AI Playbook:** [web-ui/README.md](web-ui/README.md)
- **Mô tả Tập dữ liệu:** [datasets/README.md](datasets/README.md)
- **Kết quả Kiểm chứng Tự động (56/56 PASS):** [database_Phase 3/TEST_RESULTS.md](database_Phase%203/TEST_RESULTS.md)
- **Báo cáo Benchmark Hiệu năng MySQL:** [database_Phase 3/PERFORMANCE_REPORT.md](database_Phase%203/PERFORMANCE_REPORT.md)
