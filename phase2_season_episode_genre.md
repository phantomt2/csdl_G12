# BÁO CÁO GIAI ĐOẠN 2: THIẾT KẾ LUẬN LÝ & CHUẨN HÓA CƠ SỞ DỮ LIỆU
**Đối tượng phân tích:** `SEASON`, `TV_EPISODE`, `GENRE`, `CONTENT_GENRE`  
**Tiêu chuẩn áp dụng:**  
- Thiết kế luận lý: ISO/IEC 19505 (Relational Mapping)  
- Từ điển dữ liệu: ISO/IEC 11179 Metadata Standards  
- Chuẩn hóa hình thức: 1NF $\rightarrow$ 3NF / BCNF (Codd & Boyce-Codd Normal Form)  
- Quy tắc mã hóa: Google SQL Style Guide / SQLStyle.guide  

---

## BẢNG KIỂM TRA ĐÁNH GIÁ TIÊU CHÍ (VERIFICATION CHECKLIST)

| Hạng mục yêu cầu (Phase 2 Deliverables) | Trạng thái | Diễn giải minh chứng kỹ thuật |
| :--- | :---: | :--- |
| **1. Ánh xạ lược đồ quan hệ (Relational Mapping)** | **ĐẠT** | Biểu diễn chuẩn hình thức $R(\underline{PK}, FK, ...)$, xử lý chính xác thực thể yếu lồng nhau và quan hệ $M:N$. |
| **2. Toàn vẹn tham chiếu (Referential Integrity)** | **ĐẠT** | Định nghĩa chi tiết khóa ngoại (FK), bảng tham chiếu và hành vi `ON DELETE CASCADE` / `RESTRICT`. |
| **3. Bám sát BR & FR của Phase 1** | **ĐẠT** | Tuân thủ BR-04 (Episode phụ thuộc Season), BR-08 (Season thuộc Series) và bảng liên kết Content-Genre (Table 1). |
| **4. Chứng minh chuẩn hóa (1NF $\rightarrow$ 3NF/BCNF)** | **ĐẠT** | Liệt kê đầy đủ tập Phụ thuộc hàm ($F$), tìm Khóa ứng viên ($CK$), chứng minh không vi phạm 1NF, 2NF, 3NF và đạt BCNF. |
| **5. Từ điển dữ liệu (ISO/IEC 11179)** | **ĐẠT** | Đủ 6 cột chuẩn: `Attribute Name`, `Data Type`, `Key Type`, `Nullable?`, `Default Value`, `Business Rules / Constraints`. |

---

## PHẦN I: ÁNH XẠ LƯỢC ĐỒ QUAN HỆ & RÀNG BUỘC TOÀN VẸN (RELATIONAL SCHEMA MAPPING)

### 1. Ký hiệu hình thức Lược đồ quan hệ

* **Quan hệ `SEASON`** (Ánh xạ từ Thực thể yếu phụ thuộc tồn tại vào `TV_SERIES`):
  $$\text{SEASON}(\underline{\text{season\_id}}, \text{content\_id}, \text{season\_number}, \text{season\_name}, \text{release\_date})$$
  * Khóa chính (PK): `season_id`
  * Khóa ngoại (FK): `content_id` $\rightarrow \text{TV\_SERIES}(\text{content\_id})$
  * Khóa tự nhiên phụ (Alternate Key): `(content_id, season_number)`

* **Quan hệ `TV_EPISODE`** (Ánh xạ từ Thực thể yếu phụ thuộc vào `SEASON` qua Identifying Relationship):
  $$\text{TV\_EPISODE}(\underline{\text{episode\_id}}, \text{season\_id}, \text{episode\_number}, \text{episode\_title}, \text{duration\_minutes}, \text{video\_file\_size\_gb})$$
  * Khóa chính (PK): `episode_id`
  * Khóa ngoại (FK): `season_id` $\rightarrow \text{SEASON}(\text{season\_id})$
  * Khóa tự nhiên phụ (Alternate Key): `(season_id, episode_number)`

* **Quan hệ `GENRE`** (Ánh xạ từ Thực thể mạnh / Bảng danh mục phân loại Lookup Entity):
  $$\text{GENRE}(\underline{\text{genre\_id}}, \text{genre\_name})$$
  * Khóa chính (PK): `genre_id`
  * Khóa duy nhất (Unique Key): `genre_name`

* **Quan hệ `CONTENT_GENRE`** (Ánh xạ từ Mối quan hệ Nhiều - Nhiều $M:N$ và giải quyết thuộc tính đa trị `Genre` của `CONTENT`):
  $$\text{CONTENT\_GENRE}(\underline{\text{content\_id}}, \underline{\text{genre\_id}})$$
  * Khóa chính tổng hợp (Composite PK): `(content_id, genre_id)`
  * Khóa ngoại 1 (FK1): `content_id` $\rightarrow \text{CONTENT}(\text{content\_id})$
  * Khóa ngoại 2 (FK2): `genre_id` $\rightarrow \text{GENRE}(\text{genre\_id})$

---

### 2. Định nghĩa Khóa ngoại và Toàn vẹn tham chiếu (Referential Integrity Definition)

| Bảng nguồn | Cột khóa ngoại (FK) | Bảng đích tham chiếu | Cột khóa chính (PK) | ON DELETE | ON UPDATE | Ý nghĩa nghiệp vụ / Ràng buộc |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`SEASON`** | `content_id` | `TV_SERIES` | `content_id` | **CASCADE** | **CASCADE** | Một mùa phim bắt buộc phải thuộc về một TV Series (BR-08). Khi xóa bộ phim, toàn bộ các mùa phát sóng của phim đó tự động bị xóa. |
| **`TV_EPISODE`** | `season_id` | `SEASON` | `season_id` | **CASCADE** | **CASCADE** | Tập phim là thực thể yếu, không thể tồn tại nếu không có mùa xác định (BR-04). Khi xóa một mùa, các tập phim con tự động bị xóa. |
| **`CONTENT_GENRE`**| `content_id` | `CONTENT` | `content_id` | **CASCADE** | **CASCADE** | Khi một nội dung bị gỡ khỏi hệ thống, các bản ghi gán thể loại của tác phẩm đó tự động được giải phóng. |
| **`CONTENT_GENRE`**| `genre_id` | `GENRE` | `genre_id` | **RESTRICT** | **CASCADE** | Chặn hành vi xóa một thể loại (ví dụ: "Hành động") nếu đang có phim gán thể loại này trong CSDL. |

---

## PHẦN II: CHỨNG MINH CHUẨN HÓA HÌNH THỨC (FORMAL NORMALIZATION PROOFS)

---

### 1. Chuẩn hóa quan hệ `GENRE`

* **Tập thuộc tính:** $R = \{\text{genre\_id}, \text{genre\_name}\}$
* **Tập Phụ thuộc hàm ($F$):**
  $$f_1: \text{genre\_id} \rightarrow \text{genre\_name}$$
  $$f_2: \text{genre\_name} \rightarrow \text{genre\_id}$$
* **Tập Khóa ứng viên (Candidate Keys):**
  $$(\text{genre\_id})^+ = \{\text{genre\_id}, \text{genre\_name}\} = R \Rightarrow CK_1 = \{\text{genre\_id}\}$$
  $$(\text{genre\_name})^+ = \{\text{genre\_name}, \text{genre\_id}\} = R \Rightarrow CK_2 = \{\text{genre\_name}\}$$
* **Khóa chính được chọn:** $PK = \text{genre\_id}$
* **Tiến trình chứng minh các dạng chuẩn:**
  1. **Dạng chuẩn 1 (1NF):** Thuộc tính `genre_id` (số nguyên) và `genre_name` (chuỗi ký tự) đều mang giá trị đơn nguyên tố (Atomic values), không chứa thuộc tính phức hợp hay tập giá trị lặp $\Rightarrow$ **Đạt 1NF**.
  2. **Dạng chuẩn 2 (2NF):** Khóa chính chỉ gồm 1 thuộc tính đơn (`genre_id`). Mọi thuộc tính không khóa đều phụ thuộc hàm đầy đủ vào khóa chính, không tồn tại phụ thuộc từng phần $\Rightarrow$ **Đạt 2NF**.
  3. **Dạng chuẩn 3 (3NF):** Không có thuộc tính không khóa nào xác định thuộc tính không khóa khác (không tồn tại phụ thuộc bắc cầu qua thuộc tính không khóa) $\Rightarrow$ **Đạt 3NF**.
  4. **Dạng chuẩn Boyce-Codd (BCNF):** Với mọi phụ thuộc hàm không tầm thường $X \rightarrow Y \in F$, vế trái $X$ đều là Siêu khóa (Superkey: cả `genre_id` và `genre_name` đều là khóa ứng viên) $\Rightarrow$ **Đạt BCNF**.

---

### 2. Chuẩn hóa quan hệ `CONTENT_GENRE`

* **Tập thuộc tính:** $R = \{\text{content\_id}, \text{genre\_id}\}$
* **Tập Phụ thuộc hàm ($F$):**
  $$F = \emptyset \quad (\text{chỉ tồn tại phụ thuộc hàm tầm thường: } \{\text{content\_id}, \text{genre\_id}\} \rightarrow \{\text{content\_id}, \text{genre\_id}\})$$
* **Khóa chính (PK):** $PK = \{\text{content\_id}, \text{genre\_id}\}$
* **Tiến trình chứng minh các dạng chuẩn:**
  1. **1NF:** Mỗi ô dữ liệu lưu trữ duy nhất một cặp mã định danh số nguyên nguyên tố $\Rightarrow$ **Đạt 1NF**.
  2. **2NF:** Toàn bộ các thuộc tính trong quan hệ đều tham gia vào khóa chính ($R = PK$). Không tồn tại thuộc tính không khóa $\Rightarrow$ Không thể vi phạm phụ thuộc từng phần $\Rightarrow$ **Đạt 2NF**.
  3. **3NF & BCNF:** Do không có thuộc tính không khóa và không có phụ thuộc hàm không tầm thường vi phạm điều kiện siêu khóa $\Rightarrow$ **Mặc nhiên đạt chuẩn 3NF và BCNF**.

---

### 3. Chuẩn hóa quan hệ `SEASON`

* **Tập thuộc tính:** $R = \{\text{season\_id}, \text{content\_id}, \text{season\_number}, \text{season\_name}, \text{release\_date}\}$
* **Tập Phụ thuộc hàm ($F$):**
  $$f_1: \text{season\_id} \rightarrow \{\text{content\_id}, \text{season\_number}, \text{season\_name}, \text{release\_date}\}$$
  $$f_2: \{\text{content\_id}, \text{season\_number}\} \rightarrow \{\text{season\_id}, \text{season\_name}, \text{release\_date}\}$$
* **Tập Khóa ứng viên (Candidate Keys):**
  $$CK_1 = \{\text{season\_id}\} \quad (\text{Khóa thay thế - Surrogate Key})$$
  $$CK_2 = \{\text{content\_id}, \text{season\_number}\} \quad (\text{Khóa tự nhiên - Natural Key})$$
* **Khóa chính được chọn:** $PK = \text{season\_id}$
* **Thuộc tính khóa:** $\{\text{season\_id}, \text{content\_id}, \text{season\_number}\}$  
* **Thuộc tính không khóa:** $\{\text{season\_name}, \text{release\_date}\}$
* **Tiến trình chứng minh các dạng chuẩn:**
  1. **1NF:** Mọi thuộc tính số mùa, tên mùa, ngày phát hành đều có miền giá trị nguyên tố $\Rightarrow$ **Đạt 1NF**.
  2. **2NF:** Khóa chính được chọn $\text{season\_id}$ là khóa đơn. Không có thuộc tính không khóa nào phụ thuộc vào một tập con thực sự của $\text{season\_id}$. Xét với $CK_2 = \{\text{content\_id}, \text{season\_number}\}$, cả `season_name` và `release_date` đều phụ thuộc vào toàn bộ cặp (phải biết cả phim và mùa mới biết ngày ra mắt), không phụ thuộc riêng vào `content_id` hay `season_number` $\Rightarrow$ **Đạt 2NF**.
  3. **3NF:** Thuộc tính `release_date` và `season_name` phụ thuộc trực tiếp vào khóa chính, không có sự phụ thuộc bắc cầu lẫn nhau (ví dụ: `season_name` không suy ra `release_date`) $\Rightarrow$ **Đạt 3NF**.
  4. **BCNF:** Trong cả hai phụ thuộc hàm $f_1$ và $f_2$, vế xác định ($\text{season\_id}$ và $\{\text{content\_id}, \text{season\_number}\}$) đều là Siêu khóa $\Rightarrow$ **Đạt BCNF**.

---

### 4. Chuẩn hóa quan hệ `TV_EPISODE`

* **Tập thuộc tính:** $R = \{\text{episode\_id}, \text{season\_id}, \text{episode\_number}, \text{episode\_title}, \text{duration\_minutes}, \text{video\_file\_size\_gb}\}$
* **Tập Phụ thuộc hàm ($F$):**
  $$f_1: \text{episode\_id} \rightarrow \{\text{season\_id}, \text{episode\_number}, \text{episode\_title}, \text{duration\_minutes}, \text{video\_file\_size\_gb}\}$$
  $$f_2: \{\text{season\_id}, \text{episode\_number}\} \rightarrow \{\text{episode\_id}, \text{episode\_title}, \text{duration\_minutes}, \text{video\_file\_size\_gb}\}$$
* **Tập Khóa ứng viên (Candidate Keys):**
  $$CK_1 = \{\text{episode\_id}\}$$
  $$CK_2 = \{\text{season\_id}, \text{episode\_number}\}$$
* **Khóa chính được chọn:** $PK = \text{episode\_id}$
* **Thuộc tính khóa:** $\{\text{episode\_id}, \text{season\_id}, \text{episode\_number}\}$  
* **Thuộc tính không khóa:** $\{\text{episode\_title}, \text{duration\_minutes}, \text{video\_file\_size\_gb}\}$
* **Tiến trình chứng minh các dạng chuẩn:**
  1. **1NF:** Mọi thuộc tính tiêu đề tập, thời lượng phát, dung lượng video đều mang giá trị đơn vị, nguyên tố $\Rightarrow$ **Đạt 1NF**.
  2. **2NF:** Khóa chính $\text{episode\_id}$ là khóa đơn lẻ $\Rightarrow$ Mọi thuộc tính không khóa đều phụ thuộc đầy đủ vào $\text{episode\_id}$. Xét $CK_2$, các thuộc tính `episode_title`, `duration_minutes`, `video_file_size_gb` phụ thuộc vào toàn bộ cặp $\{\text{season\_id}, \text{episode\_number}\}$, không phụ thuộc một phần $\Rightarrow$ **Đạt 2NF**.
  3. **3NF:** Không tồn tại phụ thuộc hàm bắc cầu giữa các thuộc tính không khóa (ví dụ: `duration_minutes` không suy ra `episode_title` hay `video_file_size_gb`) $\Rightarrow$ **Đạt 3NF**.
  4. **BCNF:** Với mọi phụ thuộc hàm không tầm thường trong $F$, vế trái đều là Siêu khóa $\Rightarrow$ **Đạt BCNF**.

---

## PHẦN III: TỪ ĐIỂN DỮ LIỆU CHUẨN HÓA (DATA DICTIONARY - ISO/IEC 11179)

---

### 1. Bảng dữ liệu: `GENRE` (Danh mục Thể loại phim)
* **Ý nghĩa thực thể:** Bảng danh mục chuẩn hóa lưu trữ tên các thể loại phim phục vụ phân loại và lọc nội dung cho toàn bộ hệ thống Mini-Netflix.

| Tên thuộc tính | Kiểu dữ liệu | Khóa | Nullable? | Mặc định | Quy tắc nghiệp vụ & Ràng buộc toàn vẹn |
| :--- | :--- | :---: | :---: | :--- | :--- |
| `genre_id` | `INT` | **PK** | **NO** | Auto-increment | Khóa chính tự tăng định danh duy nhất cho từng thể loại. Giá trị $> 0$. |
| `genre_name` | `VARCHAR(50)` | **UK** | **NO** | None | Tên thể loại (Hành động, Hài hước, Kinh dị...). Ràng buộc duy nhất (`UNIQUE`), không được trùng lặp. |

---

### 2. Bảng dữ liệu: `CONTENT_GENRE` (Bảng liên kết Nội dung - Thể loại)
* **Ý nghĩa thực thể:** Bảng trung gian ánh xạ quan hệ Nhiều - Nhiều ($M:N$) giữa tác phẩm `CONTENT` và thể loại `GENRE`, triệt tiêu thuộc tính đa trị theo chuẩn 1NF.

| Tên thuộc tính | Kiểu dữ liệu | Khóa | Nullable? | Mặc định | Quy tắc nghiệp vụ & Ràng buộc toàn vẹn |
| :--- | :--- | :---: | :---: | :--- | :--- |
| `content_id` | `INT` | **PK, FK** | **NO** | None | Khóa ngoại tham chiếu đến `CONTENT(content_id)`. Xóa Content thì tự động xóa liên kết (`ON DELETE CASCADE`). |
| `genre_id` | `INT` | **PK, FK** | **NO** | None | Khóa ngoại tham chiếu đến `GENRE(genre_id)`. Không cho phép xóa Genre nếu đang có phim gán (`ON DELETE RESTRICT`). |

---

### 3. Bảng dữ liệu: `SEASON` (Mùa phim truyền hình)
* **Ý nghĩa thực thể:** Đơn vị phân cấp trung gian thuộc về một `TV_SERIES`, đại diện cho một mùa phát sóng cụ thể, phụ thuộc tồn tại vào phim bộ.

| Tên thuộc tính | Kiểu dữ liệu | Khóa | Nullable? | Mặc định | Quy tắc nghiệp vụ & Ràng buộc toàn vẹn |
| :--- | :--- | :---: | :---: | :--- | :--- |
| `season_id` | `INT` | **PK** | **NO** | Auto-increment | Khóa chính thay thế (Surrogate Key) định danh duy nhất cho từng mùa phim. |
| `content_id` | `INT` | **FK** | **NO** | None | Khóa ngoại tham chiếu đến `TV_SERIES(content_id)`. Bắt buộc phải gắn với 1 TV Series (`ON DELETE CASCADE`). |
| `season_number` | `INT` | None | **NO** | `1` | Số thứ tự mùa phát sóng (Mùa 1, Mùa 2...). Ràng buộc miền: `CHECK (season_number >= 1)`. |
| `season_name` | `VARCHAR(100)`| None | **YES** | NULL | Tên mùa phát sóng riêng biệt (ví dụ: "Phần 1: Khởi nguồn"). Cho phép NULL. |
| `release_date` | `DATE` | None | **YES** | NULL | Ngày phát hành chính thức của mùa phim. |

* **Ràng buộc cấp bảng (Table-level Constraint):**
  $$\text{CONSTRAINT } \text{uk\_series\_season\_number} \text{ UNIQUE (content\_id, season\_number)}$$
  *(Đảm bảo trong một bộ phim không bao giờ có hai mùa trùng số thứ tự).*

---

### 4. Bảng dữ liệu: `TV_EPISODE` (Tập phim truyền hình)
* **Ý nghĩa thực thể:** Đơn vị nội dung phát sóng video nhỏ nhất của phim bộ, phụ thuộc tồn tại và định danh hoàn toàn vào một `SEASON`.

| Tên thuộc tính | Kiểu dữ liệu | Khóa | Nullable? | Mặc định | Quy tắc nghiệp vụ & Ràng buộc toàn vẹn |
| :--- | :--- | :---: | :---: | :--- | :--- |
| `episode_id` | `INT` | **PK** | **NO** | Auto-increment | Khóa chính thay thế định danh duy nhất cho từng tập phim phát sóng. |
| `season_id` | `INT` | **FK** | **NO** | None | Khóa ngoại tham chiếu đến `SEASON(season_id)`. Xóa mùa thì tự động xóa các tập con (`ON DELETE CASCADE`). |
| `episode_number` | `INT` | None | **NO** | None | Số thứ tự tập trong mùa (Tập 1, Tập 2...). Ràng buộc miền: `CHECK (episode_number >= 1)`. |
| `episode_title` | `VARCHAR(255)`| None | **NO** | None | Tiêu đề riêng của từng tập phim. Không được để trống (`NOT NULL`). |
| `duration_minutes` | `INT` | None | **NO** | None | Thời lượng phát video tính bằng phút. Ràng buộc miền: `CHECK (duration_minutes > 0)`. |
| `video_file_size_gb`| `DECIMAL(6,2)`| None | **NO** | None | Dung lượng tệp video tính bằng Gigabyte. Ràng buộc miền: `CHECK (video_file_size_gb > 0.00)`. |

* **Ràng buộc cấp bảng (Table-level Constraint):**
  $$\text{CONSTRAINT } \text{uk\_season\_episode\_number} \text{ UNIQUE (season\_id, episode_number)}$$
  *(Đảm bảo trong cùng một mùa phim không thể có hai tập trùng số thứ tự).*
