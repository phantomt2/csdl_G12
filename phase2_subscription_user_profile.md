# Phase 2: Logical Design & Normalization

## 1. Ánh xạ Lược đồ quan hệ (Relational Schema Mapping)

### A. Thực thể: SUBSCRIPTION_TIER (Gói dịch vụ)
* **Khóa chính (PK):** `tier_id`
* **Thuộc tính:**
  * `tier_id` (INT, Auto Increment): Mã gói cước dịch vụ
  * `tier_name` (VARCHAR(50), Unique, Not Null): Tên gói (VD: Basic, Standard, Premium)
  * `price` (DECIMAL(10, 2), Not Null): Giá cước hàng tháng
  * `max_screens` (INT, Not Null): Số thiết bị phát đồng thời tối đa
  * `resolution` (VARCHAR(20), Not Null): Độ phân giải tối đa (VD: HD, Full HD, 4K)

### B. Thực thể: USER_ACCOUNT (Tài khoản người dùng)
* **Khóa chính (PK):** `account_id`
* **Khóa ứng viên (CK):** `email`
* **Khóa ngoại (FK):** `tier_id` -> `SUBSCRIPTION_TIER(tier_id)`
* **Thuộc tính:**
  * `account_id` (INT, Auto Increment): Mã tài khoản hệ thống
  * `email` (VARCHAR(255), Unique, Not Null): Email đăng nhập
  * `password_hash` (VARCHAR(255), Not Null): Mật khẩu đã mã hóa
  * `tier_id` (INT, Nullable): Mã gói cước đăng ký hiện tại
  * `status` (VARCHAR(20), Default 'ACTIVE'): Trạng thái tài khoản (ACTIVE, INACTIVE, SUSPENDED)
  * `created_at` (TIMESTAMP, Default Current Timestamp): Ngày giờ tạo tài khoản

### C. Thực thể: USER_PROFILE (Hồ sơ xem phim)
* **Khóa chính (PK):** `profile_id`
* **Khóa ngoại (FK):** `account_id` -> `USER_ACCOUNT(account_id)`
* **Thuộc tính:**
  * `profile_id` (INT, Auto Increment): Mã hồ sơ xem phim
  * `account_id` (INT, Not Null): Mã tài khoản sở hữu
  * `profile_name` (VARCHAR(100), Not Null): Tên hiển thị của hồ sơ
  * `avatar_url` (VARCHAR(500), Nullable): Đường dẫn ảnh đại diện
  * `is_child` (BOOLEAN, Default False): Đánh dấu hồ sơ dành cho trẻ em
  * `created_at` (TIMESTAMP, Default Current Timestamp): Ngày giờ tạo hồ sơ

---

## 2. Định nghĩa Khóa ngoại và Toàn vẹn tham chiếu (Referential Integrity Definition)

| Bảng nguồn | Cột khóa ngoại (FK) | Bảng đích tham chiếu | Cột khóa chính (PK) | ON DELETE | ON UPDATE | Ý nghĩa nghiệp vụ / Ràng buộc |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `USER_ACCOUNT` | `tier_id` | `SUBSCRIPTION_TIER` | `tier_id` | `SET NULL` | `CASCADE` | Khi một gói cước bị xóa khỏi hệ thống, thuộc tính `tier_id` của tài khoản người dùng sẽ chuyển về `NULL` để người dùng đăng ký gói mới mà không mất tài khoản. |
| `USER_PROFILE` | `account_id` | `USER_ACCOUNT` | `account_id` | `CASCADE` | `CASCADE` | Hồ sơ xem phim là thực thể yếu, phụ thuộc hoàn toàn vào tài khoản. Khi xóa tài khoản người dùng, toàn bộ hồ sơ xem phim con tự động bị xóa theo. |

---

## 3. Chứng minh Dạng chuẩn (Normalization Proofs)

### A. Bảng `SUBSCRIPTION_TIER`
* **Khóa chính (PK):** `tier_id`
* **Khóa ứng viên (CK):** `tier_name`
* **Tập phụ thuộc hàm (FDs):**
  * **FD1:** `tier_id` -> {`tier_name`, `price`, `max_screens`, `resolution`}
  * **FD2:** `tier_name` -> {`tier_id`, `price`, `max_screens`, `resolution`}
* **Chứng minh:**
  * **1NF:** Mọi thuộc tính đều mang giá trị đơn nguyên (Atomic).
  * **2NF:** Đạt 1NF và Khóa chính là thuộc tính đơn (`tier_id`), không tồn tại phụ thuộc hàm một phần.
  * **3NF:** Đạt 2NF và các thuộc tính không khóa không phụ thuộc bắc cầu vào khóa chính.
  * **BCNF:** Với mọi phụ thuộc hàm X -> Y (FD1, FD2), vế trái X (`tier_id`, `tier_name`) luôn là Siêu khóa (Super Key).
* **Kết luận:** Bảng đạt dạng chuẩn **BCNF**.

### B. Bảng `USER_ACCOUNT`
* **Khóa chính (PK):** `account_id`
* **Khóa ứng viên (CK):** `email`
* **Tập phụ thuộc hàm (FDs):**
  * **FD1:** `account_id` -> {`email`, `password_hash`, `tier_id`, `status`, `created_at`}
  * **FD2:** `email` -> {`account_id`, `password_hash`, `tier_id`, `status`, `created_at`}
* **Chứng minh:**
  * **1NF:** Mọi ô dữ liệu đều chứa một giá trị nguyên tố.
  * **2NF:** Đạt 1NF và có Khóa chính đơn (`account_id`), tất cả thuộc tính không khóa phụ thuộc đầy đủ vào khóa.
  * **3NF:** Đạt 2NF và không có phụ thuộc bắc cầu giữa các thuộc tính không khóa.
  * **BCNF:** Vế trái của mọi phụ thuộc hàm (`account_id`, `email`) đều là Siêu khóa.
* **Kết luận:** Bảng đạt dạng chuẩn **BCNF**.

### C. Bảng `USER_PROFILE`
* **Khóa chính (PK):** `profile_id`
* **Tập phụ thuộc hàm (FDs):**
  * **FD1:** `profile_id` -> {`account_id`, `profile_name`, `avatar_url`, `is_child`, `created_at`}
* **Chứng minh:**
  * **1NF:** Tất cả các thuộc tính đều chứa giá trị nguyên tố đơn lẻ.
  * **2NF:** Đạt 1NF và Khóa chính đơn (`profile_id`), không có phụ thuộc một phần.
  * **3NF:** Đạt 2NF và các thuộc tính không khóa chỉ phụ thuộc trực tiếp vào `profile_id`.
  * **BCNF:** Phụ thuộc hàm duy nhất FD1 có vế trái `profile_id` là Siêu khóa.
* **Kết luận:** Bảng đạt dạng chuẩn **BCNF**.
