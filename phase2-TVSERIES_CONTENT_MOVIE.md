# PHÂN HỆ NỘI DUNG: THIẾT KẾ VÀ CHUẨN HÓA

---

## 1. ÁNH XẠ LƯỢC ĐỒ QUAN HỆ

mô hình kế thừa:
- Bảng cha `CONTENT` lưu các thuộc tính chung.
- Các bảng con `MOVIE` và `TV_SERIES` lưu các thuộc tính chuyên biệt.
- Khóa chính `content_id` của bảng cha được dùng làm khóa chính và khóa ngoại ở các bảng con.
- Ràng buộc toàn vẹn tham chiếu: Sử dụng `ON DELETE CASCADE` và `ON UPDATE CASCADE` để dữ liệu bảng con tự động đồng bộ theo bảng cha.

### Biểu diễn lược đồ quan hệ

- **`CONTENT`** (<u>`content_id`</u>, `title`, `description`, `release_year`, `rating_age`, `content_type`)
  - Khóa chính: `content_id`

- **`MOVIE`** (<u>*`content_id`*</u>, `duration_minutes`, `video_file_size_gb`, `video_resolution`)
  - Khóa chính: `content_id`
  - Khóa ngoại: `content_id` tham chiếu đến `CONTENT(content_id)`
  - Quy tắc: `ON DELETE CASCADE ON UPDATE CASCADE`

- **`TV_SERIES`** (<u>*`content_id`*</u>, `total_seasons`, `series_status`)
  - Khóa chính: `content_id`
  - Khóa ngoại: `content_id` tham chiếu đến `CONTENT(content_id)`
  - Quy tắc: `ON DELETE CASCADE ON UPDATE CASCADE`

---

## 2. TỪ ĐIỂN DỮ LIỆU CHUẨN ISO/IEC 11179

### Bảng `CONTENT`

| Attribute Name | Data Type | Key Type | Nullable? | Default Value | Constraints / Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `content_id` | INT | PK | NO | None | Mã định danh nội dung, số nguyên tự tăng. |
| `title` | VARCHAR(255) | | NO | None | Tiêu đề nội dung, không rỗng. |
| `description` | TEXT | | YES | NULL | Tóm tắt nội dung phim. |
| `release_year` | SMALLINT | | NO | None | Năm phát hành: `CHECK (release_year BETWEEN 1888 AND 2100)`. |
| `rating_age` | VARCHAR(10) | | NO | 'ALL' | Giới hạn độ tuổi: `CHECK (rating_age IN ('ALL', '7+', '13+', '16+', '18+'))`. |
| `content_type` | VARCHAR(20) | | NO | None | Phân loại hình thức: `CHECK (content_type IN ('MOVIE', 'TV_SERIES'))`. |

---

### Bảng `MOVIE`

| Attribute Name | Data Type | Key Type | Nullable? | Default Value | Constraints / Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `content_id` | INT | PK, FK | NO | None | Tham chiếu `CONTENT(content_id)`, `CASCADE`. |
| `duration_minutes` | INT | | NO | None | Thời lượng phát sóng tính bằng phút: `CHECK (duration_minutes > 0)`. |
| `video_file_size_gb`| DECIMAL(6,2) | | NO | None | Dung lượng lưu trữ tính bằng GB: `CHECK (video_file_size_gb > 0.00)`. |
| `video_resolution` | VARCHAR(10) | | NO | '1080p' | Độ phân giải chuẩn: `CHECK (video_resolution IN ('720p', '1080p', '2K', '4K', '8K'))`. |

---

### Bảng `TV_SERIES`

| Attribute Name | Data Type | Key Type | Nullable? | Default Value | Constraints / Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `content_id` | INT | PK, FK | NO | None | Tham chiếu `CONTENT(content_id)`, `CASCADE`. |
| `total_seasons` | INT | | NO | 1 | Số lượng mùa đã sản xuất: `CHECK (total_seasons >= 1)`. |
| `series_status` | VARCHAR(20) | | NO | 'Ongoing' | Trạng thái phát hành: `CHECK (series_status IN ('Ongoing', 'Completed', 'Cancelled'))`. |

---

## 3. CHỨNG MINH CHUẨN HÓA

### 1. Bảng `CONTENT`

#### Phụ thuộc hàm
Mỗi nội dung có một mã `content_id` duy nhất xác định mọi thông tin mô tả đi kèm. Các thuộc tính khác như tiêu đề hay năm phát hành có thể trùng lặp và không xác định được thuộc tính nào khác.

Quy ước tập thuộc tính $\Omega = \{C, T, D, Y, A, K\}$, tương ứng:
- $C$: `content_id`
- $T$: `title`
- $D$: `description`
- $Y$: `release_year`
- $A$: `rating_age`
- $K$: `content_type`

Biểu diễn trực quan:
```text
FD1: content_id -> { title, description, release_year, rating_age, content_type }
```

Công thức toán học:
$$F = \{\text{FD}_1\}$$
$$\text{FD}_1: C \rightarrow \{T, D, Y, A, K\}$$

#### Khóa chính
Bao đóng của $C$:
$$\{C\}^+ = \{C, T, D, Y, A, K\} = \Omega$$

Vì $\{C\}^+$ chứa toàn bộ thuộc tính và $C$ là thuộc tính đơn, khóa chính duy nhất của bảng là `content_id`.

#### Chứng minh các dạng chuẩn
- **1NF:** Tất cả các cột đều chứa giá trị nguyên tử, không có thuộc tính đa trị hoặc bảng lồng. Đạt 1NF.
- **2NF:** Đạt 1NF và khóa chính chỉ gồm một thuộc tính $C$. Không thể tồn tại phụ thuộc một phần vào khóa. Đạt 2NF.
- **3NF:** Đạt 2NF và phụ thuộc hàm duy nhất có vế xác định là siêu khóa $C$. Không tồn tại phụ thuộc bắc cầu giữa các thuộc tính ngoài khóa. Đạt 3NF.
- **BCNF:** Mọi phụ thuộc hàm không tầm thường đều có vế trái là siêu khóa $C$. Đạt BCNF.

---

### 2. Bảng `MOVIE`

#### Phụ thuộc hàm
Khi biết `content_id`, các thông số kỹ thuật gồm thời lượng, dung lượng và độ phân giải được xác định đơn trị. Các thông số này độc lập và không xác định lẫn nhau.

Quy ước tập thuộc tính $\Omega = \{C, M, S, R\}$:
- $C$: `content_id`
- $M$: `duration_minutes`
- $S$: `video_file_size_gb`
- $R$: `video_resolution`

Biểu diễn trực quan:
```text
FD2: content_id -> { duration_minutes, video_file_size_gb, video_resolution }
```

Công thức toán học:
$$F = \{\text{FD}_2\}$$
$$\text{FD}_2: C \rightarrow \{M, S, R\}$$

#### Khóa chính
Bao đóng của $C$:
$$\{C\}^+ = \{C, M, S, R\} = \Omega$$

Khóa chính duy nhất là `content_id`.

#### Chứng minh các dạng chuẩn
- **1NF:** Các giá trị thời lượng, dung lượng và độ phân giải đều là giá trị đơn nguyên tử. Đạt 1NF.
- **2NF:** Đạt 1NF và khóa chính là thuộc tính đơn $C$, loại trừ hoàn toàn phụ thuộc bộ phận. Đạt 2NF.
- **3NF:** Đạt 2NF và vế trái của $\text{FD}_2$ là siêu khóa $C$. Không có phụ thuộc bắc cầu. Đạt 3NF.
- **BCNF:** Phụ thuộc hàm duy nhất có vế trái là siêu khóa. Đạt BCNF.

---

### 3. Bảng `TV_SERIES`

#### Phụ thuộc hàm
Khi biết `content_id`, số mùa và tình trạng phát sóng được xác định đơn trị. Số mùa không quyết định tình trạng sản xuất và ngược lại.

Quy ước tập thuộc tính $\Omega = \{C, N, P\}$:
- $C$: `content_id`
- $N$: `total_seasons`
- $P$: `series_status`

Biểu diễn trực quan:
```text
FD3: content_id -> { total_seasons, series_status }
```

Công thức toán học:
$$F = \{\text{FD}_3\}$$
$$\text{FD}_3: C \rightarrow \{N, P\}$$

#### Khóa chính
Bao đóng của $C$:
$$\{C\}^+ = \{C, N, P\} = \Omega$$

Khóa chính duy nhất là `content_id`.

#### Chứng minh các dạng chuẩn
- **1NF:** Toàn bộ thuộc tính đều có miền giá trị nguyên tử. Đạt 1NF.
- **2NF:** Đạt 1NF và khóa chính là thuộc tính đơn $C$, không có phụ thuộc bộ phận. Đạt 2NF.
- **3NF:** Đạt 2NF và vế xác định của phụ thuộc hàm là siêu khóa $C$, không có phụ thuộc bắc cầu. Đạt 3NF.
- **BCNF:** Vế trái của phụ thuộc hàm là siêu khóa $C$. Đạt BCNF.
