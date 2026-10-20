DROP DATABASE IF EXISTS mini_netflix;
CREATE DATABASE mini_netflix
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;
USE mini_netflix;

-- =====================================================================
-- BẢNG 1: SUBSCRIPTION_TIER
-- =====================================================================
CREATE TABLE subscription_tier (
    tier_id INT AUTO_INCREMENT,
    tier_name VARCHAR(50) NOT NULL,
    monthly_price DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    max_profiles_allowed INT NOT NULL DEFAULT 1,
    max_concurrent_streams INT NOT NULL DEFAULT 1,
    resolution VARCHAR(10) NOT NULL DEFAULT '1080p',
    CONSTRAINT pk_subscription_tier PRIMARY KEY (tier_id),
    CONSTRAINT uq_subscription_tier_name UNIQUE (tier_name),
    CONSTRAINT chk_tier_price CHECK (monthly_price >= 0.00),
    CONSTRAINT chk_tier_max_profiles CHECK (max_profiles_allowed BETWEEN 1 AND 5),
    CONSTRAINT chk_tier_max_streams CHECK (max_concurrent_streams >= 1),
    CONSTRAINT chk_tier_resolution CHECK (resolution IN ('1080p', '2K', '4K'))
);

-- =====================================================================
-- BẢNG 2: USER_ACCOUNT
-- =====================================================================
CREATE TABLE user_account (
    account_id INT AUTO_INCREMENT,
    email VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    registration_date DATE NOT NULL DEFAULT (CURRENT_DATE),
    account_status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    tier_id INT NOT NULL,
    CONSTRAINT pk_user_account PRIMARY KEY (account_id),
    CONSTRAINT uq_user_account_email UNIQUE (email),
    CONSTRAINT chk_account_status CHECK (account_status IN ('ACTIVE', 'SUSPENDED', 'CANCELED')),
    CONSTRAINT fk_account_tier FOREIGN KEY (tier_id)
        REFERENCES subscription_tier (tier_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

-- =====================================================================
-- BẢNG 3: PROFILE
-- =====================================================================
CREATE TABLE profile (
    profile_id INT AUTO_INCREMENT,
    account_id INT NOT NULL,
    profile_name VARCHAR(100) NOT NULL,
    avatar_url VARCHAR(500) NULL DEFAULT NULL,
    is_kids BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_profile PRIMARY KEY (profile_id),
    CONSTRAINT uq_profile_account_name UNIQUE (account_id, profile_name),
    CONSTRAINT fk_profile_account FOREIGN KEY (account_id)
        REFERENCES user_account (account_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- =====================================================================
-- BẢNG 4: LANGUAGE
-- =====================================================================
CREATE TABLE language (
    language_code VARCHAR(10) NOT NULL,
    language_name VARCHAR(50) NOT NULL,
    CONSTRAINT pk_language PRIMARY KEY (language_code),
    CONSTRAINT uq_language_name UNIQUE (language_name)
);

-- =====================================================================
-- BẢNG 5: GENRE
-- =====================================================================
CREATE TABLE genre (
    genre_id INT AUTO_INCREMENT,
    genre_name VARCHAR(50) NOT NULL,
    CONSTRAINT pk_genre PRIMARY KEY (genre_id),
    CONSTRAINT uq_genre_name UNIQUE (genre_name)
);

-- =====================================================================
-- BẢNG 6: CONTENT
-- =====================================================================
CREATE TABLE content (
    content_id INT AUTO_INCREMENT,
    title VARCHAR(255) NOT NULL,
    description TEXT NULL,
    release_year SMALLINT NOT NULL,
    rating_age VARCHAR(10) NOT NULL DEFAULT 'G',
    content_type VARCHAR(20) NOT NULL,
    language_code VARCHAR(10) NOT NULL,
    CONSTRAINT pk_content PRIMARY KEY (content_id),
    CONSTRAINT chk_content_release_year CHECK (release_year BETWEEN 1888 AND 2100),
    CONSTRAINT chk_content_rating_age CHECK (rating_age IN ('G', 'PG', 'PG-13', 'R', 'NC-17')),
    CONSTRAINT chk_content_type CHECK (content_type IN ('MOVIE', 'TV_SERIES')),
    CONSTRAINT fk_content_language FOREIGN KEY (language_code)
        REFERENCES language (language_code)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

-- =====================================================================
-- BẢNG 7: CONTENT_GENRE
-- =====================================================================
CREATE TABLE content_genre (
    content_id INT NOT NULL,
    genre_id INT NOT NULL,
    CONSTRAINT pk_content_genre PRIMARY KEY (content_id, genre_id),
    CONSTRAINT fk_cg_content FOREIGN KEY (content_id)
        REFERENCES content (content_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_cg_genre FOREIGN KEY (genre_id)
        REFERENCES genre (genre_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

-- =====================================================================
-- BẢNG 8: MOVIE
-- =====================================================================
CREATE TABLE movie (
    content_id INT NOT NULL,
    duration_minutes INT NOT NULL,
    video_resolution VARCHAR(10) NOT NULL DEFAULT '1080p',
    CONSTRAINT pk_movie PRIMARY KEY (content_id),
    CONSTRAINT chk_movie_duration CHECK (duration_minutes > 0),
    CONSTRAINT chk_movie_resolution CHECK (video_resolution IN ('1080p', '2K', '4K')),
    CONSTRAINT fk_movie_content FOREIGN KEY (content_id)
        REFERENCES content (content_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- =====================================================================
-- BẢNG 9: TV_SERIES
-- =====================================================================
CREATE TABLE tv_series (
    content_id INT NOT NULL,
    total_seasons INT NOT NULL DEFAULT 1,
    series_status VARCHAR(20) NOT NULL DEFAULT 'ONGOING',
    CONSTRAINT pk_tv_series PRIMARY KEY (content_id),
    CONSTRAINT chk_series_seasons CHECK (total_seasons >= 1),
    CONSTRAINT chk_series_status CHECK (series_status IN ('ONGOING', 'COMPLETED', 'CANCELLED')),
    CONSTRAINT fk_tv_series_content FOREIGN KEY (content_id)
        REFERENCES content (content_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- =====================================================================
-- BẢNG 10: SEASON
-- =====================================================================
CREATE TABLE season (
    season_id INT AUTO_INCREMENT,
    content_id INT NOT NULL,
    season_number INT NOT NULL DEFAULT 1,
    season_name VARCHAR(100) NULL DEFAULT NULL,
    release_date DATE NULL DEFAULT NULL,
    CONSTRAINT pk_season PRIMARY KEY (season_id),
    CONSTRAINT uq_season_series_number UNIQUE (content_id, season_number),
    CONSTRAINT chk_season_number CHECK (season_number >= 1),
    CONSTRAINT fk_season_tv_series FOREIGN KEY (content_id)
        REFERENCES tv_series (content_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- =====================================================================
-- BẢNG 11: TV_EPISODE
-- =====================================================================
CREATE TABLE tv_episode (
    episode_id INT AUTO_INCREMENT,
    season_id INT NOT NULL,
    episode_number INT NOT NULL,
    episode_title VARCHAR(255) NOT NULL,
    duration_minutes INT NOT NULL,
    CONSTRAINT pk_tv_episode PRIMARY KEY (episode_id),
    CONSTRAINT uq_episode_season_number UNIQUE (season_id, episode_number),
    CONSTRAINT chk_episode_number CHECK (episode_number >= 1),
    CONSTRAINT chk_episode_duration CHECK (duration_minutes > 0),
    CONSTRAINT fk_episode_season FOREIGN KEY (season_id)
        REFERENCES season (season_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- =====================================================================
-- BẢNG 12: WATCHLIST
-- =====================================================================
CREATE TABLE watchlist (
    profile_id INT NOT NULL,
    content_id INT NOT NULL,
    added_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_watchlist PRIMARY KEY (profile_id, content_id),
    CONSTRAINT fk_watchlist_profile FOREIGN KEY (profile_id)
        REFERENCES profile (profile_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_watchlist_content FOREIGN KEY (content_id)
        REFERENCES content (content_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- =====================================================================
-- BẢNG 13: WATCH_HISTORY
-- =====================================================================
CREATE TABLE watch_history (
    history_id INT AUTO_INCREMENT,
    profile_id INT NOT NULL,
    content_id INT NOT NULL,
    episode_id INT NULL DEFAULT NULL,
    last_watched_timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    stopped_position_seconds INT NOT NULL DEFAULT 0,
    is_completed BOOLEAN NOT NULL DEFAULT FALSE,
    CONSTRAINT pk_watch_history PRIMARY KEY (history_id),
    CONSTRAINT uq_watch_history_profile_content UNIQUE (profile_id, content_id),
    CONSTRAINT chk_history_stopped_pos CHECK (stopped_position_seconds >= 0),
    CONSTRAINT fk_history_profile FOREIGN KEY (profile_id)
        REFERENCES profile (profile_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_history_content FOREIGN KEY (content_id)
        REFERENCES content (content_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_history_episode FOREIGN KEY (episode_id)
        REFERENCES tv_episode (episode_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- =====================================================================
-- INDEXES
-- =====================================================================
CREATE INDEX idx_content_title ON content (title);
CREATE INDEX idx_content_type_year ON content (content_type, release_year);
CREATE INDEX idx_content_rating ON content (rating_age);
CREATE INDEX idx_watch_history_last_watched ON watch_history (profile_id, last_watched_timestamp DESC);

DELIMITER $$

-- ---------------------------------------------------------------------
-- TRIGGER 1: Kiểm tra giới hạn số lượng Profile theo gói cước (BR-01, FR-02)
-- ---------------------------------------------------------------------
CREATE TRIGGER trg_check_profile_limit_before_insert
BEFORE INSERT ON profile
FOR EACH ROW
BEGIN
    DECLARE v_current_profiles INT DEFAULT 0;
    DECLARE v_max_allowed INT DEFAULT 1;

    -- 1. Đếm số lượng profile hiện có của tài khoản đang định tạo thêm
    SELECT COUNT(*)
    INTO v_current_profiles
    FROM profile
    WHERE account_id = NEW.account_id;

    -- 2. Tra cứu số profile tối đa mà gói cước của tài khoản này cho phép
    SELECT st.max_profiles_allowed
    INTO v_max_allowed
    FROM user_account AS ua
    INNER JOIN subscription_tier AS st ON ua.tier_id = st.tier_id
    WHERE ua.account_id = NEW.account_id;

    -- 3. Nếu số lượng hiện tại đã chạm hoặc vượt mức cho phép thì chặn lại
    IF v_current_profiles >= v_max_allowed THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Vi pham BR-01/FR-02: Tai khoan da dat gioi han so luong Profile toi da cua goi cuoc!';
    END IF;
END$$

-- ---------------------------------------------------------------------
-- TRIGGER 2: Chặn Hồ sơ trẻ em (is_kids = TRUE) xem phim nhãn R và NC-17 (BR-09)
-- ---------------------------------------------------------------------
CREATE TRIGGER trg_check_kids_rating_before_watch
BEFORE INSERT ON watch_history
FOR EACH ROW
BEGIN
    DECLARE v_is_kids BOOLEAN DEFAULT FALSE;
    DECLARE v_rating_age VARCHAR(10);

    -- 1. Kiểm tra xem profile đang xem có bật chế độ trẻ em (is_kids) không
    SELECT is_kids
    INTO v_is_kids
    FROM profile
    WHERE profile_id = NEW.profile_id;

    -- 2. Lấy nhãn độ tuổi MPAA của bộ phim đang định xem
    SELECT rating_age
    INTO v_rating_age
    FROM content
    WHERE content_id = NEW.content_id;

    -- 3. Nếu là trẻ em mà xem phim R hoặc NC-17 thì chặn ngay lập tức
    IF v_is_kids = TRUE AND v_rating_age IN ('R', 'NC-17') THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Vi pham BR-09: Ho so tre em (is_kids = TRUE) bi chan truy cap noi dung gan nhan R va NC-17!';
    END IF;
END$$

DELIMITER ;

-- ---------------------------------------------------------------------
-- VIEW 1: Danh mục phim toàn diện (Kết hợp Content + Movie/TV_Series + Language + Genres)
-- ---------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_content_full_catalog AS
SELECT
    c.content_id,
    c.title,
    c.content_type,
    c.release_year,
    c.rating_age,
    l.language_name AS original_language,
    GROUP_CONCAT(g.genre_name ORDER BY g.genre_name SEPARATOR ', ') AS genres,
    m.duration_minutes AS movie_duration_mins,
    m.video_resolution AS movie_resolution,
    tv.total_seasons AS series_total_seasons,
    tv.series_status
FROM content AS c
INNER JOIN language AS l ON c.language_code = l.language_code
LEFT JOIN movie AS m ON c.content_id = m.content_id
LEFT JOIN tv_series AS tv ON c.content_id = tv.content_id
LEFT JOIN content_genre AS cg ON c.content_id = cg.content_id
LEFT JOIN genre AS g ON cg.genre_id = g.genre_id
GROUP BY
    c.content_id,
    c.title,
    c.content_type,
    c.release_year,
    c.rating_age,
    l.language_name,
    m.duration_minutes,
    m.video_resolution,
    tv.total_seasons,
    tv.series_status;

-- ---------------------------------------------------------------------
-- VIEW 2: Báo cáo doanh thu hàng tháng theo từng Subscription Tier
-- ---------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_subscription_revenue_summary AS
SELECT
    st.tier_id,
    st.tier_name,
    st.monthly_price,
    st.resolution,
    COUNT(ua.account_id) AS active_subscribers_count,
    COALESCE(COUNT(ua.account_id) * st.monthly_price, 0.00) AS estimated_monthly_revenue
FROM subscription_tier AS st
LEFT JOIN user_account AS ua
    ON st.tier_id = ua.tier_id
    AND ua.account_status = 'ACTIVE'
GROUP BY
    st.tier_id,
    st.tier_name,
    st.monthly_price,
    st.resolution;