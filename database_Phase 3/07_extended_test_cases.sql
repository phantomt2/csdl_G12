USE mini_netflix;

-- =====================================================================
-- BỘ KỊCH BẢN KIỂM THỬ MỞ RỘNG (EXTENDED TEST CASES)
-- Nhóm G12 — Hệ thống Phim trực tuyến Mini-Netflix
-- Lưu ý:
--   1. Giữ nguyên file `06_negative_test_cases.sql` (TC-01..TC-05) để khớp Bảng 5.1 Báo cáo.
--   2. Khi chạy trên MySQL Workbench, có thể chạy từng khối; mọi lệnh thêm/xóa
--      đều bọc trong START TRANSACTION / ROLLBACK để giữ nguyên 86.895 dòng dữ liệu gốc.
--   3. Để chạy toàn bộ tự động & xuất kết quả PASS/FAIL, chạy:
--        python verify_database.py
-- =====================================================================


-- =====================================================================
-- PHẦN 1: KIỂM THỬ LUỒNG HỢP LỆ & CẬN BIÊN (POSITIVE & BOUNDARY CASES)
-- =====================================================================

-- [EXT-POS-01] BR-01 Cận biên gói Standard (max_profiles_allowed = 3):
-- Tài khoản 2 hiện có 2 profile -> Thêm profile thứ 3 PHẢI THÀNH CÔNG; thêm thứ 4 PHẢI BỊ TRIGGER CHẶN (1644).
START TRANSACTION;
INSERT INTO profile (account_id, profile_name, is_kids)
VALUES (2, 'Thành viên thứ 3 hợp lệ', FALSE);
-- Lệnh tiếp theo nếu chạy ngay lúc này sẽ kích hoạt lỗi 1644:
-- INSERT INTO profile (account_id, profile_name, is_kids) VALUES (2, 'Thành viên thứ 4 vượt mức', FALSE);
ROLLBACK;

-- [EXT-POS-02] BR-09 Hồ sơ trẻ em xem phim nhãn cho phép ('PG-13'):
-- Profile 3 ('Bé Bi', is_kids = TRUE) xem content_id = 5 ('Interstellar', 'PG-13') PHẢI THÀNH CÔNG.
START TRANSACTION;
INSERT INTO watch_history (profile_id, content_id, episode_id, stopped_position_seconds, is_completed)
VALUES (3, 5, NULL, 900, FALSE);
ROLLBACK;

-- [EXT-POS-03] BR-06 Lưu tiến trình nhiều tập khác nhau cho cùng một TV_SERIES:
-- Profile 1 đã có episode_id = 2 của Stranger Things (content_id = 7), nay xem thêm episode_id = 1 PHẢI THÀNH CÔNG.
START TRANSACTION;
INSERT INTO watch_history (profile_id, content_id, episode_id, stopped_position_seconds, is_completed)
VALUES (1, 7, 1, 600, FALSE);
ROLLBACK;

-- [EXT-POS-04] Cận biên hợp lệ của CHECK constraints (năm 1888, thời lượng 1 phút, vị trí dừng 0 giây):
START TRANSACTION;
INSERT INTO content (title, description, release_year, rating_age, content_type, language_code)
VALUES ('Roundhay Garden Scene (Boundary Test)', 'Boundary check year 1888', 1888, 'G', 'MOVIE', 'en');
SET @boundary_cid = LAST_INSERT_ID();
INSERT INTO movie (content_id, duration_minutes, video_resolution)
VALUES (@boundary_cid, 1, '1080p');
INSERT INTO watch_history (profile_id, content_id, episode_id, stopped_position_seconds, is_completed)
VALUES (1, @boundary_cid, NULL, 0, FALSE);
ROLLBACK;


-- =====================================================================
-- PHẦN 2: KIỂM THỬ MỞ RỘNG CHẶN DỮ LIỆU SAI (EXTENDED NEGATIVE TESTS)
-- Lưu ý: Chạy từng lệnh riêng lẻ để quan sát mã lỗi MySQL chặn lại.
-- =====================================================================

-- [EXT-NEG-01] UNIQUE Email tài khoản (uq_user_account_email) -> Kỳ vọng Error 1062:
INSERT INTO user_account (email, password_hash, tier_id)
VALUES ('an.nguyen@gmail.com', '$2b$12$DummyHash', 1);

-- [EXT-NEG-02] UNIQUE Tên hồ sơ trong cùng tài khoản (uq_profile_account_name) -> Kỳ vọng Error 1062:
-- (Dù tài khoản 2 gói Standard còn trống 1 slot nhưng vẫn không được đặt trùng tên 'Bình Trần')
INSERT INTO profile (account_id, profile_name, is_kids)
VALUES (2, 'Bình Trần', FALSE);

-- [EXT-NEG-03] UNIQUE Số tập trong cùng mùa (uq_episode_season_number) -> Kỳ vọng Error 1062:
INSERT INTO tv_episode (season_id, episode_number, episode_title, duration_minutes)
VALUES (1, 1, 'Tập 1 bị trùng', 45);

-- [EXT-NEG-04] Composite PK Watchlist không cho lưu trùng phim (pk_watchlist) -> Kỳ vọng Error 1062:
INSERT INTO watchlist (profile_id, content_id)
VALUES (1, 1);

-- [EXT-NEG-05] CHECK chk_account_status (chỉ nhận ACTIVE/SUSPENDED/CANCELED) -> Kỳ vọng Error 3819:
INSERT INTO user_account (email, password_hash, account_status, tier_id)
VALUES ('invalid.status@test.local', '$2b$12$DummyHash', 'BANNED', 1);

-- [EXT-NEG-06] CHECK chk_content_rating_age (theo chuẩn MPAA) -> Kỳ vọng Error 3819:
INSERT INTO content (title, release_year, rating_age, content_type, language_code)
VALUES ('Invalid Rating Film', 2024, '18+', 'MOVIE', 'en');

-- [EXT-NEG-07] CHECK chk_content_type (chỉ nhận MOVIE / TV_SERIES) -> Kỳ vọng Error 3819:
INSERT INTO content (title, release_year, rating_age, content_type, language_code)
VALUES ('Invalid Type Film', 2024, 'PG', 'ANIME', 'ja');

-- [EXT-NEG-08] CHECK chk_content_release_year (BETWEEN 1888 AND 2100) -> Kỳ vọng Error 3819:
INSERT INTO content (title, release_year, rating_age, content_type, language_code)
VALUES ('Too Old Film', 1800, 'G', 'MOVIE', 'en');

-- [EXT-NEG-09] CHECK chk_history_stopped_pos (>= 0 giây) -> Kỳ vọng Error 3819:
INSERT INTO watch_history (profile_id, content_id, episode_id, stopped_position_seconds, is_completed)
VALUES (1, 2, NULL, -10, FALSE);

-- [EXT-NEG-10] CHECK chk_tier_max_profiles (BETWEEN 1 AND 5) -> Kỳ vọng Error 3819:
INSERT INTO subscription_tier (tier_name, monthly_price, max_profiles_allowed, max_concurrent_streams, resolution)
VALUES ('Ultra 10 Profiles', 500000.00, 10, 4, '4K');

-- [EXT-NEG-11] FK ON DELETE RESTRICT cho Language & Genre -> Kỳ vọng Error 1451:
DELETE FROM language WHERE language_code = 'en';
DELETE FROM genre WHERE genre_id = 1;

-- [EXT-NEG-12] FK Ngăn chặn bản ghi mồ côi (account_id không tồn tại) -> Kỳ vọng Error 1452:
INSERT INTO profile (account_id, profile_name, is_kids)
VALUES (999999, 'Orphan Profile', FALSE);


-- =====================================================================
-- PHẦN 3: KIỂM THỬ TOÀN VẸN THAM CHIẾU ON DELETE CASCADE
-- =====================================================================

-- [EXT-CAS-01] Xóa USER_ACCOUNT tự động xóa lan truyền PROFILE, WATCHLIST, WATCH_HISTORY:
START TRANSACTION;
INSERT INTO user_account (email, password_hash, tier_id) VALUES ('cascade.user@test.local', '$2b$12$Hash', 2);
SET @cas_uid = LAST_INSERT_ID();
INSERT INTO profile (account_id, profile_name, is_kids) VALUES (@cas_uid, 'Cascade Profile', FALSE);
SET @cas_pid = LAST_INSERT_ID();
INSERT INTO watchlist (profile_id, content_id) VALUES (@cas_pid, 1);
INSERT INTO watch_history (profile_id, content_id, episode_id, stopped_position_seconds) VALUES (@cas_pid, 1, NULL, 120);
DELETE FROM user_account WHERE account_id = @cas_uid;
SELECT
    (SELECT COUNT(*) FROM profile WHERE profile_id = @cas_pid) AS remaining_profiles,
    (SELECT COUNT(*) FROM watchlist WHERE profile_id = @cas_pid) AS remaining_watchlist,
    (SELECT COUNT(*) FROM watch_history WHERE profile_id = @cas_pid) AS remaining_history;
ROLLBACK;

-- [EXT-CAS-02] Xóa CONTENT (TV_SERIES) tự động xóa TV_SERIES -> SEASON -> TV_EPISODE & CONTENT_GENRE:
START TRANSACTION;
INSERT INTO content (title, release_year, rating_age, content_type, language_code)
VALUES ('Cascade Test Series', 2025, 'PG', 'TV_SERIES', 'en');
SET @cas_cid = LAST_INSERT_ID();
INSERT INTO content_genre (content_id, genre_id) VALUES (@cas_cid, 1);
INSERT INTO tv_series (content_id, total_seasons, series_status) VALUES (@cas_cid, 1, 'ONGOING');
INSERT INTO season (content_id, season_number, season_name) VALUES (@cas_cid, 1, 'Mùa 1');
SET @cas_sid = LAST_INSERT_ID();
INSERT INTO tv_episode (season_id, episode_number, episode_title, duration_minutes) VALUES (@cas_sid, 1, 'Tập 1', 40);
SET @cas_eid = LAST_INSERT_ID();
DELETE FROM content WHERE content_id = @cas_cid;
SELECT
    (SELECT COUNT(*) FROM tv_series WHERE content_id = @cas_cid) AS remaining_series,
    (SELECT COUNT(*) FROM season WHERE season_id = @cas_sid) AS remaining_seasons,
    (SELECT COUNT(*) FROM tv_episode WHERE episode_id = @cas_eid) AS remaining_episodes,
    (SELECT COUNT(*) FROM content_genre WHERE content_id = @cas_cid) AS remaining_cg;
ROLLBACK;


-- =====================================================================
-- PHẦN 4: KIỂM TOÁN TOÀN VẸN MÔ HÌNH EER TRÊN TOÀN BỘ 8.817 TỰA PHIM
-- =====================================================================

-- [EXT-EER-01] Kiểm chứng Disjoint (MOVIE ∩ TV_SERIES = ∅) -> Kỳ vọng: 0
SELECT COUNT(*) AS eer_disjoint_violations
FROM movie AS m
INNER JOIN tv_series AS tv ON m.content_id = tv.content_id;

-- [EXT-EER-02] Kiểm chứng Total Completeness (Mọi CONTENT đều thuộc MOVIE hoặc TV_SERIES) -> Kỳ vọng: 0
SELECT COUNT(*) AS eer_orphan_contents
FROM content AS c
LEFT JOIN movie AS m ON c.content_id = m.content_id
LEFT JOIN tv_series AS tv ON c.content_id = tv.content_id
WHERE m.content_id IS NULL AND tv.content_id IS NULL;

-- [EXT-EER-03] Kiểm chứng nhất quán tập phim thuộc đúng series trong WATCH_HISTORY -> Kỳ vọng: 0
SELECT COUNT(*) AS episode_series_mismatches
FROM watch_history AS wh
INNER JOIN tv_episode AS ep ON wh.episode_id = ep.episode_id
INNER JOIN season AS s ON ep.season_id = s.season_id
WHERE wh.content_id <> s.content_id;


-- =====================================================================
-- PHẦN 5: KIỂM THỬ HIỆU NĂNG ĐẦY ĐỦ CHO CẢ 4 B-TREE INDEXES (EXPLAIN)
-- =====================================================================

-- Index 1: idx_content_title
EXPLAIN SELECT content_id, title, release_year, rating_age
FROM content
WHERE title LIKE 'Inception%';

-- Index 2: idx_watch_history_last_watched
EXPLAIN SELECT history_id, profile_id, content_id, episode_id, last_watched_timestamp
FROM watch_history
WHERE profile_id = 1
ORDER BY last_watched_timestamp DESC;

-- Index 3: idx_content_type_year
EXPLAIN SELECT content_id, title, release_year
FROM content
WHERE content_type = 'MOVIE' AND release_year >= 2020;

-- Index 4: idx_content_rating
EXPLAIN SELECT content_id, title, rating_age
FROM content
WHERE rating_age = 'G';


-- =====================================================================
-- PHẦN 6: KỊCH BẢN MINH HỌA KIỂM THỬ PHÂN QUYỀN RBAC (05_rbac_security.sql)
-- Chạy sau khi đã thực thi `05_rbac_security.sql`
-- =====================================================================
-- Tạo user test tạm, kiểm chứng MySQL Error 1142 rồi xóa user sau khi kiểm thử:
--   CREATE USER IF NOT EXISTS 'test_client'@'localhost' IDENTIFIED BY 'Test@12345';
--   GRANT 'role_streaming_client'@'%' TO 'test_client'@'localhost';
--   SET DEFAULT ROLE ALL TO 'test_client'@'localhost';
--   -- Khi đăng nhập bằng 'test_client':
--   --   SELECT COUNT(*) FROM mini_netflix.content;              -> THÀNH CÔNG
--   --   DELETE FROM mini_netflix.watch_history WHERE history_id = 1; -> BỊ CHẶN Error 1142 (REVOKE DELETE)
--   -- Dọn dẹp sau khi test:
--   DROP USER IF EXISTS 'test_client'@'localhost';
