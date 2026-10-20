--- BUSINESS_RULES.md ---

# BUSINESS RULES & CONSTRAINTS – Mini-Netflix (Nhóm G12)

Tài liệu này tổng hợp các quy tắc nghiệp vụ được thực thi bởi Database (Triggers, Constraints) và RBAC. Frontend cần đảm bảo hiển thị thông báo lỗi chính xác khi các quy tắc này bị vi phạm.

## 1. Quy tắc Nghiệp vụ (Business Rules)

### BR-01: Giới hạn số lượng Profile
- **Mô tả:** Mỗi tài khoản chỉ được tạo tối đa `max_profiles_allowed` hồ sơ, tùy thuộc vào gói cước (`subscription_tier`).
- **Cơ chế thực thi:** Trigger `trg_check_profile_limit_before_insert` (BEFORE INSERT ON `profile`).
- **Hành vi của DB:** Nếu số lượng Profile hiện tại của tài khoản đã đạt hoặc vượt giới hạn, trigger sẽ gọi `SIGNAL SQLSTATE '45000'` và chặn giao dịch.
- **Thông báo lỗi từ DB:**
  > `Vi pham BR-01/FR-02: Tai khoan da dat gioi han so luong Profile toi da cua goi cuoc!`
- **Yêu cầu FE:** Khi nhận mã lỗi 409 từ API `POST /profiles`, hiển thị nguyên văn thông báo trên. Nút "Tạo Profile" nên hiển thị trạng thái disabled nếu đã đạt giới hạn (dựa trên dữ liệu từ API).

### BR-06: Ghi nhận tiến trình xem
- **Mô tả:** Hệ thống phải lưu lại thời điểm và vị trí dừng xem của người dùng để có thể "Tiếp tục xem" (Continue Watching).
- **Cơ chế:** Ghi vào bảng `watch_history`. Nếu chưa có bản ghi (profile_id, content_id) thì INSERT; nếu đã có thì UPDATE `last_watched_timestamp` và `stopped_position_seconds`.
- **Yêu cầu FE:** Cung cấp slider chọn vị trí dừng (giây) và checkbox "Đã xem xong" (`is_completed`).

### BR-07: Danh sách xem sau (Watchlist)
- **Mô tả:** Cho phép người dùng lưu phim vào danh sách cá nhân để xem sau.
- **Cơ chế:** Thêm/xóa bản ghi trong bảng `watchlist` với khóa chính phức hợp `(profile_id, content_id)`.
- **Yêu cầu FE:** Hiển thị trạng thái "Đã có trong Watchlist" và cho phép toggle thêm/xóa.

### BR-09: Bảo vệ Trẻ em (Kids Mode)
- **Mô tả:** Hồ sơ có `is_kids = TRUE` tuyệt đối không được xem nội dung có nhãn `R` hoặc `NC-17`.
- **Cơ chế thực thi:** 
  - **Tầng đọc (Read):** Backend tự động thêm điều kiện `WHERE rating_age NOT IN ('R', 'NC-17')` vào API `/catalog` khi `kids=true`.
  - **Tầng ghi (Write):** Trigger `trg_check_kids_rating_before_watch` (BEFORE INSERT ON `watch_history`) sẽ chặn nếu cố tình ghi dữ liệu xem phim R/NC-17 cho hồ sơ trẻ em.
- **Thông báo lỗi từ DB:**
  > `Vi pham BR-09: Ho so tre em (is_kids = TRUE) bi chan truy cap noi dung gan nhan R va NC-17!`
- **Yêu cầu FE:** 
  - Hiển thị banner cảnh báo khi đang ở Kids Mode.
  - **Quan trọng:** Giữ nguyên nút toggle "Demo Giảng viên" (bypass filter) để có thể cố tình chọn phim R và test trigger chặn ở tầng ghi.

---

## 2. Ràng buộc Toàn vẹn Dữ liệu (Data Integrity Constraints)

Các ràng buộc này nằm trong `01_schema.sql`. Khi vi phạm, DB sẽ trả về lỗi và Frontend cần hiển thị thông báo phù hợp.

| Tên ràng buộc | Bảng | Mô tả | Mã lỗi MySQL |
|---|---|---|---|
| `chk_tier_price` | `subscription_tier` | Giá gói cước phải >= 0 | 3819 |
| `chk_tier_max_profiles` | `subscription_tier` | Số profile tối đa từ 1 đến 5 | 3819 |
| `chk_account_status` | `user_account` | Trạng thái chỉ nhận `ACTIVE`, `SUSPENDED`, `CANCELED` | 3819 |
| `uq_profile_account_name` | `profile` | Tên profile không được trùng trong cùng một tài khoản | 1062 |
| `chk_content_release_year` | `content` | Năm phát hành từ 1888 đến 2100 | 3819 |
| `chk_movie_duration` | `movie` | Thời lượng phim phải > 0 | 3819 |
| `uq_season_series_number` | `season` | Số mùa không được trùng trong cùng một series | 1062 |
| `uq_watch_history_profile_content` | `watch_history` | Mỗi cặp (profile, content) chỉ có 1 bản ghi lịch sử | 1062 |

*Ghi chú cho FE:* Mã lỗi `1062` là lỗi trùng lặp (Duplicate entry). Mã lỗi `3819` là lỗi vi phạm CHECK constraint. Backend nên bắt các lỗi này và trả về message thân thiện, nhưng FE vẫn nên có fallback hiển thị lỗi chung.

---

## 3. Phân quyền Hệ thống (RBAC)

Hệ thống định nghĩa 3 role trong `05_rbac_security.sql`. Frontend cần ẩn/hiện các thành phần UI tương ứng.

| Role | Quyền hạn chính | Ghi chú cho FE |
|---|---|---|
| `role_system_admin` | Toàn quyền trên `mini_netflix.*` | Được phép xem `password_hash`, được chạy SQL tùy ý, quản lý users. |
| `role_content_manager` | SELECT/INSERT/UPDATE/DELETE trên các bảng nội dung (`content`, `movie`, `tv_series`, `genre`, v.v.) | **Tuyệt đối không được xem** bảng `user_account`. Ẩn tab "Quản trị Tài khoản" trên UI. |
| `role_streaming_client` | SELECT trên catalog, INSERT/UPDATE trên `watch_history`, INSERT/DELETE trên `watchlist`. | Không được DELETE `watch_history` (đã bị REVOKE). |

---

## 4. Các Test Case Phủ định (Dành cho Demo)

Dựa trên `06_negative_test_cases.sql`, đây là các kịch bản Frontend cần hỗ trợ để chứng minh tính đúng đắn của DB:

1. **Test BR-01:** Tạo profile thứ 6 (vượt giới hạn của gói Basic) → Phải hiện lỗi trigger.
2. **Test BR-09:** Dùng profile Kids, bật bypass, chọn phim R, bấm "Lưu tiến trình" → Phải hiện lỗi trigger.
3. **Test CHECK constraint:** Cố tình nhập thời lượng phim âm hoặc năm phát hành không hợp lệ → Backend từ chối, FE hiển thị lỗi validate.
4. **Test UNIQUE:** Tạo 2 profile cùng tên trong 1 tài khoản → Phải hiện lỗi trùng lặp.
