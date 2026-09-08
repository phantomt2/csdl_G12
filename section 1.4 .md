# CHỦ ĐỀ 4: YÊU CẦU CHỨC NĂNG DỮ LIỆU (SECTION 1.4 - FUNCTIONAL REQUIREMENTS)
**Tiêu chuẩn áp dụng: ISO/IEC/IEEE 29148:2018 (Requirements Engineering - Data-Centric Transactions)**

---

## 1.4.1 TỔNG QUAN NGUYÊN TẮC THIẾT KẾ YÊU CẦU CHỨC NĂNG CSDL

Khác với yêu cầu phần mềm hướng giao diện (UI-driven requirements), các yêu cầu chức năng trong thiết kế cơ sở dữ liệu được định nghĩa dưới dạng **Các giao tác lấy dữ liệu làm trung tâm (Data-Centric Transactions)**. Mỗi yêu cầu chức năng (FR) mô tả chi tiết:
* **Tác nhân kích hoạt (Triggering Actor):** Thực thể hoặc vai trò khởi phát hành vi giao tác.
* **Thực thể / Bảng tác động (Target Entities/Tables):** Danh sách các bảng chịu ảnh hưởng trực tiếp qua các thao tác nguyên tử `INSERT`, `UPDATE`, `DELETE`, `SELECT`.
* **Tiền điều kiện (Preconditions):** Trạng thái bắt buộc của CSDL trước khi thực thi giao tác.
* **Trình tự giao tác dữ liệu (Data Transaction Execution):** Chuỗi thao tác CRUD nội bộ bảo đảm tính toàn vẹn và nhất quán dữ liệu.
* **Hậu điều kiện (Postconditions):** Trạng thái nhất quán mới của dữ liệu sau khi hoàn tất giao tác.
* **Ràng buộc nghiệp vụ liên đới (Linked Business Rules):** Mã quy tắc nghiệp vụ (ở Mục 1.3) chi phối trực tiếp giao tác.

---

## 1.4.2 CHI TIẾT CÁC GIAO TÁC CHỨC NĂNG DỮ LIỆU (FR01 – FR06)

### FR01: Đăng ký tài khoản và Thiết lập gói cước thuê bao (Account Registration & Subscription Setup)
* **Tác nhân:** Khách vãng lai (`CASUAL_VISITOR` - đối tượng ngoài CSDL).
* **Bảng dữ liệu tương tác:** `ACCOUNT`, `SUBSCRIPTION_TIER`.
* **Tiền điều kiện (Preconditions):**
  * Gói cước được chọn `tier_id` phải tồn tại trong bảng `SUBSCRIPTION_TIER`.
  * Địa chỉ `email` đầu vào chưa từng tồn tại trong bảng `ACCOUNT` (đảm bảo tính duy nhất tuyệt đối).
* **Trình tự giao tác dữ liệu (Data Transaction Flow):**
  1. Kiểm tra tính duy nhất (`UNIQUE`) và định dạng chuẩn RFC 5322 của giá trị `email`.
  2. Thực hiện hàm băm một chiều kèm chuỗi muối ngẫu nhiên (Salted Hash) trên mật khẩu đầu vào để tạo chuỗi `password_hash` an toàn.
  3. Khởi tạo bản ghi mới vào bảng `ACCOUNT`:
     * Sinh tự động khóa chính `account_id`.
     * Gán khóa ngoại `tier_id` tham chiếu đến gói dịch vụ đã chọn.
     * Thiết lập `billing_status = 'ACTIVE'`, `created_at = CURRENT_TIMESTAMP`.
     * Thiết lập thời hạn gói cước `subscription_expires_at = CURRENT_TIMESTAMP + INTERVAL '30 days'`.
* **Hậu điều kiện (Postconditions):** Một bộ dữ liệu `ACCOUNT` mới được ghi nhận thành công; tài khoản chuyển thành chủ thể hợp lệ có quyền đăng nhập và tạo hồ sơ con.
* **Ràng buộc liên đới:** BR01 (Gói cước có hiệu lực duy nhất).

---

### FR02: Quản trị vòng đời Hồ sơ người dùng con (User Profile Lifecycle Management)
* **Tác nhân:** Chủ tài khoản (`ACCOUNT`).
* **Bảng dữ liệu tương tác:** `PROFILE`, `ACCOUNT`, `SUBSCRIPTION_TIER`, `WATCHLIST`, `WATCH_HISTORY`.
* **Tiền điều kiện (Preconditions):**
  * `account_id` hợp lệ và đang ở trạng thái `billing_status = 'ACTIVE'`.
  * Tổng số lượng hồ sơ con hiện có của tài khoản phải nhỏ hơn định mức cho phép:
    $$\text{COUNT(profile\_id)} < \text{SUBSCRIPTION\_TIER.max\_profiles}$$
* **Trình tự giao tác dữ liệu (Data Transaction Flow):**
  * **Thêm mới hồ sơ (Create Profile):**
    1. Kiểm tra hạn mức `max_profiles` từ bảng `SUBSCRIPTION_TIER` thông qua liên kết khóa ngoại của `ACCOUNT`.
    2. Chèn bản ghi mới vào bảng `PROFILE` gồm: `account_id`, `profile_name`, `avatar_url`, `is_kids_mode`, `maturity_rating`, `pin_code` (nếu cài đặt).
  * **Cập nhật hồ sơ (Update Profile):** Cập nhật tên hiển thị, thay đổi cờ `is_kids_mode`, ảnh đại diện hoặc ngưỡng tuổi `maturity_rating`.
  * **Xóa hồ sơ (Delete Profile):** 
    1. Kích hoạt xóa dây chuyền (`ON DELETE CASCADE`) toàn bộ các bản ghi trong `WATCHLIST` và `WATCH_HISTORY` có `profile_id` tương ứng.
    2. Xóa bản ghi mục tiêu trong bảng `PROFILE`.
* **Hậu điều kiện (Postconditions):** Bản ghi `PROFILE` được cập nhật trong CSDL; tính toàn vẹn tham chiếu của các bảng tương tác con được bảo toàn.
* **Ràng buộc liên đới:** BR02 (Định mức số lượng Hồ sơ theo gói), BR04 (Kiểm soát phụ huynh).

---

### FR03: Quản trị Cấu trúc phân cấp và Siêu dữ liệu Nội dung (Content Hierarchy & Metadata Management)
* **Tác nhân:** Quản trị viên hệ thống / Quản trị nội dung (`ADMIN`).
* **Bảng dữ liệu tương tác:** `CONTENT`, `MOVIE`, `TV_SERIES`, `SEASON`, `TV_EPISODE`, `GENRE`, `PERSON`, `CONTENT_GENRE`, `CONTENT_CAST`.
* **Tiền điều kiện (Preconditions):** Quản trị viên được xác thực quyền quản trị cấp cơ sở dữ liệu (`Admin/DBA Role`).
* **Trình tự giao tác dữ liệu (Data Transaction Flow):**
  * **Xuất bản Phim lẻ (Publish Movie):**
    1. Chèn siêu dữ liệu chung vào bảng cha `CONTENT`: `content_id`, `title`, `release_year`, `age_classification`, `description`.
    2. Chèn dữ liệu kỹ thuật đặc thù vào bảng con `MOVIE`: `content_id` (vừa là PK, vừa là FK), `duration_minutes`, `video_file_url`.
  * **Xuất bản Phim bộ truyền hình (Publish TV Series & Hierarchy):**
    1. Tạo bản ghi thực thể gốc `TV_SERIES` (`series_id`, `series_title`, `synopsis`).
    2. Tạo thực thể trung gian `SEASON` (`season_id`, `series_id` (FK), `season_number`).
    3. Tạo bản ghi cha `CONTENT` đại diện cho tập phim nghe nhìn.
    4. Tạo bản ghi thực thể con kiêm thực thể yếu `TV_EPISODE`: `content_id` (PK/FK), `season_id` (FK), `episode_number`, `duration_minutes`, `video_file_url`.
  * **Gán nhãn Phân loại đa trị:** Chèn các bộ khóa tổng hợp vào bảng quan hệ nhiều - nhiều `CONTENT_GENRE` `(content_id, genre_id)` và `CONTENT_CAST` `(content_id, person_id, role, character_name)`.
* **Hậu điều kiện (Postconditions):** Đồ thị phân cấp nội dung được lưu trữ nhất quán, không xảy ra mâu thuẫn chuyên biệt hóa hoặc tập phim mồ côi.
* **Ràng buộc liên đới:** BR05 (Chuyên biệt hóa EER Disjoint & Total), BR06 (Phân cấp Phim bộ), BR07 (Metadata đa trị).

---

### FR04: Quản lý Danh sách xem cá nhân hóa (Watchlist Management)
* **Tác nhân:** Hồ sơ người dùng (`PROFILE`).
* **Bảng dữ liệu tương tác:** `WATCHLIST`, `PROFILE`, `CONTENT`.
* **Tiền điều kiện (Preconditions):**
  * `profile_id` và `content_id` phải tồn tại hợp lệ trong hệ thống.
  * Phân loại độ tuổi của nội dung phải thỏa mãn ngưỡng kiểm soát phụ huynh của hồ sơ:
    $$\text{CONTENT.age\_classification} \le \text{PROFILE.maturity\_rating}$$
* **Trình tự giao tác dữ liệu (Data Transaction Flow):**
  * **Thêm nội dung vào danh sách (Bookmark Content):**
    1. Kiểm tra sự tồn tại của cặp `(profile_id, content_id)` trong bảng `WATCHLIST`.
    2. Nếu chưa tồn tại, thực thi lệnh chèn:
       ```sql
       INSERT INTO WATCHLIST (profile_id, content_id, added_at)
       VALUES (:profile_id, :content_id, CURRENT_TIMESTAMP);
       ```
    3. Nếu đã tồn tại, hủy bỏ giao tác (từ chối lưu trùng lặp).
  * **Xóa nội dung khỏi danh sách (Remove Bookmark):** Thực thi lệnh xóa bản ghi dựa trên cặp khóa chính tổng hợp `(profile_id, content_id)`.
  * **Truy vấn danh sách theo dõi (Fetch Watchlist):** Thực hiện phép kết nối (`JOIN`) giữa `WATCHLIST` và `CONTENT`, sắp xếp giảm dần theo thời gian đánh dấu (`ORDER BY added_at DESC`).
* **Hậu điều kiện (Postconditions):** Bản ghi liên kết được cập nhật; danh sách xem của các hồ sơ khác trong cùng tài khoản hoàn toàn không bị ảnh hưởng.
* **Ràng buộc liên đới:** BR04 (Kiểm soát phụ huynh), BR08 (Độc lập danh sách xem).

---

### FR05: Ghi nhận Lịch sử xem và Đồng bộ tiến trình phát tiếp nối (Watch History & Playback Sync)
* **Tác nhân:** Hồ sơ người dùng (`PROFILE`) / Trình phát video hệ thống.
* **Bảng dữ liệu tương tác:** `WATCH_HISTORY`, `CONTENT`, `MOVIE`, `TV_EPISODE`.
* **Tiền điều kiện (Preconditions):** Video được phát phải là một đơn vị nội dung cụ thể có thời lượng phát sóng xác định (`MOVIE` hoặc `TV_EPISODE`).
* **Trình tự giao tác dữ liệu (Data Transaction Flow):**
  1. Khi bắt đầu hoặc tạm dừng phát video, hệ thống tiếp nhận tham số tiến độ thực tế `watched_duration_seconds`.
  2. Kiểm tra bản ghi tiến trình trong bảng `WATCH_HISTORY` theo bộ đôi `(profile_id, content_id)`:
     * **Nếu chưa tồn tại:** Chèn mới bản ghi với `last_watched_timestamp = CURRENT_TIMESTAMP` và `watched_duration_seconds` ban đầu.
     * **Nếu đã tồn tại:** Cập nhật bản ghi hiện hữu:
       ```sql
       UPDATE WATCH_HISTORY
       SET watched_duration_seconds = :current_seconds,
           last_watched_timestamp = CURRENT_TIMESTAMP
       WHERE profile_id = :profile_id AND content_id = :content_id;
       ```
  3. **Đánh giá điều kiện hoàn thành:** Đối chiếu thời lượng đã xem với tổng thời lượng tác phẩm (`total_duration` lấy từ `MOVIE` hoặc `TV_EPISODE`):
     * Nếu $\text{watched\_duration\_seconds} \ge 0.9 \times (\text{duration\_minutes} \times 60)$:
       Tự động kích hoạt cập nhật cờ hoàn thành `is_completed = TRUE`.
  4. **Truy vấn phát tiếp nối (Resume Playback Query):** Khi người dùng mở lại nội dung, hệ thống thực hiện `SELECT watched_duration_seconds` để định vị thanh tua video.
* **Hậu điều kiện (Postconditions):** Trạng thái tiêu thụ nội dung và mốc thời gian tạm dừng mới nhất được lưu vết chính xác, phục vụ tính năng xem tiếp liên tục trên mọi thiết bị.
* **Ràng buộc liên đới:** BR09 (Theo dõi tiến trình phát liên tục).

---

### FR06: Quản lý Phiên phát trực tuyến và Kiểm soát luồng xem đồng thời (Streaming Session & Concurrency Control)
* **Tác nhân:** Hồ sơ người dùng (`PROFILE`) / Hệ thống quản trị phiên.
* **Bảng dữ liệu tương tác:** `STREAMING_SESSION`, `ACCOUNT`, `PROFILE`, `SUBSCRIPTION_TIER`.
* **Tiền điều kiện (Preconditions):** Hồ sơ con gửi yêu cầu bắt đầu phát video (`Play Request`); tài khoản chủ `ACCOUNT` đang ở trạng thái hiệu lực (`billing_status = 'ACTIVE'`).
* **Trình tự giao tác dữ liệu (Data Transaction Flow):**
  1. Xác định `account_id` sở hữu `profile_id` yêu cầu.
  2. Truy xuất chỉ số giới hạn `max_concurrent_streams` từ bảng `SUBSCRIPTION_TIER` của tài khoản.
  3. Đếm số lượng phiên xem đang hoạt động tại thời điểm hiện tại:
     ```sql
     SELECT COUNT(session_id) 
     FROM STREAMING_SESSION 
     WHERE account_id = :account_id AND session_status = 'ACTIVE';
     ```
  4. **Kiểm tra điều kiện biên (Boundary Check):**
     * **Nếu $\text{COUNT} \ge \text{max\_concurrent\_streams}$:** Hủy bỏ giao tác, từ chối cấp phép luồng phát và trả về thông báo lỗi vượt quá số thiết bị cho phép.
     * **Nếu $\text{COUNT} < \text{max\_concurrent\_streams}$:** Chấp thuận phát sóng, khởi tạo bản ghi mới vào `STREAMING_SESSION` gồm: `session_id`, `account_id`, `profile_id`, `content_id`, `device_name`, `started_at = CURRENT_TIMESTAMP`, `session_status = 'ACTIVE'`.
  5. **Đóng phiên (Terminate Session):** Khi người dùng tắt ứng dụng hoặc dừng phát, cập nhật bản ghi tương ứng sang `session_status = 'TERMINATED'` và lưu mốc `ended_at = CURRENT_TIMESTAMP`.
* **Hậu điều kiện (Postconditions):** Luồng phát video được giám sát chặt chẽ theo thời gian thực; tài nguyên phát sóng không vượt quá định mức thương mại của gói cước.
* **Ràng buộc liên đới:** BR03 (Giới hạn luồng phát đồng thời).

---

## 1.4.3 BẢNG MA TRẬN TRUY VẾT QUAN HỆ (TRACEABILITY MATRIX)

| Mã chức năng (FR) | Tên giao tác dữ liệu | Bảng CSDL thao tác chính | Quy tắc nghiệp vụ liên đới (BR) |
| :---: | :--- | :--- | :---: |
| **FR01** | Đăng ký tài khoản & gán gói cước | `ACCOUNT`, `SUBSCRIPTION_TIER` | BR01 |
| **FR02** | Quản trị vòng đời hồ sơ con | `PROFILE`, `ACCOUNT`, `SUBSCRIPTION_TIER` | BR02, BR04 |
| **FR03** | Xuất bản & phân cấp cây nội dung | `CONTENT`, `MOVIE`, `TV_SERIES`, `SEASON`, `TV_EPISODE` | BR05, BR06, BR07 |
| **FR04** | Đánh dấu & truy xuất danh sách xem | `WATCHLIST`, `PROFILE`, `CONTENT` | BR04, BR08 |
| **FR05** | Đồng bộ tiến độ phát & hoàn thành | `WATCH_HISTORY`, `CONTENT`, `MOVIE`, `TV_EPISODE` | BR09 |
| **FR06** | Kiểm soát luồng xem đồng thời | `STREAMING_SESSION`, `ACCOUNT`, `SUBSCRIPTION_TIER` | BR03 |