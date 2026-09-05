1. Mô tả thế giới thu nhỏ (Miniworld)

Tổng quan hệ thống: Mini-Netflix là một nền tảng cung cấp dịch vụ xem phim trực tuyến theo yêu cầu. Hệ thống phục vụ các khách hàng đăng ký tài khoản dựa trên các gói thuê bao (Subscription Tiers) khác nhau (ví dụ: Cơ bản, Tiêu chuẩn, Cao cấp).

Quản lý Hồ sơ (User Profiles): Mỗi tài khoản đăng ký có thể tạo ra nhiều hồ sơ cá nhân (User Profiles) khác nhau cho các thành viên trong gia đình sử dụng riêng biệt.

Kho nội dung (Content): Hệ thống quản lý kho tàng nội dung giải trí được chia thành hai dạng chính: Phim lẻ (Movies) và Tập phim truyền hình (TV Series Episodes), kèm theo các thông tin phân loại thể loại, đạo diễn, diễn viên.

Lịch sử và Tương tác: Hệ thống ghi nhận lại lịch sử xem (Watch History), thời gian xem dở dang và danh sách theo dõi (Watchlist) của từng hồ sơ người dùng để phục vụ cho việc theo dõi tiến độ xem phim.

2. Danh mục Trong phạm vi (In-Scope)

Quản lý thông tin tài khoản người dùng và phân quyền các gói thuê bao (Subscription Tiers).

Quản lý danh sách các hồ sơ cá nhân (User Profiles) gắn với từng tài khoản.

Phân cấp và lưu trữ thông tin nội dung: Phim lẻ (Movie) và Tập phim (Episode) kế thừa từ thực thể chung là Nội dung (Content) theo mô hình phân cấp EER.

Quản lý mối quan hệ nhiều-nhiều (Many-to-Many) giữa Hồ sơ người dùng và Nội dung đối với tính năng Lịch sử xem (Watch History) và Danh sách yêu thích (Watchlist).

Quản lý thông tin chi tiết về thể loại phim, diễn viên và đạo diễn.

3. Danh mục Ngoài phạm vi (Out-of-Scope)

Tích hợp cổng thanh toán trực tuyến thực tế (như thẻ ngân hàng, Momo, Visa,... hệ thống chỉ lưu trữ trạng thái gói cước trong cơ sở dữ liệu).

Xây dựng hệ thống gợi ý phim thông minh (Recommendation System) dựa trên thuật toán AI/Machine Learning phức tạp.

Quản lý tệp phụ đề đa ngôn ngữ chi tiết (Subtitles) và hệ thống lưu trữ/truyền tải video thực tế (Video Streaming CDN).

Tính năng mạng xã hội như bình luận, đánh giá công khai hoặc nhắn tin giữa các người dùng với nhau.
