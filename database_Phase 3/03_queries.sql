USE mini_netflix;

-- =====================================================================
-- TRUY VẤN 1 (Multi-table JOIN): Danh mục Phim lẻ (MOVIE) chất lượng 4K
-- Ý nghĩa: Ghép 5 bảng để lấy danh sách phim lẻ 4K kèm ngôn ngữ gốc và thể loại
-- =====================================================================
SELECT
    c.content_id,
    c.title AS movie_title,
    c.release_year,
    c.rating_age,
    l.language_name AS original_language,
    m.duration_minutes,
    m.video_resolution,
    GROUP_CONCAT(g.genre_name ORDER BY g.genre_name SEPARATOR ', ') AS genres
FROM content AS c
INNER JOIN movie AS m ON c.content_id = m.content_id
INNER JOIN language AS l ON c.language_code = l.language_code
INNER JOIN content_genre AS cg ON c.content_id = cg.content_id
INNER JOIN genre AS g ON cg.genre_id = g.genre_id
WHERE m.video_resolution = '4K'
GROUP BY
    c.content_id,
    c.title,
    c.release_year,
    c.rating_age,
    l.language_name,
    m.duration_minutes,
    m.video_resolution
ORDER BY c.release_year DESC;

-- =====================================================================
-- TRUY VẤN 2 (Hierarchical 4-Table JOIN): Cấu trúc phân cấp Phim bộ (TV_SERIES)
-- Ý nghĩa: Truy xuất toàn bộ chuỗi kế thừa CONTENT -> TV_SERIES -> SEASON -> TV_EPISODE
-- =====================================================================
SELECT
    c.title AS series_title,
    tv.series_status,
    s.season_number,
    s.season_name,
    ep.episode_number,
    ep.episode_title,
    ep.duration_minutes
FROM content AS c
INNER JOIN tv_series AS tv ON c.content_id = tv.content_id
INNER JOIN season AS s ON tv.content_id = s.content_id
INNER JOIN tv_episode AS ep ON s.season_id = ep.season_id
ORDER BY c.title ASC, s.season_number ASC, ep.episode_number ASC;

-- =====================================================================
-- TRUY VẤN 3 (LEFT JOIN & Continuous Playback - BR-06, FR-05):
-- Ý nghĩa: Hiển thị danh sách "Tiếp tục xem (Continue Watching)" các nội dung đang
-- xem dở (is_completed = FALSE) của từng Profile, hiển thị cả Phim lẻ và Tập phim bộ
-- =====================================================================
SELECT
    p.profile_name,
    c.title AS content_title,
    c.content_type,
    COALESCE(CONCAT('Mùa ', s.season_number, ' - Tập ', ep.episode_number, ': ', ep.episode_title), 'Phim lẻ nguyên bản') AS current_episode_info,
    ROUND(wh.stopped_position_seconds / 60, 1) AS stopped_at_minute,
    wh.last_watched_timestamp
FROM watch_history AS wh
INNER JOIN profile AS p ON wh.profile_id = p.profile_id
INNER JOIN content AS c ON wh.content_id = c.content_id
LEFT JOIN tv_episode AS ep ON wh.episode_id = ep.episode_id
LEFT JOIN season AS s ON ep.season_id = s.season_id
WHERE wh.is_completed = FALSE
ORDER BY wh.last_watched_timestamp DESC;

-- =====================================================================
-- TRUY VẤN 4 (GROUP BY & Aggregation): Top 5 nội dung ăn khách nhất hệ thống
-- Ý nghĩa: Thống kê tổng lượt xem và số lượt xem hoàn tất của từng tựa phim
-- =====================================================================
SELECT
    c.content_id,
    c.title,
    c.content_type,
    c.rating_age,
    COUNT(wh.history_id) AS total_views,
    SUM(CASE WHEN wh.is_completed = TRUE THEN 1 ELSE 0 END) AS completed_views
FROM content AS c
INNER JOIN watch_history AS wh ON c.content_id = wh.content_id
GROUP BY c.content_id, c.title, c.content_type, c.rating_age
ORDER BY total_views DESC, completed_views DESC
LIMIT 5;

-- =====================================================================
-- TRUY VẤN 5 (GROUP BY & Revenue Analysis): Báo cáo doanh thu theo Gói cước
-- Ý nghĩa: Tính số tài khoản ACTIVE, tổng số Profile đang tạo và doanh thu hàng tháng
-- =====================================================================
SELECT
    st.tier_name,
    st.monthly_price,
    COUNT(DISTINCT ua.account_id) AS active_accounts,
    COUNT(p.profile_id) AS total_profiles_created,
    COUNT(DISTINCT ua.account_id) * st.monthly_price AS monthly_revenue_vnd
FROM subscription_tier AS st
LEFT JOIN user_account AS ua
    ON st.tier_id = ua.tier_id
    AND ua.account_status = 'ACTIVE'
LEFT JOIN profile AS p ON ua.account_id = p.account_id
GROUP BY st.tier_id, st.tier_name, st.monthly_price
ORDER BY monthly_revenue_vnd DESC;

-- =====================================================================
-- TRUY VẤN 6 (GROUP BY & Completion Rate): Tỷ lệ xem hoàn thành của từng Profile
-- Ý nghĩa: Tính tổng số phim đã xem, tổng số phút đã cày và tỷ lệ % xem hết phim
-- =====================================================================
SELECT
    ua.email AS account_email,
    p.profile_name,
    p.is_kids,
    COUNT(wh.history_id) AS total_titles_watched,
    ROUND(SUM(wh.stopped_position_seconds) / 60.0, 1) AS total_minutes_streamed,
    ROUND(AVG(CASE WHEN wh.is_completed = TRUE THEN 100.0 ELSE 0.0 END), 1) AS completion_rate_percent
FROM profile AS p
INNER JOIN user_account AS ua ON p.account_id = ua.account_id
INNER JOIN watch_history AS wh ON p.profile_id = wh.profile_id
GROUP BY ua.email, p.profile_id, p.profile_name, p.is_kids
ORDER BY total_minutes_streamed DESC;

-- =====================================================================
-- TRUY VẤN 7 (Correlated Subquery - NOT EXISTS): Phim nằm trong Watchlist nhưng chưa xem
-- Ý nghĩa: Tìm các bộ phim mà người dùng đã lưu vào Watchlist nhưng chưa từng bấm xem
-- để hệ thống gửi thông báo nhắc nhở
-- =====================================================================
SELECT
    p.profile_name,
    c.title AS unwatched_saved_title,
    c.content_type,
    w.added_at AS saved_to_watchlist_at
FROM watchlist AS w
INNER JOIN profile AS p ON w.profile_id = p.profile_id
INNER JOIN content AS c ON w.content_id = c.content_id
WHERE NOT EXISTS (
    SELECT 1
    FROM watch_history AS wh
    WHERE wh.profile_id = w.profile_id
      AND wh.content_id = w.content_id
)
ORDER BY w.added_at ASC;

-- =====================================================================
-- TRUY VẤN 8 (Scalar Subquery): Tìm các Phim lẻ có thời lượng dài hơn mức trung bình
-- Ý nghĩa: So sánh thời lượng của từng bộ phim lẻ với thời lượng trung bình toàn hệ thống
-- =====================================================================
SELECT
    c.title,
    c.release_year,
    m.duration_minutes,
    (SELECT ROUND(AVG(duration_minutes), 1) FROM movie) AS system_avg_duration
FROM content AS c
INNER JOIN movie AS m ON c.content_id = m.content_id
WHERE m.duration_minutes > (
    SELECT AVG(duration_minutes)
    FROM movie
)
ORDER BY m.duration_minutes DESC;

-- =====================================================================
-- TRUY VẤN 9 (Subquery & Genre Preference): Thống kê Thể loại được yêu thích nhất
-- Ý nghĩa: Đếm số lượng phim và tổng lượt xem thực tế theo từng Thể loại (GENRE)
-- =====================================================================
SELECT
    g.genre_name,
    COUNT(DISTINCT cg.content_id) AS total_catalog_titles,
    COUNT(wh.history_id) AS total_stream_views
FROM genre AS g
LEFT JOIN content_genre AS cg ON g.genre_id = cg.genre_id
LEFT JOIN watch_history AS wh ON cg.content_id = wh.content_id
GROUP BY g.genre_id, g.genre_name
HAVING COUNT(wh.history_id) > 0
ORDER BY total_stream_views DESC, total_catalog_titles DESC;

-- =====================================================================
-- TRUY VẤN 10 (Kids Safe Catalog Filter - BR-09): Danh mục phim an toàn cho Trẻ em
-- Ý nghĩa: Lọc tự động các bộ phim có nhãn độ tuổi phù hợp (G, PG, PG-13) cho hồ sơ Kids
-- =====================================================================
SELECT
    c.content_id,
    c.title,
    c.content_type,
    c.rating_age,
    l.language_name,
    GROUP_CONCAT(g.genre_name SEPARATOR ', ') AS genres
FROM content AS c
INNER JOIN language AS l ON c.language_code = l.language_code
INNER JOIN content_genre AS cg ON c.content_id = cg.content_id
INNER JOIN genre AS g ON cg.genre_id = g.genre_id
WHERE c.rating_age NOT IN ('R', 'NC-17')
GROUP BY c.content_id, c.title, c.content_type, c.rating_age, l.language_name
ORDER BY c.rating_age ASC, c.title ASC;