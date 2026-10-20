USE mini_netflix;

-- =====================================================================
-- 1. NẠP DỮ LIỆU BẢNG SUBSCRIPTION_TIER (3 gói cước chuẩn)
-- =====================================================================
INSERT INTO subscription_tier (tier_id, tier_name, monthly_price, max_profiles_allowed, max_concurrent_streams, resolution)
VALUES
    (1, 'Basic', 70000.00, 1, 1, '1080p'),
    (2, 'Standard', 150000.00, 3, 2, '2K'),
    (3, 'Premium', 260000.00, 5, 4, '4K');

-- =====================================================================
-- 2. NẠP DỮ LIỆU BẢNG LANGUAGE (5 ngôn ngữ theo chuẩn ISO 639-1)
-- =====================================================================
INSERT INTO language (language_code, language_name)
VALUES
    ('vi', 'Tiếng Việt'),
    ('en', 'English'),
    ('ko', 'Korean'),
    ('ja', 'Japanese'),
    ('es', 'Spanish');

-- =====================================================================
-- 3. NẠP DỮ LIỆU BẢNG GENRE (6 thể loại phim)
-- =====================================================================
INSERT INTO genre (genre_id, genre_name)
VALUES
    (1, 'Hành động'),
    (2, 'Khoa học viễn tưởng'),
    (3, 'Tâm lý - Tình cảm'),
    (4, 'Hoạt hình'),
    (5, 'Kinh dị - Giật gân'),
    (6, 'Hài hước');

-- =====================================================================
-- 4. NẠP DỮ LIỆU BẢNG USER_ACCOUNT (5 tài khoản khách hàng)
-- =====================================================================
INSERT INTO user_account (account_id, email, password_hash, registration_date, account_status, tier_id)
VALUES
    (1, 'an.nguyen@gmail.com', '$2b$12$HashPassAnNguyen01', '2025-01-10', 'ACTIVE', 1),
    (2, 'binh.tran@gmail.com', '$2b$12$HashPassBinhTran02', '2025-02-15', 'ACTIVE', 2),
    (3, 'cuong.le@gmail.com', '$2b$12$HashPassCuongLe03', '2025-03-01', 'ACTIVE', 3),
    (4, 'dung.pham@gmail.com', '$2b$12$HashPassDungPham04', '2025-03-20', 'SUSPENDED', 2),
    (5, 'em.hoang@gmail.com', '$2b$12$HashPassEmHoang05', '2025-04-05', 'ACTIVE', 3);

-- =====================================================================
-- 5. NẠP DỮ LIỆU BẢNG PROFILE (9 hồ sơ cá nhân thuộc 5 tài khoản)
-- Lưu ý: account_id = 1 (Gói Basic) đã có 1 profile -> Đạt giới hạn tối đa!
-- =====================================================================
INSERT INTO profile (profile_id, account_id, profile_name, avatar_url, is_kids)
VALUES
    (1, 1, 'An Nguyễn', 'https://cdn.mininetflix.vn/avatars/u1_p1.png', FALSE),
    (2, 2, 'Bình Trần', 'https://cdn.mininetflix.vn/avatars/u2_p1.png', FALSE),
    (3, 2, 'Bé Bi', 'https://cdn.mininetflix.vn/avatars/kids_01.png', TRUE),
    (4, 3, 'Cường Lê', 'https://cdn.mininetflix.vn/avatars/u3_p1.png', FALSE),
    (5, 3, 'Minh Anh', 'https://cdn.mininetflix.vn/avatars/u3_p2.png', FALSE),
    (6, 3, 'Bé Bông', 'https://cdn.mininetflix.vn/avatars/kids_02.png', TRUE),
    (7, 4, 'Dũng Phạm', 'https://cdn.mininetflix.vn/avatars/u4_p1.png', FALSE),
    (8, 5, 'Hoàng Em', 'https://cdn.mininetflix.vn/avatars/u5_p1.png', FALSE),
    (9, 5, 'Gia Đình', 'https://cdn.mininetflix.vn/avatars/u5_p2.png', FALSE);

-- =====================================================================
-- 6. NẠP DỮ LIỆU SIÊU LỚP CONTENT (10 tác phẩm: 1-6 là MOVIE, 7-10 là TV_SERIES)
-- =====================================================================
INSERT INTO content (content_id, title, description, release_year, rating_age, content_type, language_code)
VALUES
    (1, 'Inception', 'Kẻ đánh cắp giấc mơ xâm nhập vào tiềm thức để cấy ghép ý tưởng.', 2010, 'PG-13', 'MOVIE', 'en'),
    (2, 'Mai', 'Câu chuyện tâm lý tình cảm sâu sắc về cuộc đời và tình yêu của Mai.', 2024, 'R', 'MOVIE', 'vi'),
    (3, 'Doraemon: Bản Giao Hưởng Địa Cầu', 'Chú mèo máy Doraemon cùng nhóm bạn giải cứu âm nhạc trên Trái Đất.', 2024, 'G', 'MOVIE', 'ja'),
    (4, 'Parasite', 'Sự phân hóa giàu nghèo qua câu chuyện hai gia đình tại Seoul.', 2019, 'R', 'MOVIE', 'ko'),
    (5, 'Interstellar', 'Hành trình xuyên hố đen vũ trụ tìm kiếm hành tinh mới cho nhân loại.', 2014, 'PG-13', 'MOVIE', 'en'),
    (6, 'Deadpool & Wolverine', 'Màn kết hợp hành động hài hước táo bạo của hai dị nhân Marvel.', 2024, 'R', 'MOVIE', 'en'),
    (7, 'Stranger Things', 'Những bí ẩn siêu nhiên kỳ lạ xảy ra tại thị trấn Hawkins.', 2016, 'PG-13', 'TV_SERIES', 'en'),
    (8, 'Squid Game', 'Trò chơi sinh tồn khắc nghiệt với giải thưởng 45,6 tỷ Won.', 2021, 'R', 'TV_SERIES', 'ko'),
    (9, 'Spy x Family', 'Gia đình điệp viên giả mạo đầy hài hước và ấm áp của bé Anya.', 2022, 'PG', 'TV_SERIES', 'ja'),
    (10, 'Money Heist', 'Phi vụ đột nhập xưởng in tiền Hoàng gia Tây Ban Nha của Giáo Sư.', 2017, 'R', 'TV_SERIES', 'es');

-- =====================================================================
-- 7. NẠP DỮ LIỆU BẢNG TRUNG GIAN CONTENT_GENRE (Gán đa thể loại cho phim)
-- =====================================================================
INSERT INTO content_genre (content_id, genre_id)
VALUES
    (1, 1), (1, 2),
    (2, 3),
    (3, 4), (3, 6),
    (4, 3), (4, 5),
    (5, 2), (5, 3),
    (6, 1), (6, 6),
    (7, 2), (7, 5),
    (8, 1), (8, 5),
    (9, 1), (9, 4), (9, 6),
    (10, 1), (10, 5);

-- =====================================================================
-- 8. NẠP DỮ LIỆU PHÂN LỚP MOVIE (Kế thừa từ CONTENT có content_id 1 -> 6)
-- =====================================================================
INSERT INTO movie (content_id, duration_minutes, video_resolution)
VALUES
    (1, 148, '4K'),
    (2, 131, '4K'),
    (3, 115, '1080p'),
    (4, 132, '4K'),
    (5, 169, '4K'),
    (6, 128, '4K');

-- =====================================================================
-- 9. NẠP DỮ LIỆU PHÂN LỚP TV_SERIES (Kế thừa từ CONTENT có content_id 7 -> 10)
-- =====================================================================
INSERT INTO tv_series (content_id, total_seasons, series_status)
VALUES
    (7, 4, 'ONGOING'),
    (8, 2, 'ONGOING'),
    (9, 2, 'ONGOING'),
    (10, 5, 'COMPLETED');

-- =====================================================================
-- 10. NẠP DỮ LIỆU BẢNG SEASON (Các mùa phim thuộc TV_SERIES)
-- =====================================================================
INSERT INTO season (season_id, content_id, season_number, season_name, release_date)
VALUES
    (1, 7, 1, 'Stranger Things Mùa 1', '2016-07-15'),
    (2, 7, 2, 'Stranger Things Mùa 2', '2017-10-27'),
    (3, 8, 1, 'Trò Chơi Con Mực Mùa 1', '2021-09-17'),
    (4, 8, 2, 'Trò Chơi Con Mực Mùa 2', '2024-12-26'),
    (5, 9, 1, 'Spy x Family Mùa 1', '2022-04-09'),
    (6, 10, 1, 'Phi Vụ Triệu Đô Phần 1', '2017-05-02');

-- =====================================================================
-- 11. NẠP DỮ LIỆU BẢNG TV_EPISODE (Các tập phim thuộc từng SEASON)
-- =====================================================================
INSERT INTO tv_episode (episode_id, season_id, episode_number, episode_title, duration_minutes)
VALUES
    (1, 1, 1, 'Chương Một: Sự biến mất của Will Byers', 49),
    (2, 1, 2, 'Chương Hai: Cô bé kỳ lạ ở đường Maple', 56),
    (3, 2, 1, 'Chương Một: MADMAX', 48),
    (4, 3, 1, 'Đèn Đỏ, Đèn Xanh', 60),
    (5, 3, 2, 'Địa Ngục', 63),
    (6, 4, 1, 'Bánh Mì và Vé Số', 61),
    (7, 5, 1, 'Chiến dịch Strix', 24),
    (8, 5, 2, 'Tìm kiếm một người vợ', 24),
    (9, 6, 1, 'Thực hiện theo thỏa thuận', 47),
    (10, 6, 2, 'Sự bất cẩn chết người', 41);

-- =====================================================================
-- 12. NẠP DỮ LIỆU BẢNG WATCHLIST (Danh sách lưu xem sau của các Profile)
-- =====================================================================
INSERT INTO watchlist (profile_id, content_id, added_at)
VALUES
    (1, 1, '2026-03-01 20:00:00'),
    (1, 5, '2026-03-02 21:15:00'),
    (1, 8, '2026-03-05 19:30:00'),
    (2, 2, '2026-03-10 22:00:00'),
    (2, 4, '2026-03-11 20:45:00'),
    (3, 3, '2026-03-12 16:00:00'),
    (3, 9, '2026-03-12 16:05:00'),
    (4, 6, '2026-03-15 23:10:00'),
    (5, 2, '2026-03-18 19:00:00'),
    (8, 10, '2026-03-20 21:00:00');

-- =====================================================================
-- 13. NẠP DỮ LIỆU BẢNG WATCH_HISTORY (Nhật ký & Tiến trình xem gần nhất)
-- Lưu ý: Phim lẻ (MOVIE) có episode_id = NULL; Phim bộ có episode_id cụ thể
-- =====================================================================
INSERT INTO watch_history (profile_id, content_id, episode_id, last_watched_timestamp, stopped_position_seconds, is_completed)
VALUES
    (1, 1, NULL, '2026-04-01 22:30:00', 8880, TRUE),
    (1, 7, 2, '2026-04-05 21:10:00', 1850, FALSE),
    (2, 2, NULL, '2026-04-02 20:00:00', 7860, TRUE),
    (2, 8, 4, '2026-04-06 23:15:00', 3600, TRUE),
    (3, 3, NULL, '2026-04-03 17:30:00', 6900, TRUE),
    (3, 9, 7, '2026-04-07 18:00:00', 720, FALSE),
    (4, 1, NULL, '2026-04-04 21:45:00', 4200, FALSE),
    (4, 6, NULL, '2026-04-08 22:50:00', 7680, TRUE),
    (5, 4, NULL, '2026-04-09 20:30:00', 7920, TRUE),
    (6, 3, NULL, '2026-04-10 15:20:00', 3000, FALSE),
    (8, 5, NULL, '2026-04-11 23:00:00', 10140, TRUE),
    (8, 8, 6, '2026-04-12 22:15:00', 2400, FALSE);