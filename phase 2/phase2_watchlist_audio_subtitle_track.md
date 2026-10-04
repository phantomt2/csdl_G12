# BÁO CÁO GIAI ĐOẠN 2: THIẾT KẾ LUẬN LÝ & CHUẨN HÓA CƠ SỞ DỮ LIỆU
**Học phần:** Cơ sở dữ liệu | **Dự án:** #2 On-Demand Streaming Platform (Mini-Netflix)  
**Nhóm:** G12 | **Thành viên thực hiện:** Lê Trương Vĩ  
**Đối tượng phân tích:** `WATCHLIST`, `WATCH_HISTORY`, `AUDIO_SUBTITLE_TRACK`  
**Tiêu chuẩn áp dụng:**  
- Thiết kế luận lý: ISO/IEC 19505 (Relational Schema Mapping)  
- Từ điển dữ liệu: ISO/IEC 11179 Metadata Standards  
- Chuẩn hóa hình thức: 1NF $\rightarrow$ 3NF / BCNF (Codd & Boyce-Codd Normal Form)  
- Quy tắc mã hóa: Google SQL Style Guide / SQLStyle.guide  

---

## PHẦN I: ÁNH XẠ LƯỢC ĐỒ QUAN HỆ & RÀNG BUỘC TOÀN VẸN (RELATIONAL SCHEMA MAPPING)

### 1. Ký hiệu hình thức Lược đồ quan hệ

* **Quan hệ `WATCHLIST`** (Ánh xạ từ Thực thể liên kết Associative Entity giải quyết quan hệ $M:N$ giữa `PROFILE` và `CONTENT`):
  $$\mathbf{WATCHLIST}(\underline{\text{profile\_id}}, \underline{\text{content\_id}}, \text{added\_at})$$
  * Khóa chính tổng hợp (Composite PK): `(profile_id, content_id)`
  * Khóa ngoại 1 (FK1): `profile_id` $\rightarrow$ `PROFILE(profile_id)`
  * Khóa ngoại 2 (FK2): `content_id` $\rightarrow$ `CONTENT(content_id)`

* **Quan hệ `WATCH_HISTORY`** (Ánh xạ từ Thực thể liên kết / Nhật ký tiến trình xem phim của người dùng):
  $$\mathbf{WATCH\_HISTORY}(\underline{\text{history\_id}}, \text{profile\_id}, \text{content\_id}, \text{episode\_id}, \text{last\_watched\_timestamp}, \text{stopped\_position\_seconds}, \text{is\_completed})$$
  * Khóa chính thay thế (Surrogate PK): `history_id`
  * Khóa ngoại 1 (FK1): `profile_id` $\rightarrow$ `PROFILE(profile_id)`
  * Khóa ngoại 2 (FK2): `content_id` $\rightarrow$ `CONTENT(content_id)`
  * Khóa ngoại 3 (FK3): `episode_id` $\rightarrow$ `TV_EPISODE(episode_id)` *(cho phép NULL đối với phim lẻ MOVIE)*
  * Khóa tự nhiên phụ (Alternate Key): `(profile_id, content_id)` *(duy trì 1 bản ghi tiến trình gần nhất cho mỗi tác phẩm trên từng profile)*

* **Quan hệ `AUDIO_SUBTITLE_TRACK`** (Ánh xạ từ Thực thể yếu phụ thuộc tồn tại vào nội dung nghe nhìn `CONTENT` hoặc `TV_EPISODE` và danh mục `LANGUAGE`):
  $$\mathbf{AUDIO\_SUBTITLE\_TRACK}(\underline{\text{track\_id}}, \text{content\_id}, \text{episode\_id}, \text{language\_code}, \text{track\_type}, \text{audio\_codec}, \text{file\_url}, \text{is\_default})$$
  * Khóa chính (PK): `track_id`
  * Khóa ngoại 1 (FK1): `content_id` $\rightarrow$ `CONTENT(content_id)` *(gắn với phim lẻ MOVIE, cho phép NULL nếu là tập phim bộ)*
  * Khóa ngoại 2 (FK2): `episode_id` $\rightarrow$ `TV_EPISODE(episode_id)` *(gắn với tập phim bộ TV_EPISODE, cho phép NULL nếu là phim lẻ)*
  * Khóa ngoại 3 (FK3): `language_code` $\rightarrow$ `LANGUAGE(language_code)`

---

### 2. Định nghĩa Khóa ngoại và Toàn vẹn tham chiếu (Referential Integrity Definition)

| Bảng nguồn | Cột khóa ngoại (FK) | Bảng đích tham chiếu | Cột khóa chính (PK) | ON DELETE | ON UPDATE | Ý nghĩa nghiệp vụ / Ràng buộc |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`WATCHLIST`** | `profile_id` | `PROFILE` | `profile_id` | **CASCADE** | **CASCADE** | Một hồ sơ bị xóa thì danh sách theo dõi của hồ sơ đó tự động được giải phóng khỏi hệ thống. |
| **`WATCHLIST`** | `content_id` | `CONTENT` | `content_id` | **CASCADE** | **CASCADE** | Khi một nội dung phim bị gỡ khỏi nền tảng, các mục lưu trong danh sách Watchlist của mọi người dùng tự động bị xóa. |
| **`WATCH_HISTORY`** | `profile_id` | `PROFILE` | `profile_id` | **CASCADE** | **CASCADE** | Xóa hồ sơ người dùng sẽ tự động dọn sạch toàn bộ nhật ký xem tương ứng để bảo đảm quyền riêng tư. |
| **`WATCH_HISTORY`** | `content_id` | `CONTENT` | `content_id` | **CASCADE** | **CASCADE** | Khi một bộ phim bị xóa khỏi hệ thống, toàn bộ nhật ký xem liên quan của tác phẩm đó bị xóa theo. |
| **`WATCH_HISTORY`** | `episode_id` | `TV_EPISODE`| `episode_id` | **CASCADE** | **CASCADE** | Nếu một tập phim cụ thể bị xóa, lịch sử dừng xem ở tập đó bị xóa hoặc cập nhật tương ứng. |
| **`AUDIO_SUBTITLE_TRACK`**| `content_id` | `CONTENT` | `content_id` | **CASCADE** | **CASCADE** | Khi một phim điện ảnh bị xóa, các luồng âm thanh và tệp phụ đề đính kèm tự động bị xóa bỏ. |
| **`AUDIO_SUBTITLE_TRACK`**| `episode_id` | `TV_EPISODE`| `episode_id` | **CASCADE** | **CASCADE** | Khi xóa một tập phim truyền hình, các tệp phụ đề và audio gắn với tập đó tự động bị giải phóng. |
| **`AUDIO_SUBTITLE_TRACK`**| `language_code`| `LANGUAGE` | `language_code`| **RESTRICT** | **CASCADE** | Chặn hành vi xóa một mã ngôn ngữ trong danh mục nếu đang có tệp phụ đề/âm thanh tham chiếu đến. |

---

## PHẦN II: CHỨNG MINH CHUẨN HÓA HÌNH THỨC (FORMAL NORMALIZATION PROOFS)

---

### 1. Chuẩn hóa quan hệ `WATCHLIST`

* **Tập thuộc tính:** $R = \{\text{profile\_id}, \text{content\_id}, \text{added\_at}\}$
* **Tập Phụ thuộc hàm ($F$):**
  $$f_1: \{\text{profile\_id}, \text{content\_id}\} \rightarrow \text{added\_at}$$
* **Tập Khóa ứng viên (Candidate Keys):**
  $$(\{\text{profile\_id}, \text{content\_id}\})^+ = \{\text{profile\_id}, \text{content\_id}, \text{added\_at}\} = R \Rightarrow CK = \{\text{profile\_id}, \text{content\_id}\}$$
* **Khóa chính được chọn:** $PK = \{\text{profile\_id}, \text{content\_id}\}$
* **Thuộc tính khóa:** $\{\text{profile\_id}, \text{content\_id}\}$  
* **Thuộc tính không khóa:** $\{\text{added\_at}\}$
* **Tiến trình chứng minh các dạng chuẩn:**
  1. **Dạng chuẩn 1 (1NF):** Mỗi ô dữ liệu đều chứa giá trị nguyên tố (Atomic values), thời điểm thêm `added_at` là một mốc thời gian đơn trị, không có thuộc tính lặp $\Rightarrow$ **Đạt 1NF**.
  2. **Dạng chuẩn 2 (2NF):** Thuộc tính không khóa duy nhất là `added_at` phụ thuộc vào toàn bộ cặp khóa chính $\{\text{profile\_id}, \text{content\_id}\}$ (chỉ khi biết rõ hồ sơ nào thêm bộ phim nào thì mới xác định được thời điểm thêm). Không tồn tại phụ thuộc từng phần vào `profile_id` hay `content_id` riêng lẻ $\Rightarrow$ **Đạt 2NF**.
  3. **Dạng chuẩn 3 (3NF):** Chỉ có một thuộc tính không khóa duy nhất nên không thể tồn tại phụ thuộc bắc cầu giữa các thuộc tính không khóa $\Rightarrow$ **Đạt 3NF**.
  4. **Dạng chuẩn Boyce-Codd (BCNF):** Phụ thuộc hàm không tầm thường duy nhất $f_1$ có vế trái $\{\text{profile\_id}, \text{content\_id}\}$ chính là Siêu khóa (Superkey) $\Rightarrow$ **Đạt BCNF**.

---

### 2. Chuẩn hóa quan hệ `WATCH_HISTORY`

* **Tập thuộc tính:** 
  $$R = \{\text{history\_id}, \text{profile\_id}, \text{content\_id}, \text{episode\_id}, \text{last\_watched\_timestamp}, \text{stopped\_position\_seconds}, \text{is\_completed}\}$$
* **Tập Phụ thuộc hàm ($F$):**
  $$f_1: \text{history\_id} \rightarrow \{\text{profile\_id}, \text{content\_id}, \text{episode\_id}, \text{last\_watched\_timestamp}, \text{stopped\_position\_seconds}, \text{is\_completed}\}$$
  $$f_2: \{\text{profile\_id}, \text{content\_id}\} \rightarrow \{\text{history\_id}, \text{episode\_id}, \text{last\_watched\_timestamp}, \text{stopped\_position\_seconds}, \text{is\_completed}\}$$
* **Tập Khóa ứng viên (Candidate Keys):**
  $$CK_1 = \{\text{history\_id}\} \quad (\text{Khóa thay thế - Surrogate Key})$$
  $$CK_2 = \{\text{profile\_id}, \text{content\_id}\} \quad (\text{Khóa tự nhiên - Natural Key biểu diễn tiến trình Continue Watching})$$
* **Khóa chính được chọn:** $PK = \text{history\_id}$
* **Thuộc tính khóa:** $\{\text{history\_id}, \text{profile\_id}, \text{content\_id}\}$  
* **Thuộc tính không khóa:** $\{\text{episode\_id}, \text{last\_watched\_timestamp}, \text{stopped\_position\_seconds}, \text{is\_completed}\}$
* **Tiến trình chứng minh các dạng chuẩn:**
  1. **1NF:** Tất cả các thuộc tính định danh, mốc thời gian, số giây dừng xem và cờ trạng thái Boolean đều mang giá trị đơn nguyên tố $\Rightarrow$ **Đạt 1NF**.
  2. **2NF:** Khóa chính $\text{history\_id}$ là khóa đơn lẻ $\Rightarrow$ Mọi thuộc tính không khóa đều phụ thuộc hàm đầy đủ vào khóa chính. Đồng thời, xét khóa ứng viên $CK_2 = \{\text{profile\_id}, \text{content\_id}\}$, toàn bộ tiến trình dừng xem và trạng thái hoàn thành phụ thuộc vào cả hồ sơ lẫn bộ phim đang xem, không phụ thuộc một phần $\Rightarrow$ **Đạt 2NF**.
  3. **3NF:** Các thuộc tính không khóa (`last_watched_timestamp`, `stopped_position_seconds`, `is_completed`) độc lập với nhau, không suy ra nhau (ví dụ: biết số giây dừng xem không thể suy ra thời điểm xem thực tế gần nhất). Không tồn tại phụ thuộc bắc cầu qua thuộc tính không khóa $\Rightarrow$ **Đạt 3NF**.
  4. **BCNF:** Với cả hai phụ thuộc hàm $f_1$ và $f_2$, các vế xác định ($\text{history\_id}$ và $\{\text{profile\_id}, \text{content\_id}\}$) đều là Siêu khóa của quan hệ $\Rightarrow$ **Đạt BCNF**.

---

### 3. Chuẩn hóa quan hệ `AUDIO_SUBTITLE_TRACK`

* **Tập thuộc tính:** 
  $$R = \{\text{track\_id}, \text{content\_id}, \text{episode\_id}, \text{language\_code}, \text{track\_type}, \text{audio\_codec}, \text{file\_url}, \text{is\_default}\}$$
* **Tập Phụ thuộc hàm ($F$):**
  $$f_1: \text{track\_id} \rightarrow \{\text{content\_id}, \text{episode\_id}, \text{language\_code}, \text{track\_type}, \text{audio\_codec}, \text{file\_url}, \text{is\_default}\}$$
  $$f_2: \text{file\_url} \rightarrow \{\text{track\_id}, \text{content\_id}, \text{episode\_id}, \text{language\_code}, \text{track\_type}, \text{audio\_codec}, \text{is\_default}\}$$
* **Tập Khóa ứng viên (Candidate Keys):**
  $$CK_1 = \{\text{track\_id}\} \quad (\text{Khóa thay thế định danh luồng đa phương tiện})$$
  $$CK_2 = \{\text{file\_url}\} \quad (\text{Đường dẫn tệp tài nguyên tĩnh trên CDN là duy nhất})$$
* **Khóa chính được chọn:** $PK = \text{track\_id}$
* **Thuộc tính khóa:** $\{\text{track\_id}, \text{file\_url}\}$  
* **Thuộc tính không khóa:** $\{\text{content\_id}, \text{episode\_id}, \text{language\_code}, \text{track\_type}, \text{audio\_codec}, \text{is\_default}\}$
* **Tiến trình chứng minh các dạng chuẩn:**
  1. **1NF:** Mọi thuộc tính mã số, mã ngôn ngữ, kiểu phân loại, đường dẫn URL tệp đều là giá trị đơn nguyên tử $\Rightarrow$ **Đạt 1NF**.
  2. **2NF:** Khóa chính $\text{track\_id}$ chỉ gồm một thuộc tính đơn, do đó không thể tồn tại phụ thuộc hàm từng phần vào khóa chính $\Rightarrow$ **Đạt 2NF**.
  3. **3NF:** Không tồn tại phụ thuộc bắc cầu giữa các thuộc tính không khóa (ví dụ: `language_code` không quyết định `audio_codec` hay `track_type`) $\Rightarrow$ **Đạt 3NF**.
  4. **BCNF:** Với mọi phụ thuộc hàm không tầm thường trong $F$, các vế trái ($\text{track\_id}$ và $\text{file\_url}$) đều là Siêu khóa $\Rightarrow$ **Đạt BCNF**.

---

## PHẦN III: TỪ ĐIỂN DỮ LIỆU CHUẨN HÓA (DATA DICTIONARY - ISO/IEC 11179)

---

### 1. Bảng dữ liệu: `WATCHLIST` (Danh sách theo dõi / Xem sau)
* **Ý nghĩa thực thể:** Bảng liên kết trung gian thể hiện danh sách các sản phẩm nghe nhìn (phim điện ảnh hoặc phim bộ) mà từng hồ sơ người dùng (`PROFILE`) đánh dấu để theo dõi hoặc xem sau (BR-07, FR-04).

| Tên thuộc tính | Kiểu dữ liệu | Khóa | Nullable? | Mặc định | Quy tắc nghiệp vụ & Ràng buộc toàn vẹn |
| :--- | :--- | :---: | :---: | :--- | :--- |
| `profile_id` | `INT` | **PK, FK** | **NO** | None | Khóa ngoại tham chiếu đến `PROFILE(profile_id)`. Xóa Profile thì tự động giải phóng mục danh sách (`ON DELETE CASCADE`). |
| `content_id` | `INT` | **PK, FK** | **NO** | None | Khóa ngoại tham chiếu đến `CONTENT(content_id)`. Xóa nội dung phim thì tự động gỡ khỏi Watchlist (`ON DELETE CASCADE`). |
| `added_at` | `DATETIME` | None | **NO** | `CURRENT_TIMESTAMP` | Thời điểm người dùng nhấn thêm nội dung vào danh sách. |

---

### 2. Bảng dữ liệu: `WATCH_HISTORY` (Nhật ký tiến trình xem phim)
* **Ý nghĩa thực thể:** Lưu trữ lịch sử phát và tiến trình dừng xem thực tế của từng hồ sơ cá nhân đối với từng nội dung, hỗ trợ tính năng tiếp tục xem (Continue Watching) và ghi nhận tỷ lệ xem hoàn thành (BR-06, FR-05).

| Tên thuộc tính | Kiểu dữ liệu | Khóa | Nullable? | Mặc định | Quy tắc nghiệp vụ & Ràng buộc toàn vẹn |
| :--- | :--- | :---: | :---: | :--- | :--- |
| `history_id` | `INT` | **PK** | **NO** | Auto-increment | Khóa chính thay thế định danh duy nhất cho từng bản ghi nhật ký phát nội dung. |
| `profile_id` | `INT` | **FK** | **NO** | None | Khóa ngoại tham chiếu đến `PROFILE(profile_id)`. Xóa hồ sơ tự động xóa nhật ký xem (`ON DELETE CASCADE`). |
| `content_id` | `INT` | **FK** | **NO** | None | Khóa ngoại tham chiếu đến `CONTENT(content_id)`. Xóa tác phẩm tự động xóa nhật ký (`ON DELETE CASCADE`). |
| `episode_id` | `INT` | **FK** | **YES** | NULL | Khóa ngoại tham chiếu đến `TV_EPISODE(episode_id)`. Ghi nhận tập phim cụ thể đang xem dở; mang giá trị NULL nếu nội dung là phim lẻ `MOVIE`. |
| `last_watched_timestamp` | `DATETIME` | None | **NO** | `CURRENT_TIMESTAMP` | Thời điểm phát sinh lần xem gần nhất của người dùng. |
| `stopped_position_seconds`| `INT` | None | **NO** | `0` | Vị trí tạm dừng phát tính bằng giây. Ràng buộc miền giá trị: `CHECK (stopped_position_seconds >= 0)`. |
| `is_completed` | `BOOLEAN` | None | **NO** | `FALSE` | Cờ trạng thái ghi nhận xem hoàn tất; tự động bật thành TRUE khi người dùng xem đạt từ 90% thời lượng tác phẩm (FR-05). |

* **Ràng buộc cấp bảng (Table-level Constraint):**
```sql
CONSTRAINT uk_profile_content_history UNIQUE (profile_id, content_id)