USE mini_netflix;

-- =====================================================================
-- KIỂM CHỨNG HIỆU NĂNG TRUY VẤN VỚI EXPLAIN (PERFORMANCE TEST CASES < 200ms)
-- Khớp Mục 4.2B trong Báo cáo Dự án Nhóm G12
-- =====================================================================

-- Kịch bản 1: Kiểm tra chỉ mục idx_content_title (tìm kiếm theo tiền tố tiêu đề)
-- Kỳ vọng: type = range, key = idx_content_title
EXPLAIN
SELECT content_id, title, release_year, rating_age
FROM content
WHERE title LIKE 'Inception%';

-- Kịch bản 2: Kiểm tra chỉ mục idx_watch_history_last_watched (lấy lịch sử xem gần nhất theo profile_id)
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
