<!-- ===================================================================== -->
<!-- 🤖 AI AGENT / LLM ENTRYPOINT DIRECTIVE (ĐỌC DÒNG NÀY ĐẦU TIÊN!)       -->
<!-- Nếu bạn là AI Agent đang đọc file README.md này lần đầu tiên:         -->
<!-- ĐÂY LÀ DÒNG CHỈ ĐƯỜNG DÀNH RIÊNG CHO AI! Hãy di chuyển con trỏ đọc    -->
<!-- và NHẢY THẲNG XUỐNG nhãn neo: #ai-agent-setup-section ở Phần II!      -->
<!-- ===================================================================== -->

> 🤖 **[CHỈ DẪN ĐẦU TIÊN DÀNH CHO AI AGENT / LLM]:**  
> **ĐÂY LÀ ĐIỂM NHẢY DÀNH CHO AI!** Khi bạn (AI) lần đầu tiên đọc vào file `README.md` này, hãy **dịch chuyển con trỏ nhảy thẳng xuống [👉 PHẦN II: HƯỚNG DẪN SETUP DÀNH CHO AI AGENT (`#ai-agent-setup-section`)](#ai-agent-setup-section)** ở bên dưới để thực thi quy trình cài đặt tự động. Phần I ngay sau đây được viết dành cho con người đọc trước.

---

# 🎬 MINI-NETFLIX WEB APPLICATION & DATABASE SYSTEM (NHÓM G12)

**Học phần:** Cơ sở dữ liệu (Database Systems)  
**Đề tài:** Hệ thống Quản lý & Khai thác Cơ sở dữ liệu Phim Trực tuyến (*On-Demand Streaming Platform — Mini-Netflix*)  
**Kiến trúc:** 3-Tier Architecture (`Client Browser UI` $\leftrightarrow$ `Python Flask REST API` $\leftrightarrow$ `MySQL Relational Database`)

> [!IMPORTANT]
> **Triết lý cốt lõi của hệ thống Mini-Netflix:**  
> Đây là ứng dụng minh họa **Cơ sở dữ liệu Quan hệ chuẩn hóa 3NF/BCNF** (13 Bảng, Phân cấp thực thể EER `CONTENT` $\rightarrow$ `MOVIE` / `TV_SERIES` $\rightarrow$ `SEASON` $\rightarrow$ `TV_EPISODE`, 2 Views, 2 Triggers `BR-01` & `BR-09`). Hệ thống tập trung 100% vào **Đọc (`SELECT`) và Ghi (`INSERT / UPDATE / DELETE`) dữ liệu hai chiều trực tiếp với MySQL** (thông qua Bộ Ghi Nhận Nhật Ký Xem `WATCH_HISTORY` và Bộ Lọc Phân Tích Đa Chiều Admin), **không sử dụng trình phát video giả lập**.

---

## 📑 MỤC LỤC ĐIỀU HƯỚNG
1. **[PHẦN I: Hướng dẫn Cài đặt & Sử dụng dành cho Người dùng (Human Setup Guide)](#human-setup-guide)**
   - [1.1. Cấu trúc thư mục đóng gói](#11-cau-truc-thu-muc)
   - [1.2. Yêu cầu hệ thống](#12-yeu-cau-he-thong)
   - [1.3. Các bước cài đặt từ A–Z (4 Bước)](#13-cac-buoc-cai-dat)
   - [1.4. Tài khoản Demo & Hướng dẫn trải nghiệm tính năng](#14-tai-khoan-demo)
2. **[🤖 PHẦN II: Hướng dẫn Setup Tự động dành cho AI Agent (AI Agent Playbook)](#ai-agent-setup-section)**

---

<a id="human-setup-guide"></a>
## 👨‍💻 PHẦN I: HƯỚNG DẪN CÀI ĐẶT & SỬ DỤNG DÀNH CHO NGƯỜI DÙNG (HUMAN SETUP GUIDE)

### 1.1. Cấu trúc thư mục đóng gói (`web-ui/`) {#11-cau-truc-thu-muc}

```text
web-ui/
├── server.py                  # Máy chủ Backend Flask REST API & Động cơ Truy vấn Động (Port 5000)
├── setup_database.py          # Script tự động kiểm tra kết nối & khởi tạo CSDL MySQL (13 bảng, 2 views, 2 triggers)
├── index.html                 # Giao diện Người dùng (Auth Gate, Profile Gate, Multi-Genre Filter, Watch Logger)
├── admin.html                 # Giao diện DBA Admin Console (Revenue View, Dynamic Query Builder 1..300, DML, Triggers)
├── requirements.txt           # Danh sách thư viện Python cần cài đặt
├── .env                       # File cấu hình kết nối MySQL hiện hành
├── .env.example               # File mẫu cấu hình kết nối MySQL
├── templates/                 # Thư mục template HTML chuẩn của Flask
│   ├── index.html
│   └── admin.html
├── static/                    # Thư mục phục vụ file tĩnh
│   ├── index.html
│   └── admin.html
└── database/                  # Bộ kịch bản SQL gốc (Phase 3)
    ├── 01_schema.sql          # Định nghĩa DDL: 13 Bảng, Khóa ngoại CASCADE, 2 Triggers, 2 Views
    ├── 02_mock_data.sql       # Dữ liệu mẫu phong phú cho toàn bộ 13 bảng
    ├── 03_queries.sql         # 10 câu truy vấn phân tích phức tạp chuẩn Phase 3
    ├── 04_performance_test.sql# Kịch bản kiểm thử hiệu năng Index
    ├── 05_rbac_security.sql   # Phân quyền người dùng CSDL (RBAC)
    └── 06_negative_test_cases.sql # Kịch bản kiểm thử vi phạm ràng buộc & Triggers
```

---

### 1.2. Yêu cầu hệ thống (Prerequisites) {#12-yeu-cau-he-thong}
* **Python:** Phiên bản `3.8` trở lên.
* **MySQL Server:** Phiên bản `8.0` trở lên (đang chạy ở cổng mặc định `3306`).
* **Trình duyệt web:** Chrome, Edge, Firefox hoặc Safari.

---

### 1.3. Các bước cài đặt từ A–Z (Chỉ 4 bước) {#13-cac-buoc-cai-dat}

#### Bước 1: Cài đặt thư viện Python
Mở Terminal (PowerShell hoặc Command Prompt) tại thư mục `web-ui` và chạy:
```powershell
pip install -r requirements.txt
```

#### Bước 2: Cấu hình thông tin MySQL trong file `.env`
Mở file `.env` (nếu chưa có thì copy từ `.env.example` thành `.env`) và chỉnh lại `DB_USER`, `DB_PASSWORD` đúng với MySQL trên máy của bạn:
```ini
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=123
DB_NAME=mini_netflix
PORT=5000
```

#### Bước 3: Khởi tạo & Kiểm tra Cơ sở dữ liệu MySQL
Chạy script tự động `setup_database.py` để kiểm tra kết nối MySQL và tự động tạo CSDL `mini_netflix` (nếu máy bạn chưa nạp CSDL hoặc muốn nạp lại toàn bộ từ đầu):
```powershell
# Kiểm tra kết nối (tự động tạo CSDL nếu chưa tồn tại):
python setup_database.py

# Hoặc nếu muốn XÓA và NẠP LẠI MỚI toàn bộ 13 bảng + dữ liệu mẫu từ đầu:
python setup_database.py --reset
```

#### Bước 4: Khởi chạy Web Server
```powershell
python server.py
```
Sau khi màn hình hiện thông báo máy chủ hoạt động, mở trình duyệt tại:
* **Trang Người dùng (Mini-Netflix User UI):** `http://localhost:5000`
* **Trang Quản trị CSDL (DBA Admin Console):** `http://localhost:5000/admin`

---

### 1.4. Tài khoản Demo & Hướng dẫn Trải nghiệm Tính năng {#14-tai-khoan-demo}

| Vai trò | Email đăng nhập | Mật khẩu | Đặc điểm kiểm thử CSDL |
| :--- | :--- | :--- | :--- |
| **User (Gói Basic)** | `an.nguyen@gmail.com` | `123456` | Độ phân giải HD, giới hạn tối đa **1 hồ sơ** (bấm ô vuông `"Thêm hồ sơ"` sẽ kích hoạt ngay **Trigger BR-01**). |
| **User (Gói Standard)** | `binh.tran@gmail.com` | `123456` | Độ phân giải Full HD, tối đa **3 hồ sơ**, có sẵn hồ sơ trẻ em **`Bé Bi` (`is_kids = 1`)** để test **Trigger BR-09**. |
| **User (Gói Premium)** | `cuong.le@gmail.com` | `123456` | Độ phân giải 4K UHD, tối đa **5 hồ sơ**. |
| **User (Bị khóa)** | `dung.pham@gmail.com` | `123456` | Trạng thái `SUSPENDED` — bị chặn đăng nhập ngay tại Cổng xác thực (`BR-05`). |
| **Quản trị viên (DBA)** | `admin@mininetflix.com` *(hoặc `admin@netflix.com`)* | `admin123` | Tự động chuyển hướng sang **DBA Admin Console (`/admin`)**. |

#### Điểm nhấn tính năng trên Giao diện Người dùng (`/`):
1. **Cổng Chọn Hồ sơ (`#profileGate` - "Ai đang xem?"):** Hỗ trợ Thêm (`POST`), Sửa (`PUT`), Xóa (`DELETE`) hồ sơ. Ô vuông `"Thêm hồ sơ"` luôn hiển thị để kiểm định trực tiếp Trigger `trg_check_profile_limit_before_insert` (`BR-01`).
2. **Tìm kiếm & Bộ lọc Đa Thể loại (`#searchFilterModal`):** Cho phép chọn kết hợp **nhiều thể loại (`Genre`) cùng lúc**, lọc theo ngôn ngữ gốc, loại hình (`MOVIE` / `TV_SERIES`), chất lượng phát và độ tuổi.
3. **Bộ Ghi Nhận Nhật Ký Xem (`#watchLoggerModal` - Bảng `WATCH_HISTORY`):**
   * Giới hạn thời gian xem không vượt quá thời lượng thực của Phim lẻ hoặc Tập phim.
   * Khi chọn `is_completed = TRUE` cho Phim lẻ, tự động ghi đè thời gian lên `100%` thời lượng.
   * Với Phim bộ (`TV_SERIES`), lưu thời gian riêng cho từng tập (`episode_id`), hỗ trợ ghi đồng bộ nhiều tập trong một lần lưu, và **bắt buộc hoàn tất 100% tất cả các mùa & tập** mới cho phép đánh dấu `is_completed = TRUE` cho cả bộ Series.

#### Điểm nhấn tính năng trên Giao diện Quản trị (`/admin`):
1. **Tab 1 — Báo cáo Doanh thu (`vw_subscription_revenue_summary`):** Tổng hợp thuê bao và doanh thu theo thời gian thực.
2. **Tab 2 — Bộ Lọc Phân Tích Đa Chiều & Trình Tạo Truy Vấn Động (`Dynamic Query Builder`):**
   * Kết hợp tự do 4 phân hệ dữ liệu gốc với 10 bộ lọc điều kiện (`WHERE`), gom nhóm thống kê (`GROUP BY`), tùy chỉnh tự do **Số bản ghi tối đa (`LIMIT` từ `1` đến tối đa `300`)**, xuất CSV, chạy 10 mẫu truy vấn chuẩn Phase 3 hoặc gõ lệnh `SELECT` trực tiếp trong khung **Safe Read-Only SQL Sandbox**.
3. **Tab 3, 4, 5:** Quản trị tài khoản & đổi gói cước trực tiếp, thêm mới dữ liệu phân cấp EER (`CONTENT`, `SEASON`, `TV_EPISODE`, `GENRE`, `LANGUAGE`), xóa lan truyền (`ON DELETE CASCADE`), và Bàn kiểm thử trực tiếp 2 Triggers `BR-01` & `BR-09`.

---
---

<a id="ai-agent-setup-section"></a>
## 🤖 PHẦN II: HƯỚNG DẪN SETUP TỰ ĐỘNG DÀNH CHO AI AGENT (AI AGENT EXECUTION PLAYBOOK)

> **[AI AGENT TARGET ANCHOR REACHED (`#ai-agent-setup-section`)]:**  
> Chào AI Agent! Bạn đã nhảy thẳng tới phần hướng dẫn thực thi tự động dành riêng cho AI. Hãy tuân thủ chính xác các bước dưới đây để cài đặt, khởi tạo CSDL MySQL, chạy máy chủ Flask và xác minh hệ thống **Mini-Netflix** mà không cần hỏi lại người dùng trừ khi phát sinh lỗi xác thực MySQL.

### Bước 1: Xác định Thư mục Làm việc & Cài đặt Dependencies
Đảm bảo thư mục làm việc hiện tại là thư mục chứa `server.py` và `setup_database.py` (tức `web-ui/`). Chạy lệnh cài đặt thư viện:
```powershell
pip install -r requirements.txt
```

### Bước 2: Kiểm tra & Khởi tạo file `.env`
1. Kiểm tra xem file `.env` có tồn tại trong cùng thư mục với `server.py` hay không.
2. Nếu chưa tồn tại, sao chép `.env.example` sang `.env`:
   ```powershell
   if (!(Test-Path .env)) { Copy-Item .env.example .env }
   ```
3. Các biến môi trường chuẩn trong `.env`:
   - `DB_HOST=localhost`
   - `DB_PORT=3306`
   - `DB_USER=root`
   - `DB_PASSWORD=123` *(Nếu kết nối thất bại với lỗi Access Denied 1045, hãy kiểm tra mật khẩu MySQL trên máy chủ hoặc hỏi người dùng mật khẩu `root` của MySQL).*
   - `DB_NAME=mini_netflix`
   - `PORT=5000`

### Bước 3: Thực thi Script Khởi tạo & Kiểm định CSDL (`setup_database.py`)
Chạy lệnh sau để tự động tạo database `mini_netflix` (nếu chưa có), nạp `database/01_schema.sql` + `database/02_mock_data.sql`, và đảm bảo chỉ mục `uq_watch_history_profile_content_ep (profile_id, content_id, episode_id)` đã được kích hoạt:
```powershell
python setup_database.py
```
* **Kỳ vọng đầu ra:**
  - `[OK] Kết nối tới MySQL Server thành công!`
  - `Số lượng Bảng (Base Tables) : 13 / 13 bảng`
  - `Số lượng Khung nhìn (Views) : 2 / 2 views`
  - `Số lượng Triggers           : 2 / 2 triggers`
* *(Lưu ý cho AI: Nếu cần reset sạch toàn bộ dữ liệu mẫu về trạng thái ban đầu, chạy `python setup_database.py --reset`).*

### Bước 4: Khởi chạy Máy chủ Flask (`server.py`) ở Chế độ Background / Daemon
1. Kiểm tra xem cổng `5000` đã có tiến trình nào chiếm dụng chưa. Nếu có tiến trình cũ, dừng tiến trình đó hoặc kiểm tra healthcheck.
2. Khởi chạy `python server.py` ở chế độ chạy nền (daemon/background process) để không làm treo phiên làm việc của AI:
   ```powershell
   python server.py
   ```
3. Kiểm tra trạng thái hoạt động qua REST API Healthcheck:
   ```powershell
   Invoke-RestMethod -Uri "http://localhost:5000/api/health" -Method Get
   ```
   * **Kỳ vọng JSON trả về:** `{"connected": true, "database": "mini_netflix", "status": "healthy"}`.

### Bước 5: Bản đồ Kiến trúc & Quy tắc Bất biến dành cho AI khi Bảo trì / Nâng cấp
Nếu người dùng yêu cầu bạn (AI) chỉnh sửa hoặc kiểm tra thêm tính năng trên dự án này, hãy ghi nhớ **5 quy tắc bất biến** sau:
1. **Không có trình phát video giả lập (`No Fake Video Player`):** Mọi thao tác "Xem phim / Ghi nhận xem" trên `index.html` đều mở `#watchLoggerModal` để ghi dữ liệu thực tế vào bảng `watch_history` qua `POST /api/watch-history`.
2. **Ràng buộc Thời lượng & Hoàn tất (`is_completed`):**
   - Thời gian dừng xem (`stopped_position_seconds`) không bao giờ được vượt quá `duration_minutes * 60` của `movie` hoặc `tv_episode`.
   - Đối với `MOVIE`: Khi chọn `is_completed = TRUE`, thời gian tự động ghi đè lên 100% thời lượng phim.
   - Đối với `TV_SERIES`: Mỗi tập phim (`episode_id`) lưu tiến trình riêng theo khóa duy nhất `(profile_id, content_id, episode_id)`. Chỉ khi **tất cả các tập của tất cả các mùa** trong Series đều đạt 100% thời lượng thì `is_completed` của Series mới được phép mang giá trị `TRUE`.
3. **2 MySQL Triggers Bắt buộc Hoạt động Thực tế (`SQLSTATE '45000'`):**
   - `trg_check_profile_limit_before_insert` (`BR-01`): Chặn tạo thêm `profile` khi vượt `max_profiles_allowed` của gói cước (`Basic: 1`, `Standard: 3`, `Premium: 5`).
   - `trg_check_kids_rating_before_watch` (`BR-09`): Chặn hồ sơ trẻ em (`is_kids = 1`, ví dụ `profile_id = 3`) ghi nhận xem nội dung nhãn `R` hoặc `NC-17`.
4. **Bộ Lọc Phân Tích Đa Chiều Admin (`POST /api/admin/query-builder`):**
   - Cho phép kết hợp 4 phân hệ (`content`, `watch_behavior`, `subscription`, `raw_table`), lọc đa điều kiện, gom nhóm `GROUP BY`, và điều chỉnh `LIMIT` tự do trong khoảng `1 <= limit <= 300`.
5. **Đồng bộ hóa File HTML:**
   - Khi sửa `index.html` hoặc `admin.html` tại thư mục gốc `web-ui/`, luôn copy đồng bộ sang `web-ui/templates/` và `web-ui/static/` (vì Flask ưu tiên đọc từ `templates/` khi render).
