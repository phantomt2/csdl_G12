# CHỦ ĐỀ 3: QUY TẮC NGHIỆP VỤ VÀ RÀNG BUỘC TOÀN VẸN (SECTION 1.3 - BUSINESS RULES & CONSTRAINTS)
**Tiêu chuẩn áp dụng: ISO/IEC/IEEE 29148 (SRS Requirements & Business Rules)**

---

## 1.3.1 QUY TẮC NGHIỆP VỤ (BUSINESS RULES - DATA LOGIC)

Các quy tắc nghiệp vụ dưới đây định nghĩa logic vận hành và quản lý dữ liệu của nền tảng xem phim trực tuyến Mini-Netflix. Các quy tắc này được chuẩn hóa, đánh mã định danh nhằm phục vụ trực tiếp cho việc thiết kế mô hình thực thể liên kết mở rộng (EER) ở Giai đoạn 1 và cài đặt ràng buộc (Constraints, Triggers) trên hệ quản trị CSDL ở Giai đoạn 3.

---

### Nhóm 1: Quản lý Tài khoản & Gói cước (Account & Subscription Rules)

* **BR01 (Gói cước có hiệu lực duy nhất - Active Subscription):**  
  Tại một thời điểm xác định, mỗi Tài khoản (`Account/User`) chỉ được liên kết với **tối đa một** Gói dịch vụ (`Subscription Tier/Plan`) đang ở trạng thái hiệu lực (`Active`). Khách hàng có thể thực hiện nâng cấp (Upgrade) hoặc hạ cấp (Downgrade) gói cước; khi đó hệ thống sẽ cập nhật trạng thái kết thúc của gói hiện tại và thiết lập thời hạn hiệu lực cho gói cước mới.

* **BR02 (Định mức số lượng Hồ sơ theo gói - Profile Quota):**  
  Số lượng Hồ sơ người dùng (`User Profiles`) trực thuộc một Tài khoản bị chặn trên bởi thuộc tính `max_profiles` được quy định trong Gói dịch vụ mà tài khoản đó đang sử dụng:
  $$\text{Số lượng Profile hiện có} \le \text{Subscription\_Tier.max\_profiles}$$
  *(Ví dụ: Gói Basic cho phép tối đa 1 Profile; Gói Standard cho phép tối đa 2 Profiles; Gói Premium cho phép tối đa 5 Profiles).*

* **BR03 (Giới hạn luồng phát đồng thời - Concurrent Streams):**  
  Số lượng thiết bị hoặc hồ sơ thuộc cùng một tài khoản đang ở trạng thái phát video tại cùng một thời điểm không được vượt quá chỉ số `max_concurrent_streams` của gói thuê bao tương ứng.

---

### Nhóm 2: Quản lý Hồ sơ & Kiểm soát Phụ huynh (Profile & Parental Control Rules)

* **BR04 (Kiểm soát độ tuổi và nội dung an toàn - Parental Control):**  
  Mỗi Hồ sơ người dùng (`Profile`) được cấu hình một ngưỡng phân loại độ tuổi (`maturity_rating`) hoặc bật chế độ dành riêng cho trẻ em (`is_kids_mode = TRUE`). Hệ thống chỉ cho phép Profile truy cập, tìm kiếm và phát các Nội dung (`Content`) có mức xếp hạng độ tuổi (`age_classification`) thấp hơn hoặc bằng mức giới hạn được cài đặt trên Profile đó:
  $$\text{Content.age\_classification} \le \text{Profile.maturity\_rating}$$
  Các nội dung vượt quá giới hạn độ tuổi sẽ bị tự động lọc bỏ khỏi giao diện hoặc yêu cầu xác thực mã PIN phụ huynh trước khi phát.

---

### Nhóm 3: Cấu trúc & Phân cấp Nội dung (Content Hierarchy & Metadata Rules)

* **BR05 (Chuyên biệt hóa nội dung - EER Specialization Disjoint & Total):**  
  Toàn bộ các tác phẩm nghe nhìn phát sóng trên nền tảng bắt buộc phải kế thừa từ thực thể tổng quát `CONTENT` (Ràng buộc tham gia toàn phần - Total Specialization: $\text{Movie} \cup \text{TV\_Episode} = \text{Content}$). Một nội dung chỉ có thể là Phim lẻ (`Movie`) hoặc Tập phim (`TV_Episode`), không thể đồng thời vừa là Phim lẻ vừa là Tập phim (Ràng buộc rời rạc tuyệt đối - Disjoint: $\text{Movie} \cap \text{TV\_Episode} = \emptyset$).

* **BR06 (Cấu trúc phân rã Phim bộ truyền hình - TV Series Hierarchy):**  
  Một Phim bộ (`TV_SERIES`) bao gồm từ 1 đến nhiều Mùa phim (`SEASON`). Mỗi Mùa phim bao gồm từ 1 đến nhiều Tập phim (`TV_EPISODE`). Một Tập phim là một thực thể yếu/phụ thuộc tồn tại, không thể phát hành độc lập ngoài ngữ cảnh của một Season và Series cụ thể.

* **BR07 (Đa thể loại và Đa nhân sự - Multivalued Metadata):**  
  Mỗi Nội dung (`Content`) có thể thuộc về nhiều Thể loại (`Genre`) khác nhau (quan hệ N:M). Đồng thời, mỗi Content có thể gắn liền với danh sách nhiều Đạo diễn (`Director`) và Diễn viên (`Cast`).

---

### Nhóm 4: Tương tác Người dùng & Trải nghiệm Xem (User Activity & Playback Rules)

* **BR08 (Danh sách xem cá nhân hóa độc lập - Watchlist Independence):**  
  Mỗi Profile sở hữu một Danh sách xem (`Watchlist`) hoàn toàn độc lập, tách biệt với các Profile khác trong cùng tài khoản. Quan hệ giữa `Profile` và `Content` trong Watchlist là quan hệ Nhiều - Nhiều (N:M). Một Content chỉ xuất hiện tối đa một lần trong Watchlist của cùng một Profile (duy nhất theo cặp `(profile_id, content_id)`).

* **BR09 (Theo dõi tiến trình phát liên tục - Continuous Playback & Watch History):**  
  Khi một Profile bắt đầu xem một Content (Movie hoặc Episode), hệ thống tự động khởi tạo hoặc cập nhật bản ghi trong Lịch sử xem (`Watch History`):
  * Lưu trữ mốc thời gian tạm dừng xem (`last_watched_timestamp`) và thời lượng thực tế đã xem (`watched_duration_seconds`).
  * Nếu thời lượng đã xem đạt từ **90%** tổng thời lượng nội dung trở lên ($\text{watched\_duration} \ge 0.9 \times \text{duration}$), hệ thống tự động đánh dấu cờ hoàn thành $\text{is\_completed} = \text{TRUE}$.
  * Khi người dùng mở lại nội dung, hệ thống cho phép tiếp tục phát từ mốc thời gian đã tạm dừng (Resume playback).

---

### Nhóm 5: Tương quan & Đề xuất Nội dung (Content Similarity)

* **BR10 (Liên kết nội dung tương đồng - Recursive Similarity):**  
  Một Content có thể liên kết với nhiều Content khác dưới dạng quan hệ đệ quy (Self-referencing Relationship) với điểm số tương đồng đối xứng (`similarity_score` từ 0.00 đến 1.00) để phục vụ cho tính năng hiển thị danh sách "Nội dung tương tự" (More Like This).

---

## 1.3.2 TÍNH TOÀN VẸN VÀ BẢO MẬT (DATA INTEGRITY & SECURITY CONSTRAINTS)

Nhằm đảm bảo cơ sở dữ liệu luôn ở trạng thái nhất quán, không chứa dữ liệu rác hoặc mâu thuẫn, hệ thống thiết lập 3 nhóm ràng buộc cốt lõi:

---

### 1. Toàn vẹn thực thể (Entity Integrity)

* **Định nghĩa & Nguyên tắc:**  
  Ràng buộc toàn vẹn thực thể quy định rằng mọi quan hệ (bảng) trong CSDL bắt buộc phải có một **Khóa chính (Primary Key - PK)**. Giá trị của khóa chính phải có tính duy nhất tuyệt đối (`UNIQUE`) và không bao giờ được phép nhận giá trị rỗng (`NOT NULL`). Điều này đảm bảo mỗi hàng dữ liệu đại diện cho một đối tượng xác định, không thể nhầm lẫn.

* **Áp dụng cụ thể trong hệ thống Mini-Netflix:**
  * **Khóa chính đơn (Single PK):**
    * `ACCOUNT`: Khóa chính `account_id` (INT / BIGINT, tự tăng Auto-increment).
    * `SUBSCRIPTION_TIER`: Khóa chính `tier_id` (INT) xác định duy nhất từng gói dịch vụ.
    * `PROFILE`: Khóa chính `profile_id` (INT) xác định duy nhất từng hồ sơ người dùng.
    * `CONTENT`: Khóa chính `content_id` (INT) xác định duy nhất tác phẩm nghe nhìn tổng quát.
    * `TV_SERIES`: Khóa chính `series_id` (INT) xác định duy nhất bộ phim nhiều tập.
    * `SEASON`: Khóa chính `season_id` (INT) xác định duy nhất mùa phát sóng.
  * **Khóa chính của thực thể chuyên biệt hóa (Specialized Subclasses):**
    * `MOVIE`: Sử dụng `content_id` vừa làm Khóa chính (PK), vừa làm Khóa ngoại (FK) tham chiếu đến `CONTENT(content_id)`.
    * `TV_EPISODE`: Sử dụng `content_id` vừa làm Khóa chính (PK), vừa làm Khóa ngoại (FK) tham chiếu đến `CONTENT(content_id)`.
  * **Khóa chính tổng hợp (Composite PK) cho các thực thể liên kết (Associative Entities):**
    * `WATCHLIST`: Khóa chính tổng hợp gồm bộ đôi `(profile_id, content_id)` nhằm triệt tiêu nguy cơ một hồ sơ lưu trùng một bộ phim nhiều lần.
    * `WATCH_HISTORY`: Khóa chính tổng hợp gồm bộ đôi `(profile_id, content_id)` đảm bảo mỗi hồ sơ chỉ duy trì một bản ghi trạng thái xem mới nhất cho mỗi nội dung.
    * `CONTENT_SIMILARITY`: Khóa chính tổng hợp gồm `(content_id_1, content_id_2)`.
    * `CONTENT_GENRE`: Khóa chính tổng hợp gồm `(content_id, genre_id)`.

---

### 2. Ràng buộc miền giá trị (Domain Constraints)

* **Định nghĩa & Nguyên tắc:**  
  Ràng buộc miền giá trị quy định tập hợp các giá trị hợp lệ mà một thuộc tính được phép lưu trữ, bao gồm định dạng kiểu dữ liệu (Data Type), khoảng giá trị cho phép (`CHECK`), tính chất bắt buộc (`NOT NULL`), tính duy nhất (`UNIQUE`) và tập giá trị liệt kê (`ENUM` hoặc danh sách `IN`).

* **Bảng chi tiết các ràng buộc miền giá trị tiêu biểu:**

| Tên thuộc tính | Thực thể / Bảng | Kiểu dữ liệu & Ràng buộc miền | Ý nghĩa nghiệp vụ & Quy tắc hợp lệ |
| :--- | :--- | :--- | :--- |
| `email` | `ACCOUNT` | `VARCHAR(255) NOT NULL UNIQUE` | Tuân thủ định dạng chuẩn email RFC 5322 (chứa ký tự `@` và tên miền hợp lệ); không được trùng lặp. |
| `password_hash` | `ACCOUNT` | `VARCHAR(255) NOT NULL` | Chuỗi mã hóa băm mật khẩu, có độ dài cố định/chuẩn theo thuật toán băm (không rỗng). |
| `price` | `SUBSCRIPTION_TIER` | `DECIMAL(10, 2) NOT NULL CHECK (price >= 0.00)` | Giá cước thuê bao không được âm (cho phép giá bằng 0 đối với gói thử nghiệm Free Trial). |
| `max_profiles` | `SUBSCRIPTION_TIER` | `INT NOT NULL CHECK (max_profiles BETWEEN 1 AND 5)` | Số lượng hồ sơ tối đa trên một tài khoản từ 1 đến 5. |
| `max_concurrent_streams`| `SUBSCRIPTION_TIER` | `INT NOT NULL CHECK (max_concurrent_streams >= 1)` | Số luồng xem đồng thời tối thiểu là 1. |
| `max_resolution` | `SUBSCRIPTION_TIER` | `VARCHAR(20) NOT NULL CHECK (max_resolution IN ('SD', 'HD', 'Full HD', '4K Ultra HD'))` | Chất lượng độ phân giải tối đa chỉ nhận 1 trong 4 chuẩn kỹ thuật cố định. |
| `duration_minutes` | `MOVIE`, `TV_EPISODE` | `INT NOT NULL CHECK (duration_minutes > 0)` | Thời lượng phát video phải là một số nguyên dương (> 0 phút). |
| `watched_duration_seconds`| `WATCH_HISTORY` | `INT NOT NULL CHECK (watched_duration_seconds >= 0)` | Thời lượng đã xem không được âm. |
| `release_year` | `CONTENT` | `INT NOT NULL CHECK (release_year >= 1895 AND release_year <= 2100)` | Năm phát hành hợp lệ từ năm ra đời của điện ảnh (1895) đến các dự án tương lai. |
| `maturity_rating` | `CONTENT`, `PROFILE` | `VARCHAR(10) NOT NULL CHECK (maturity_rating IN ('G', 'PG', 'PG-13', 'R', 'NC-17'))` | Chuẩn xếp hạng độ tuổi theo hệ thống MPAA quốc tế. |
| `similarity_score` | `CONTENT_SIMILARITY` | `DECIMAL(3, 2) NOT NULL CHECK (similarity_score BETWEEN 0.00 AND 1.00)` | Điểm tương quan chuẩn hóa nằm trong đoạn số thực $[0.00, 1.00]$. |
| `is_kids_mode` | `PROFILE` | `BOOLEAN NOT NULL DEFAULT FALSE` | Cờ nhận biết chế độ trẻ em, chỉ nhận giá trị `TRUE` hoặc `FALSE`. |
| `is_completed` | `WATCH_HISTORY` | `BOOLEAN NOT NULL DEFAULT FALSE` | Cờ đánh dấu đã xem xong nội dung, chỉ nhận `TRUE` hoặc `FALSE`. |
| `auto_renew` | `ACCOUNT` | `BOOLEAN NOT NULL DEFAULT TRUE` | Cờ tự động gia hạn gói cước, chỉ nhận `TRUE` hoặc `FALSE`. |

---

### 3. Bảo mật hệ thống & Dữ liệu (Security & Access Control)

Hệ thống triển khai các biện pháp bảo mật thiết yếu nhằm bảo vệ quyền riêng tư người dùng và an toàn dữ liệu:

* **a) Bảo mật xác thực & Băm mật khẩu (Authentication Security):**
  * Tuyệt đối **không lưu trữ mật khẩu ở dạng văn bản thuần (Plaintext)** trong cơ sở dữ liệu.
  * Mật khẩu người dùng bắt buộc phải được mã hóa một chiều thông qua các giải thuật băm mật mã chuẩn công nghiệp có chi phí tính toán cao (như **Argon2id**, **bcrypt** hoặc **PBKDF2**) kèm theo chuỗi muối ngẫu nhiên (Cryptographic Salt) được sinh tự động cho mỗi tài khoản. Điều này vô hiệu hóa hoàn toàn các nguy cơ tấn công dò quét bảng băm (Rainbow Table Attacks) hoặc rò rỉ dữ liệu khi bị trích xuất CSDL.

* **b) Phân quyền theo vai trò (Role-Based Access Control - RBAC đơn giản):**
  Hệ thống thiết lập 3 nhóm vai trò người dùng tương ứng với các giới hạn truy cập dữ liệu:
  * **Khách vãng lai (Guest / Anonymous):**  
    Chỉ có quyền đọc (`SELECT`) thông tin giới thiệu công khai trên các danh mục `CONTENT`, `TV_SERIES`, `GENRE`. Không có quyền truy cập tệp stream video, không có quyền ghi dữ liệu (`INSERT`, `UPDATE`, `DELETE`).
  * **Người dùng thuê bao (Subscriber / Registered User):**  
    * Toàn quyền quản lý và chỉnh sửa thông tin cá nhân của chính tài khoản mình (`ACCOUNT`, `PROFILE`).
    * Có quyền `SELECT`, `INSERT`, `UPDATE`, `DELETE` trên dữ liệu tương tác cá nhân (`WATCHLIST`, `WATCH_HISTORY`) của các Profile thuộc quyền sở hữu của tài khoản mình.
    * **Nguyên tắc cô lập dữ liệu (Data Isolation):** Tuyệt đối không được cấp quyền đọc hoặc thay đổi dữ liệu của tài khoản hoặc hồ sơ thuộc người dùng khác.
  * **Quản trị viên nội dung / Quản trị hệ thống (Admin / DBA):**  
    * Quyền quản trị nội dung: Toàn quyền CRUD trên kho nội dung (`CONTENT`, `MOVIE`, `TV_SERIES`, `SEASON`, `TV_EPISODE`, `GENRE`, `SUBSCRIPTION_TIER`).
    * Bảo vệ quyền riêng tư: Quản trị viên nội dung không được phép can thiệp hoặc xem trộm lịch sử xem cá nhân của người dùng; không thể xem hay đảo ngược mật khẩu gốc của người dùng.

* **c) An toàn dữ liệu trẻ em & Kiểm soát truy vấn (Child Safety & Query Security):**  
  Tất cả các truy vấn trích xuất dữ liệu nội dung phục vụ cho Profile trẻ em (`is_kids_mode = TRUE`) bắt buộc phải áp dụng bộ lọc cưỡng chế ở tầng truy vấn dữ liệu:
  $$\text{WHERE age\_classification IN ('G', 'PG')}$$
  Đảm bảo dữ liệu không phù hợp tuyệt đối không bao giờ được gửi về máy khách (Client Application).
