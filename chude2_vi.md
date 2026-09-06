# CHỦ ĐỀ 2: BẢNG THUẬT NGỮ VÀ ĐỊNH NGHĨA THỰC THỂ CỐT LÕI (GLOSSARY)

---

## NHÓM 1: NGƯỜI DÙNG VÀ TRUY CẬP (USER & ACCESS)
*(Từ lúc người dùng mở web, đăng nhập và chọn người xem)*

*   **ACCOUNT (TÀI KHOẢN)**
    *   **Ý nghĩa thực tế:** Đại diện cho một khách hàng đã đăng ký dịch vụ của nền tảng. Chứa các thông tin thanh toán, email, mật khẩu và quản lý gói cước (Subscription).
    
*   **PROFILE (HỒ SƠ NGƯỜI DÙNG)**
    *   **Ý nghĩa thực tế:** Không gian trải nghiệm cá nhân hóa của từng người xem bên trong một Tài khoản. Mỗi Profile có tên, avatar, danh sách phim (Watchlist) và lịch sử xem riêng biệt.
    *   **Phân biệt Account và Profile:** 1 Account có thể tạo ra nhiều Profile (Ví dụ: 1 tài khoản gia đình có Profile cho Bố, Mẹ, Con cái). **Account** quản lý "Tiền bạc và Quyền truy cập", trong khi **Profile** quản lý "Sở thích và Trải nghiệm xem".

*   **SUBSCRIPTION PLAN (GÓI ĐĂNG KÝ / GÓI CƯỚC)**
    *   **Ý nghĩa thực tế:** Mức dịch vụ mà Account đang trả phí (VD: Basic, Standard, Premium). Nó quyết định độ phân giải video tối đa và số lượng thiết bị được xem cùng lúc.

---

## NHÓM 2: NỘI DUNG (CONTENT)
*(Sau khi chọn Profile, người dùng sẽ lướt xem các danh mục nội dung có sẵn trên hệ thống)*

*   **TITLE / CONTENT (TÁC PHẨM / NỘI DUNG)**
    *   **Ý nghĩa thực tế:** Thuật ngữ chung để chỉ bất kỳ một sản phẩm video nào có trên hệ thống (bao gồm cả phim lẻ, phim bộ, phim tài liệu).

*   **MOVIE (PHIM LẺ)**
    *   **Ý nghĩa thực tế:** Tác phẩm điện ảnh hoàn chỉnh chỉ có một tập duy nhất (thời lượng thường từ 1-3 tiếng).

*   **TV SHOW / SERIES (PHIM BỘ / CHƯƠNG TRÌNH TRUYỀN HÌNH)**
    *   **Ý nghĩa thực tế:** Tác phẩm được chia thành nhiều phần, chiếu theo nhiều giai đoạn khác nhau.
    *   **Phân biệt Movie và Series:** Movie lưu trữ 1 video duy nhất. Series là một thực thể cha, bên trong chứa nhiều Season (Mùa), bên trong Season lại chứa nhiều Episode (Tập).

*   **SEASON (MÙA PHIM)**
    *   **Ý nghĩa thực tế:** Tập hợp các tập phim (Episodes) được phát hành trong cùng một khoảng thời gian của một TV Show/Series. 

*   **EPISODE (TẬP PHIM)**
    *   **Ý nghĩa thực tế:** Một phần video cụ thể nằm trong một Season của một TV Show. Tập phim có thời lượng, tiêu đề con và tóm tắt riêng.

*   **GENRE (THỂ LOẠI)**
    *   **Ý nghĩa thực tế:** Phân loại nội dung phim (Hành động, Hài, Lãng mạn, Kinh dị...) giúp hệ thống phân luồng hiển thị và người dùng dễ dàng tìm kiếm.

---

## NHÓM 3: TƯƠNG TÁC VÀ TRẢI NGHIỆM XEM (INTERACTION & STREAMING)
*(Khi người dùng bắt đầu chọn phim, lưu trữ hoặc nhấn nút "Play")*

*   **WATCHLIST (DANH SÁCH PHIM MUỐN XEM)**
    *   **Ý nghĩa thực tế:** Danh sách cá nhân của từng Profile, dùng để lưu lại các bộ phim hoặc chương trình mà họ có ý định sẽ xem trong tương lai.

*   **VIEWING HISTORY (LỊCH SỬ XEM)**
    *   **Ý nghĩa thực tế:** Bản ghi lại quá trình xem phim của Profile. Chứa thông tin về phim đã xem, thời gian xem, và "tiến độ xem" (đang xem đến phút thứ bao nhiêu).
    *   **Phân biệt Watchlist và Viewing History:** Watchlist do người dùng **chủ động** thêm vào (phim chưa xem hoặc muốn xem lại). Viewing History do hệ thống **tự động** ghi nhận khi người dùng nhấn "Play" (dùng cho tính năng "Tiếp tục xem - Continue Watching").

*   **RECOMMENDATION (HỆ THỐNG ĐỀ XUẤT)**
    *   **Ý nghĩa thực tế:** Thuật toán tính toán dựa trên Lịch sử xem (Viewing History) để hiển thị các bộ phim có cùng Thể loại (Genre) mà người dùng có khả năng sẽ thích.

*   **STREAM (PHIÊN PHÁT VIDEO)**
    *   **Ý nghĩa thực tế:** Hành động thực tế khi người dùng đang xem phim. Quản lý việc truyền tải dữ liệu, bao gồm Độ phân giải (Resolution), Phụ đề (Subtitle) và Âm thanh (Audio track) đang được chọn.