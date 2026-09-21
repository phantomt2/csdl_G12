 PHASE 2: LOGICAL DESIGN (Phần của Vĩ)

 1. BẢNG: WATCHLIST

Relational Schema Mapping
| Column Name | Data Type | Constraint | Description |
| :--- | :--- | :--- | :--- |
| Watchlist_ID | INT | Primary Key | Mã định danh bản ghi |
| Profile_ID | INT | Foreign Key | Mã hồ sơ người dùng |
| Content_ID | INT | Foreign Key | Mã nội dung |
| Added_Date | DATETIME | NOT NULL | Thời gian thêm vào danh sách |

Foreign Key definitions
- Profile_ID references to USER_PROFILE(Profile_ID)
- Content_ID references to CONTENT(Content_ID)

Normalization proofs (3NF/BCNF)
- 1NF: Bảng không chứa thuộc tính đa trị, mọi giá trị đều nguyên tử.
- 2NF: Khóa chính là khóa đơn (Watchlist_ID), các thuộc tính còn lại phụ thuộc hoàn toàn vào khóa chính.
- 3NF & BCNF: Không có phụ thuộc bắc cầu giữa các thuộc tính không khóa. Bảng đạt chuẩn BCNF.

---

 2. BẢNG: WATCH_HISTORY

Relational Schema Mapping
| Column Name | Data Type | Constraint | Description |
| :--- | :--- | :--- | :--- |
| History_ID | INT | Primary Key | Mã định danh lịch sử xem |
| Profile_ID | INT | Foreign Key | Mã hồ sơ người dùng |
| Content_ID | INT | Foreign Key | Mã nội dung đang xem |
| Progress_Minute | INT | DEFAULT 0 | Thời lượng đã xem (phút) |
| Last_Watched | DATETIME | NOT NULL | Thời gian xem gần nhất |

Foreign Key definitions
- Profile_ID references to USER_PROFILE(Profile_ID)
- Content_ID references to CONTENT(Content_ID)

Normalization proofs (3NF/BCNF)
- 1NF: Bảng không chứa thuộc tính đa trị, mọi giá trị đều nguyên tử.
- 2NF: Khóa chính là khóa đơn (History_ID), các thuộc tính còn lại phụ thuộc hoàn toàn vào khóa chính.
- 3NF & BCNF: Không có phụ thuộc bắc cầu giữa các thuộc tính không khóa. Bảng đạt chuẩn BCNF.

---

 3. BẢNG: AUDIO_SUBTITLE_TRACK

Relational Schema Mapping
| Column Name | Data Type | Constraint | Description |
| :--- | :--- | :--- | :--- |
| Track_ID | INT | Primary Key | Mã định danh track |
| Content_ID | INT | Foreign Key | Mã nội dung |
| Track_Type | VARCHAR(50) | NOT NULL | Loại track (Audio / Subtitle) |
| Language_Code | VARCHAR(10) | NOT NULL | Mã ngôn ngữ (VD: vi-VN) |
| File_URL | VARCHAR(255) | NOT NULL | Đường dẫn lưu trữ file |

Foreign Key definitions
- Content_ID references to CONTENT(Content_ID)

Normalization proofs (3NF/BCNF)
- 1NF: Bảng không chứa thuộc tính đa trị, mọi giá trị đều nguyên tử.
- 2NF: Khóa chính là khóa đơn (Track_ID), các thuộc tính còn lại phụ thuộc hoàn toàn vào khóa chính.
- 3NF & BCNF: Không có phụ thuộc bắc cầu giữa các thuộc tính không khóa. Bảng đạt chuẩn BCNF.