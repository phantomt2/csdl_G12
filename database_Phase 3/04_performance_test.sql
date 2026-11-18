USE mini_netflix;

-- =====================================================================
-- KIỂM CHỨNG HIỆU NĂNG TRUY VẤN & CHỈ MỤC B-TREE (PERFORMANCE TEST CASES < 200ms)
-- Khớp Mục 4.2B (Bản mở rộng) trong Báo cáo Dự án Nhóm G12
-- Gồm:
--   - 2 câu EXPLAIN chuẩn ban đầu (tìm theo tiền tố tiêu đề & lịch sử gần nhất)
--   - Phần 1: 5 cặp đối chiếu Before (IGNORE INDEX) vs. After (Có Index) với EXPLAIN ANALYZE
--   - Phần 2: 3 kịch bản biên (Edge Cases) kiểm tra giới hạn B-Tree Index
-- =====================================================================

-- [Cơ bản 1] Kiểm tra chỉ mục idx_content_title (tìm kiếm theo tiền tố tiêu đề)
-- Kỳ vọng: type = range, key = idx_content_title
EXPLAIN
SELECT content_id, title, release_year, rating_age
FROM content
WHERE title LIKE 'Inception%';

-- [Cơ bản 2] Kiểm tra chỉ mục idx_watch_history_last_watched (lấy lịch sử xem gần nhất theo profile_id)
-- Kỳ vọng: type = ref, key = idx_watch_history_last_watched
EXPLAIN
SELECT
    history_id,
    profile_id,
    content_id,
    episode_id,
    last_watched_timestamp,
    stopped_position_seconds,
    is_completed
FROM watch_history
WHERE profile_id = 1
ORDER BY last_watched_timestamp DESC;


-- =====================================================================
-- PHẦN 1: SO SÁNH BEFORE (IGNORE INDEX) vs. AFTER (CÓ B-TREE INDEX)
-- Kỹ thuật IGNORE INDEX ép Full Table Scan mà không phải xóa Index vật lý
-- =====================================================================

-- 1A / 1B. Chỉ mục idx_content_title (Tìm kiếm theo tiền tố 'Inception%')
EXPLAIN ANALYZE
SELECT content_id, title, release_year, rating_age
FROM content IGNORE INDEX (idx_content_title)
WHERE title LIKE 'Inception%';

EXPLAIN ANALYZE
SELECT content_id, title, release_year, rating_age
FROM content
WHERE title LIKE 'Inception%';

-- 2A / 2B. Chỉ mục idx_content_type_year (Lọc danh mục Phim lẻ từ năm 2020)
EXPLAIN ANALYZE
SELECT content_id, title, release_year
FROM content IGNORE INDEX (idx_content_type_year)
WHERE content_type = 'MOVIE' AND release_year >= 2020;

EXPLAIN ANALYZE
SELECT content_id, title, release_year
FROM content
WHERE content_type = 'MOVIE' AND release_year >= 2020;

-- 3A / 3B. Chỉ mục idx_content_rating (Lọc theo nhãn độ tuổi hẹp 'G')
EXPLAIN ANALYZE
SELECT content_id, title, rating_age
FROM content IGNORE INDEX (idx_content_rating)
WHERE rating_age = 'G';

EXPLAIN ANALYZE
SELECT content_id, title, rating_age
FROM content
WHERE rating_age = 'G';

-- 4A / 4B. Chỉ mục idx_watch_history_last_watched (Continue Watching theo profile_id)
EXPLAIN ANALYZE
SELECT history_id, profile_id, content_id, episode_id, last_watched_timestamp
FROM watch_history IGNORE INDEX (idx_watch_history_last_watched, uq_watch_history_profile_content_ep)
WHERE profile_id = 1
ORDER BY last_watched_timestamp DESC;

EXPLAIN ANALYZE
SELECT history_id, profile_id, content_id, episode_id, last_watched_timestamp
FROM watch_history
WHERE profile_id = 1
ORDER BY last_watched_timestamp DESC;

-- 5A / 5B. Chỉ mục uq_user_account_email (Tra cứu đăng nhập / Kiểm tra trùng Email)
EXPLAIN ANALYZE
SELECT account_id, email, account_status
FROM user_account IGNORE INDEX (uq_user_account_email)
WHERE email = 'an.nguyen@gmail.com';

EXPLAIN ANALYZE
SELECT account_id, email, account_status
FROM user_account
WHERE email = 'an.nguyen@gmail.com';


-- =====================================================================
-- PHẦN 2: CÁC KỊCH BẢN BIÊN / GIỚI HẠN CỦA B-TREE INDEX (EDGE CASES)
-- =====================================================================

-- [EDGE-01] Lọc độc lập theo release_year (không truyền content_type):
-- Vi phạm quy tắc tiền tố trái (Leftmost Prefix) của idx_content_type_year -> type = ALL
EXPLAIN ANALYZE
SELECT content_id, title
FROM content
WHERE release_year = 2020;

-- [EDGE-02] Tìm kiếm chứa wildcard '%' ở đầu chuỗi (LIKE '%Inception%'):
-- Không nhảy nhánh B-Tree từ điển A-Z được -> Full Index Scan (type = index)
EXPLAIN ANALYZE
SELECT content_id, title
FROM content
WHERE title LIKE '%Inception%';

-- [EDGE-03] Lọc diện rộng cho hồ sơ Trẻ em (NOT IN ('R', 'NC-17')):
-- Khớp >53% bảng nên Optimizer chủ động bỏ qua idx_content_rating -> type = ALL
EXPLAIN ANALYZE
SELECT content_id, title, rating_age
FROM content
WHERE rating_age NOT IN ('R', 'NC-17');
