 CHỦ ĐỀ 2: BẢNG THUẬT NGỮ VÀ ĐỊNH NGHĨA THỰC THỂ CỐT LÕI (GLOSSARY)
(Cập nhật theo chuẩn cấu trúc dữ liệu mindmap)

---

 NHÓM 1: THỰC THỂ NGƯỜI DÙNG & TÀI KHOẢN (USER ENTITIES)

- GUESTS (KHÁCH TRUY CẬP)
  + Ý nghĩa: Những người truy cập vào nền tảng nhưng chưa đăng ký hoặc chưa đăng nhập. Nhóm này bị hạn chế quyền hạn (chỉ xem được trang chủ hoặc giới thiệu).
- USER (NGƯỜI DÙNG ĐÃ ĐĂNG KÝ)
  + Ý nghĩa: Khách hàng đã tạo tài khoản thành công trên hệ thống. 
  + Đặc điểm nhận diện: Quản lý bằng các trường dữ liệu định danh như `UserID` (Mã định danh duy nhất) và `Username` (Tên đăng nhập).
- SUBSCRIPTION PLAN (GÓI CƯỚC)
  + Ý nghĩa: Gói dịch vụ trả phí mà User đăng ký, quyết định quyền lợi và giới hạn của tài khoản đó.
- PROFILES (HỒ SƠ NGƯỜI XEM)
  + Ý nghĩa: Tài khoản phụ nằm trong một User chính, giúp cá nhân hóa trải nghiệm cho nhiều người dùng chung một tài khoản (VD: các thành viên trong gia đình).
  + Đặc điểm nhận diện: Quản lý qua `ID` (Mã hồ sơ) và `Name` (Tên hồ sơ).
- PARENTAL CONTROL (KIỂM SOÁT TRẺ EM)
  + Ý nghĩa: Tính năng gắn liền với từng Profile, cho phép thiết lập giới hạn độ tuổi để lọc bỏ các nội dung không phù hợp với trẻ em.

---

 NHÓM 2: THỰC THỂ NỘI DUNG (CONTENT ENTITIES)

- CONTENT (NỘI DUNG/TÁC PHẨM)
  + Ý nghĩa: Thực thể gốc đại diện cho mọi video có trên nền tảng. Được định danh bằng `ContentID`.
- TYPE (PHÂN LOẠI NỘI DUNG)
  + Ý nghĩa: Nhóm phân loại hình thức của Content. Dựa trên cấu trúc hệ thống, Content được chia thành 4 loại chính:
    + Movies: Phim lẻ (chỉ có 1 tập).
    + Documentaries: Phim tài liệu.
    + Anime Series: Phim hoạt hình dài tập.
    + TV Shows: Chương trình truyền hình / Phim bộ nhiều tập.

---

## NHÓM 3: SIÊU DỮ LIỆU NỘI DUNG (META-DATA)
*(Tập hợp các thuộc tính chi tiết dùng để mô tả một Content)*

- TITLE: Tên chính thức của tác phẩm.
- GENRE: Thể loại tác phẩm (Hành động, Hài hước, Kinh dị...).
- RELEASE YEAR: Năm tác phẩm được phát hành.
- DURATION: Thời lượng phát của tác phẩm (thường tính bằng phút, áp dụng cho Movies).
- DIRECTOR: Đạo diễn chỉ đạo tác phẩm.
- CASTS: Danh sách các diễn viên tham gia diễn xuất.
- LANGUAGE: Ngôn ngữ gốc và các tùy chọn ngôn ngữ (âm thanh/phụ đề) của tác phẩm.
- EPISODES: Danh sách các tập phim con (áp dụng riêng cho Anime Series và TV Shows).

---

 NHÓM 4: LƯU TRỮ TƯƠNG TÁC (USER ACTIVITY)

- HISTORY (LỊCH SỬ XEM)
  + Ý nghĩa: Nơi lưu trữ thông tin về các Content mà Profile đã xem hoặc đang xem dở dang.
- WATCHLIST (DANH SÁCH LƯU TRỮ)
  + Ý nghĩa: Danh sách các Content mà Profile chủ động thêm vào để theo dõi và xem trong tương lai.