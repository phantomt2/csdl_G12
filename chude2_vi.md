CHỦ ĐỀ 2: BẢNG THUẬT NGỮ VÀ ĐỊNH NGHĨA THỰC THỂ CỐT LÕI (SECTION 1.2 - GLOSSARY)

| Đối tượng | Tên bảng CSDL | Thực tế ngoài đời | Bản chất trong CSDL |
| :--- | :--- | :--- | :--- |
| **Khách vãng lai** | `CASUAL_VISITOR` *(Non-DB)* | Khách lướt xem giao diện khi chưa đăng nhập. | **Không lưu trong DB** (không cấp ID, không xem được phim). |
| **Gói cước** | `SUBSCRIPTION_TIER` | Bảng giá dịch vụ (Basic, Standard, Premium). | Bảng lưu giá tiền, số profile tối đa, số máy xem cùng lúc và chất lượng video. |
| **Tài khoản** | `ACCOUNT` | Nick đăng nhập của người đứng ra trả tiền. | Lưu email, mật khẩu băm, gói đang dùng; quản lý 1–5 profile con. |
| **Hồ sơ con** | `PROFILE` | Màn hình "Ai đang xem?" cho từng người trong nhà. | Thuộc về Account; lưu tên, avatar, mã PIN, cờ trẻ em; không lưu thẻ ngân hàng. |
| **Nội dung chung** | `CONTENT` | Mọi poster phim hiển thị trên trang chủ. | Bảng cha (Superclass) lưu thông tin chung: mã phim, tên, năm ra mắt, độ tuổi, tóm tắt. |
| **Phim lẻ** | `MOVIE` | Phim điện ảnh xem một mạch là hết (Titanic, Avatar). | Bảng con của CONTENT; lưu thêm thời lượng (phút) và link video để phát. |
| **Phim bộ** | `TV_SERIES` | Dự án phim dài kỳ (Stranger Things, Squid Game). | Gốc quản lý các Mùa phim; không gắn trực tiếp với file video. |
| **Mùa phim** | `SEASON` | Hộp chọn "Mùa 1", "Mùa 2" của phim bộ. | Thuộc về TV_SERIES; dùng để gom nhóm và đánh số thứ tự các tập. |
| **Tập phim** | `TV_EPISODE` | Từng tập cụ thể có nút Play để xem (Tập 1, Tập 2...). | Bảng con của CONTENT, thuộc về SEASON; lưu số tập, thời lượng và link video. |
| **Thể loại** | `GENRE` | Mục lọc phim (Hành động, Hài, Kinh dị...). | Bảng danh mục; nối nhiều - nhiều (M:N) với CONTENT qua bảng phụ `CONTENT_GENRE`. |
| **Nghệ sĩ** | `PERSON` | Tên đạo diễn, diễn viên đóng trong phim. | Bảng danh mục; nối nhiều - nhiều (M:N) với CONTENT kèm vai trò và tên nhân vật. |
| **Danh sách xem sau** | `WATCHLIST` | Nút dấu cộng (+) "Thêm vào danh sách của tôi". | Bảng nối (M:N) giữa PROFILE và CONTENT; lưu ngày giờ bấm lưu. |
| **Lịch sử xem** | `WATCH_HISTORY` | Hàng phim "Tiếp tục xem". | Bảng nối (M:N) giữa PROFILE và video; lưu mốc giây xem dở để tua tiếp. |
| **Phiên đang phát** | `STREAMING_SESSION` | Cơ chế chặn khi mở quá nhiều màn hình cùng lúc. | Lưu thiết bị, giờ phát, trạng thái (Bật/Tắt) theo thời gian thực để đếm số máy đang xem. |
