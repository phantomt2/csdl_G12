-- =====================================================================
-- FILE: 02_mock_data.sql
-- MÔ TẢ: Dữ liệu mẫu (Seed Data) phong phú cho Mini-Netflix
-- ĐÃ ĐỒNG BỘ 100% VỚI FILE 01_SCHEMA.SQL CỦA NHÓM G12
-- =====================================================================

USE mini_netflix;

-- Xóa dữ liệu cũ (nếu có) để chạy lại không bị lỗi trùng khóa
-- (Tắt kiểm tra khóa ngoại tạm thời để xóa)
SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE watch_history;
TRUNCATE TABLE watchlist;
TRUNCATE TABLE tv_episode;
TRUNCATE TABLE season;
TRUNCATE TABLE tv_series;
TRUNCATE TABLE movie;
TRUNCATE TABLE content_genre;
TRUNCATE TABLE content;
TRUNCATE TABLE profile;
TRUNCATE TABLE user_account;
TRUNCATE TABLE subscription_tier;
TRUNCATE TABLE genre;
TRUNCATE TABLE language;
SET FOREIGN_KEY_CHECKS = 1;

-- =====================================================================
-- 1. BẢNG PHỤ TRỢ: LANGUAGE & GENRE
-- =====================================================================
INSERT INTO language (language_code, language_name) VALUES
('en', 'Tiếng Anh'), 
('ja', 'Tiếng Nhật'), 
('ko', 'Tiếng Hàn'), 
('vi', 'Tiếng Việt'), 
('fr', 'Tiếng Pháp');

INSERT INTO genre (genre_id, genre_name) VALUES
(1, 'Hành động (Action)'), 
(2, 'Hài hước (Comedy)'), 
(3, 'Khoa học viễn tưởng (Sci-Fi)'),
(4, 'Kinh dị (Horror)'), 
(5, 'Hoạt hình (Animation)'), 
(6, 'Tâm lý (Drama)');

-- =====================================================================
-- 2. BẢNG SUBSCRIPTION_TIER
-- Lưu ý: resolution chỉ được là '1080p', '2K', '4K'
-- =====================================================================
INSERT INTO subscription_tier (tier_id, tier_name, monthly_price, max_profiles_allowed, max_concurrent_streams, resolution) VALUES
(1, 'Basic', 70000.00, 2, 1, '1080p'),
(2, 'Standard', 150000.00, 3, 2, '2K'),
(3, 'Premium', 260000.00, 4, 4, '4K');

-- =====================================================================
-- 3. BẢNG USER_ACCOUNT
-- Lưu ý: registration_date là kiểu DATE (YYYY-MM-DD)
-- =====================================================================
INSERT INTO user_account (account_id, email, password_hash, account_status, registration_date, tier_id) VALUES
-- Acc 1: Premium - Sẽ tạo sẵn 4 profiles để test lỗi Trigger BR-01
(1, 'premium_maxed@example.com', 'hash_123', 'ACTIVE', '2023-01-10', 3), 
-- Acc 2: Premium - Có trẻ em
(2, 'premium_kids@example.com', 'hash_123', 'ACTIVE', '2023-02-15', 3),
-- Acc 3: Standard - Bình thường
(3, 'standard_user@example.com', 'hash_123', 'ACTIVE', '2023-05-20', 2),
-- Acc 4: Basic - Bị khóa (Test chức năng từ chối đăng nhập)
(4, 'banned_user@example.com', 'hash_123', 'SUSPENDED', '2023-06-01', 1),
-- Acc 5: Basic - Mới đăng ký, chưa có profile nào
(5, 'newbie@example.com', 'hash_123', 'ACTIVE', '2023-11-01', 1);

-- =====================================================================
-- 4. BẢNG PROFILE
-- =====================================================================
INSERT INTO profile (profile_id, account_id, profile_name, avatar_url, is_kids) VALUES
-- Acc 1 (Premium maxed): Đã đạt giới hạn 4/4 (Bẫy test BR-01)
(1, 1, 'Bố', 'https://cdn.mininetflix.vn/avatars/dad.png', FALSE),
(2, 1, 'Mẹ', 'https://cdn.mininetflix.vn/avatars/mom.png', FALSE),
(3, 1, 'Anh Trai', 'https://cdn.mininetflix.vn/avatars/boy.png', FALSE),
(4, 1, 'Em Gái', 'https://cdn.mininetflix.vn/avatars/girl.png', TRUE), 
-- Acc 2 (Premium): Có 1 người lớn, 1 trẻ em
(5, 2, 'Khách', 'https://cdn.mininetflix.vn/avatars/guest.png', FALSE),
(6, 2, 'Bé Na', 'https://cdn.mininetflix.vn/avatars/kids_girl.png', TRUE),
-- Acc 3 (Standard)
(7, 3, 'Tôi', 'https://cdn.mininetflix.vn/avatars/user.png', FALSE),
(8, 3, 'Vợ', 'https://cdn.mininetflix.vn/avatars/user2.png', FALSE);

-- =====================================================================
-- 5. BẢNG CONTENT (Siêu lớp EER)
-- =====================================================================
INSERT INTO content (content_id, title, description, release_year, rating_age, content_type, language_code) VALUES
-- MOVIES
(1, 'Inception', 'Kẻ trộm giấc mơ chuyên nghiệp đánh cắp bí mật từ tiềm thức.', 2010, 'PG-13', 'MOVIE', 'en'),
(2, 'Doraemon: Nobita và Cuộc Phiêu Lưu Mới', 'Mèo máy đến từ tương lai giúp đỡ cậu bé hậu đậu.', 2023, 'G', 'MOVIE', 'ja'),
(3, 'Deadpool', 'Lính đánh thuê lắm mồm với khả năng hồi phục thần tốc.', 2016, 'R', 'MOVIE', 'en'),
(4, 'The Godfather', 'Bi kịch của gia đình mafia quyền lực nhất nước Mỹ.', 1972, 'R', 'MOVIE', 'en'),
(5, 'Oppenheimer', 'Cha đẻ của bom nguyên tử và sự dằn vặt tâm lý.', 2023, 'R', 'MOVIE', 'en'),
(6, 'Toy Story', 'Cuộc phiêu lưu của những món đồ chơi có sự sống.', 1995, 'G', 'MOVIE', 'en'),
(7, 'Kỳ Nghỉ Của Bố', 'Phim hài Việt Nam về chuyến đi dở khóc dở cười.', 2021, 'PG', 'MOVIE', 'vi'),
(11, 'Fifty Shades of Grey', 'Bộ phim tâm lý người lớn (Test nhãn NC-17).', 2015, 'NC-17', 'MOVIE', 'en'),
-- TV SERIES
(8, 'Stranger Things', 'Nhóm trẻ em đối mặt với thế lực siêu nhiên tại thị trấn Hawkins.', 2016, 'PG-13', 'TV_SERIES', 'en'),
(9, 'Squid Game', 'Trò chơi sinh tồn đẫm máu với giải thưởng khổng lồ.', 2021, 'R', 'TV_SERIES', 'ko'),
(10, 'Ánh Dương Rực Rỡ', 'Bộ phim truyền hình Việt Nam về tình cảm gia đình.', 2022, 'PG', 'TV_SERIES', 'vi');

-- =====================================================================
-- 6. BẢNG SUBCLASS EER: MOVIE & TV_SERIES
-- =====================================================================
INSERT INTO movie (content_id, duration_minutes, video_resolution) VALUES
(1, 148, '4K'),      -- Inception (4K)
(2, 105, '1080p'),   -- Doraemon
(3, 108, '4K'),      -- Deadpool (4K)
(4, 175, '1080p'),   -- The Godfather (Rất dài)
(5, 180, '4K'),      -- Oppenheimer (Rất dài, 4K)
(6, 81, '1080p'),    -- Toy Story (Ngắn)
(7, 95, '1080p'),    -- Kỳ nghỉ của bố
(11, 125, '2K');     -- Fifty Shades

INSERT INTO tv_series (content_id, total_seasons, series_status) VALUES
(8, 4, 'ONGOING'),   -- Stranger Things
(9, 2, 'COMPLETED'), -- Squid Game
(10, 1, 'COMPLETED');-- Ánh Dương

-- Seasons cho Stranger Things (ID 8)
INSERT INTO season (season_id, content_id, season_number, season_name, release_date) VALUES
(1, 8, 1, 'Mùa 1: Cánh Cổng Mở Ra', '2016-07-15'),
(2, 8, 2, 'Mùa 2: Thế Giới Lộn Ngược', '2017-10-27');

-- Episodes cho Stranger Things Mùa 1
INSERT INTO tv_episode (episode_id, season_id, episode_number, episode_title, duration_minutes) VALUES
(1, 1, 1, 'Will Byers Biến Mất', 48),
(2, 1, 2, 'Cô Bé Kỳ Lạ Trên Đường Phố', 55),
(3, 1, 3, 'Đêm Giáng Sinh', 52);

-- Episodes cho Stranger Things Mùa 2
INSERT INTO tv_episode (episode_id, season_id, episode_number, episode_title, duration_minutes) VALUES
(4, 2, 1, 'Madmax', 48),
(5, 2, 2, 'Những Kẻ Bí Ẩn', 56);

-- Seasons cho Squid Game (ID 9)
INSERT INTO season (season_id, content_id, season_number, season_name, release_date) VALUES
(3, 9, 1, 'Mùa 1', '2021-09-17'),
(4, 9, 2, 'Mùa 2', '2024-12-26');

INSERT INTO tv_episode (episode_id, season_id, episode_number, episode_title, duration_minutes) VALUES
(6, 3, 1, 'Đèn Đỏ, Đèn Xanh', 60),
(7, 3, 2, 'Địa Ngục', 63),
(8, 4, 1, 'Cuộc Chơi Mới', 65);

-- =====================================================================
-- 7. BẢNG TRUNG GIAN: CONTENT_GENRE
-- =====================================================================
INSERT INTO content_genre (content_id, genre_id) VALUES
(1, 3), (1, 1), -- Inception: Sci-Fi, Action
(2, 5), (2, 2), -- Doraemon: Animation, Comedy
(3, 1), (3, 2), -- Deadpool: Action, Comedy
(4, 6), (4, 1), -- Godfather: Drama, Action
(5, 6),         -- Oppenheimer: Drama
(6, 5), (6, 2), -- Toy Story: Animation, Comedy
(7, 2),         -- Kỳ nghỉ bố: Comedy
(8, 3), (8, 4), -- Stranger Things: Sci-Fi, Horror
(9, 1), (9, 6), -- Squid Game: Action, Drama
(10, 6),        -- Ánh Dương: Drama
(11, 6);        -- Fifty Shades: Drama

-- =====================================================================
-- 8. BẢNG WATCH_HISTORY (Lịch sử xem)
-- =====================================================================
INSERT INTO watch_history (profile_id, content_id, episode_id, last_watched_timestamp, stopped_position_seconds, is_completed) VALUES
-- Profile 5 (Khách) xem Inception được 1 tiếng rồi tắt
(5, 1, NULL, '2023-11-01 20:00:00', 3600, FALSE),
-- Profile 5 (Khách) xem Stranger Things Mùa 1 Tập 1, xem xong
(5, 8, 1, '2023-11-02 21:00:00', 2880, TRUE), 
-- Profile 5 (Khách) đang xem dở Stranger Things Mùa 1 Tập 2
(5, 8, 2, '2023-11-03 22:00:00', 1200, FALSE),
-- Profile 7 (Tôi) xem Squid Game Mùa 1 Tập 1 xong
(7, 9, 6, '2023-11-05 18:00:00', 3600, TRUE),
-- Profile 6 (Bé Na - Trẻ em) xem Doraemon (Hợp lệ, nhãn G)
(6, 2, NULL, '2023-11-04 09:00:00', 1500, FALSE),
-- Profile 6 (Bé Na) xem Toy Story
(6, 6, NULL, '2023-11-04 15:00:00', 4860, TRUE);

-- =====================================================================
-- 9. BẢNG WATCHLIST (Danh sách xem sau)
-- =====================================================================
INSERT INTO watchlist (profile_id, content_id, added_at) VALUES
(5, 5, '2023-11-01 19:00:00'), -- Khách lưu Oppenheimer
(5, 3, '2023-11-02 20:00:00'), -- Khách lưu Deadpool
(7, 4, '2023-11-05 17:00:00'), -- Tôi lưu The Godfather
(6, 10, '2023-11-04 10:00:00'),-- Bé Na lưu Ánh Dương
(7, 1, '2023-11-05 12:00:00'); -- Tôi lưu Inception
