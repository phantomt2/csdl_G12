CHỦ ĐỀ 2: BẢNG THUẬT NGỮ VÀ ĐỊNH NGHĨA THỰC THỂ CỐT LÕI (SECTION 1.2 - GLOSSARY)

| Đối tượng | Tên bảng CSDL | Thực tế ngoài đời | Bản chất trong CSDL |
| :--- | :--- | :--- | :--- |
| **Khách vãng lai** | `CASUAL_VISITOR` *(Non-DB)* | Khách lướt xem giao diện khi chưa đăng nhập[cite: 1, 3]. | **Không lưu trong DB** (không cấp ID, không xem được phim)[cite: 1, 3]. |
| **Gói cước** | `SUBSCRIPTION_TIER` | Bảng giá dịch vụ (Basic, Standard, Premium)[cite: 1, 3]. | Bảng lưu giá tiền, số profile tối đa, số máy xem cùng lúc và chất lượng video[cite: 1, 3]. |
| **Tài khoản** | `ACCOUNT` | Nick đăng nhập của người đứng ra trả tiền[cite: 1, 3]. | Lưu email, mật khẩu băm, gói đang dùng; quản lý 1–5 profile con[cite: 1, 3]. |
| **Hồ sơ con** | `PROFILE` | Màn hình "Ai đang xem?" cho từng người trong nhà[cite: 1, 3]. | Thuộc về Account; lưu tên, avatar, mã PIN, cờ trẻ em; không lưu thẻ ngân hàng[cite: 1, 3]. |
| **Nội dung chung** | `CONTENT` | Mọi poster phim hiển thị trên trang chủ[cite: 1, 3]. | Bảng cha (Superclass) lưu thông tin chung: mã phim, tên, năm ra mắt, độ tuổi, tóm tắt[cite: 1, 3]. |
| **Phim lẻ** | `MOVIE` | Phim điện ảnh xem một mạch là hết (Titanic, Avatar)[cite: 1, 3]. | Bảng con của CONTENT; lưu thêm thời lượng (phút) và link video để phát[cite: 1, 3]. |
| **Phim bộ** | `TV_SERIES` | Dự án phim dài kỳ (Stranger Things, Squid Game)[cite: 1, 3]. | Gốc quản lý các Mùa phim; không gắn trực tiếp với file video[cite: 1, 3]. |
| **Mùa phim** | `SEASON` | Hộp chọn "Mùa 1", "Mùa 2" của phim bộ[cite: 1, 3]. | Thuộc về TV_SERIES; dùng để gom nhóm và đánh số thứ tự các tập[cite: 1, 3]. |
| **Tập phim** | `TV_EPISODE` | Từng tập cụ thể có nút Play để xem (Tập 1, Tập 2...)[cite: 1, 3]. | Bảng con của CONTENT, thuộc về SEASON; lưu số tập, thời lượng và link video[cite: 1, 3]. |
| **Thể loại** | `GENRE` | Mục lọc phim (Hành động, Hài, Kinh dị...)[cite: 1]. | Bảng danh mục; nối nhiều - nhiều (M:N) với CONTENT qua bảng phụ `CONTENT_GENRE`[cite: 1]. |
| **Nghệ sĩ** | `PERSON` | Tên đạo diễn, diễn viên đóng trong phim[cite: 1]. | Bảng danh mục; nối nhiều - nhiều (M:N) với CONTENT kèm vai trò và tên nhân vật[cite: 1]. |
| **Danh sách xem sau** | `WATCHLIST` | Nút dấu cộng (+) "Thêm vào danh sách của tôi"[cite: 1, 3]. | Bảng nối (M:N) giữa PROFILE và CONTENT; lưu ngày giờ bấm lưu[cite: 1, 3]. |
| **Lịch sử xem** | `WATCH_HISTORY` | Hàng phim "Tiếp tục xem"[cite: 1, 3]. | Bảng nối (M:N) giữa PROFILE và video; lưu mốc giây xem dở để tua tiếp[cite: 1, 3]. |
| **Phiên đang phát** | `STREAMING_SESSION` | Cơ chế chặn khi mở quá nhiều màn hình cùng lúc[cite: 1]. | Lưu thiết bị, giờ phát, trạng thái (Bật/Tắt) theo thời gian thực để đếm số máy đang xem[cite: 1]. |
