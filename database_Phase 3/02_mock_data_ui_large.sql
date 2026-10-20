USE mini_netflix;

-- Seed UI quy mo lon. Chay sau 02_mock_data.sql.
-- Them 120 movie, 40 TV series, 120 season, 960 episode, 60 account,
-- 180 profile, 1,800 watchlist va 2,160 watch_history.
-- shortcut: INSERT IGNORE makes this seed re-runnable, use a staging table when validating each rejected row.

DROP PROCEDURE IF EXISTS seed_ui_large_mock;

DELIMITER $$

CREATE PROCEDURE seed_ui_large_mock()
BEGIN
    DECLARE v_i INT DEFAULT 1;
    DECLARE v_j INT;
    DECLARE v_content_id INT;
    DECLARE v_season_id INT;
    DECLARE v_account_id INT;
    DECLARE v_profile_id INT;
    DECLARE v_target_content_id INT;
    DECLARE v_catalog_size INT;
    DECLARE v_target_index INT;
    DECLARE v_target_offset INT;
    DECLARE v_tier_id INT;
    DECLARE v_profile_count INT;
    DECLARE v_is_kids BOOLEAN;
    DECLARE v_title VARCHAR(255);
    DECLARE v_language_code VARCHAR(10);
    DECLARE v_rating VARCHAR(10);
    DECLARE v_status VARCHAR(20);

    START TRANSACTION;

    INSERT IGNORE INTO language (language_code, language_name) VALUES
        ('zh', 'Chinese'),
        ('fr', 'French'),
        ('th', 'Thai'),
        ('de', 'German'),
        ('hi', 'Hindi');

    INSERT IGNORE INTO genre (genre_name) VALUES
        ('Phiêu lưu'),
        ('Chính kịch'),
        ('Tài liệu'),
        ('Gia đình'),
        ('Tội phạm'),
        ('Lãng mạn');

    -- 120 phim lẻ, phân bố đều ngôn ngữ, nhãn tuổi, độ phân giải và thể loại.
    SET v_i = 1;
    WHILE v_i <= 120 DO
        SET v_title = CONCAT('G12 UI Movie ', LPAD(v_i, 3, '0'));
        SET v_language_code = ELT(1 + MOD(v_i - 1, 10), 'vi', 'en', 'ko', 'ja', 'es', 'zh', 'fr', 'th', 'de', 'hi');
        SET v_rating = ELT(1 + MOD(v_i - 1, 5), 'G', 'PG', 'PG-13', 'R', 'NC-17');

        INSERT INTO content (title, description, release_year, rating_age, content_type, language_code)
        SELECT
            v_title,
            CONCAT('Nội dung giả lập cho giao diện Mini-Netflix, phim lẻ số ', LPAD(v_i, 3, '0'), '.'),
            1995 + MOD(v_i * 7, 31),
            v_rating,
            'MOVIE',
            v_language_code
        FROM DUAL
        WHERE NOT EXISTS (SELECT 1 FROM content WHERE title = v_title);

        SELECT content_id INTO v_content_id
        FROM content
        WHERE title = v_title;

        INSERT IGNORE INTO movie (content_id, duration_minutes, video_resolution)
        VALUES (v_content_id, 80 + MOD(v_i * 13, 101), ELT(1 + MOD(v_i - 1, 3), '1080p', '2K', '4K'));

        INSERT IGNORE INTO content_genre (content_id, genre_id)
        SELECT v_content_id, genre_id
        FROM genre
        WHERE genre_name IN (
            ELT(1 + MOD(v_i - 1, 12), 'Hành động', 'Khoa học viễn tưởng', 'Tâm lý - Tình cảm', 'Hoạt hình', 'Kinh dị - Giật gân', 'Hài hước', 'Phiêu lưu', 'Chính kịch', 'Tài liệu', 'Gia đình', 'Tội phạm', 'Lãng mạn'),
            ELT(1 + MOD(v_i + 4, 12), 'Hành động', 'Khoa học viễn tưởng', 'Tâm lý - Tình cảm', 'Hoạt hình', 'Kinh dị - Giật gân', 'Hài hước', 'Phiêu lưu', 'Chính kịch', 'Tài liệu', 'Gia đình', 'Tội phạm', 'Lãng mạn')
        );

        SET v_i = v_i + 1;
    END WHILE;

    -- 40 phim bo, moi phim co dung 3 season va moi season co 8 episode.
    SET v_i = 1;
    WHILE v_i <= 40 DO
        SET v_title = CONCAT('G12 UI Series ', LPAD(v_i, 3, '0'));
        SET v_language_code = ELT(1 + MOD(v_i + 2, 10), 'vi', 'en', 'ko', 'ja', 'es', 'zh', 'fr', 'th', 'de', 'hi');
        SET v_rating = ELT(1 + MOD(v_i, 5), 'G', 'PG', 'PG-13', 'R', 'NC-17');

        INSERT INTO content (title, description, release_year, rating_age, content_type, language_code)
        SELECT
            v_title,
            CONCAT('Nội dung giả lập cho giao diện Mini-Netflix, phim bộ số ', LPAD(v_i, 3, '0'), '.'),
            2000 + MOD(v_i * 5, 26),
            v_rating,
            'TV_SERIES',
            v_language_code
        FROM DUAL
        WHERE NOT EXISTS (SELECT 1 FROM content WHERE title = v_title);

        SELECT content_id INTO v_content_id
        FROM content
        WHERE title = v_title;

        INSERT IGNORE INTO tv_series (content_id, total_seasons, series_status)
        VALUES (v_content_id, 3, ELT(1 + MOD(v_i - 1, 3), 'ONGOING', 'COMPLETED', 'CANCELLED'));

        INSERT IGNORE INTO content_genre (content_id, genre_id)
        SELECT v_content_id, genre_id
        FROM genre
        WHERE genre_name IN (
            ELT(1 + MOD(v_i + 1, 12), 'Hành động', 'Khoa học viễn tưởng', 'Tâm lý - Tình cảm', 'Hoạt hình', 'Kinh dị - Giật gân', 'Hài hước', 'Phiêu lưu', 'Chính kịch', 'Tài liệu', 'Gia đình', 'Tội phạm', 'Lãng mạn'),
            ELT(1 + MOD(v_i + 6, 12), 'Hành động', 'Khoa học viễn tưởng', 'Tâm lý - Tình cảm', 'Hoạt hình', 'Kinh dị - Giật gân', 'Hài hước', 'Phiêu lưu', 'Chính kịch', 'Tài liệu', 'Gia đình', 'Tội phạm', 'Lãng mạn')
        );

        SET v_j = 1;
        WHILE v_j <= 3 DO
            INSERT IGNORE INTO season (content_id, season_number, season_name, release_date)
            VALUES (
                v_content_id,
                v_j,
                CONCAT(v_title, ' - Mùa ', v_j),
                DATE_ADD('2018-01-01', INTERVAL (v_i * 31 + v_j * 120) DAY)
            );

            SELECT season_id INTO v_season_id
            FROM season
            WHERE content_id = v_content_id AND season_number = v_j;

            SET v_target_index = 1;
            WHILE v_target_index <= 8 DO
                INSERT IGNORE INTO tv_episode (season_id, episode_number, episode_title, duration_minutes)
                VALUES (
                    v_season_id,
                    v_target_index,
                    CONCAT('Tập ', LPAD(v_target_index, 2, '0'), ': Chương ', v_target_index, ' của ', v_title),
                    22 + MOD(v_i * 7 + v_j * 11 + v_target_index * 3, 39)
                );
                SET v_target_index = v_target_index + 1;
            END WHILE;

            SET v_j = v_j + 1;
        END WHILE;

        SET v_i = v_i + 1;
    END WHILE;

    -- 60 account va profile phu thuoc dung gioi han cua moi goi cuoc.
    SET v_i = 1;
    WHILE v_i <= 60 DO
        SET v_tier_id = 1 + MOD(v_i - 1, 3);
        SET v_status = CASE
            WHEN MOD(v_i, 15) = 0 THEN 'CANCELED'
            WHEN MOD(v_i, 10) = 0 THEN 'SUSPENDED'
            ELSE 'ACTIVE'
        END;

        INSERT IGNORE INTO user_account (email, password_hash, registration_date, account_status, tier_id)
        VALUES (
            CONCAT('ui.user', LPAD(v_i, 3, '0'), '@demo.mininetflix.local'),
            '$2b$12$G12UiMockDataOnlyNotARealBcryptHash000000000000000000',
            DATE_SUB(CURDATE(), INTERVAL v_i * 9 DAY),
            v_status,
            v_tier_id
        );

        SELECT account_id INTO v_account_id
        FROM user_account
        WHERE email = CONCAT('ui.user', LPAD(v_i, 3, '0'), '@demo.mininetflix.local');

        SET v_profile_count = CASE v_tier_id WHEN 1 THEN 1 WHEN 2 THEN 3 ELSE 5 END;
        SET v_j = 1;
        WHILE v_j <= v_profile_count DO
            SET v_is_kids = (v_j = 2 AND v_tier_id IN (2, 3));
            INSERT INTO profile (account_id, profile_name, avatar_url, is_kids)
            SELECT
                v_account_id,
                CONCAT(IF(v_is_kids, 'Bé ', 'Viewer '), LPAD(v_i, 3, '0'), '-', v_j),
                CONCAT('https://example.invalid/avatars/', v_i, '-', v_j, '.png'),
                v_is_kids
            FROM DUAL
            WHERE NOT EXISTS (
                SELECT 1
                FROM profile
                WHERE account_id = v_account_id
                  AND profile_name = CONCAT(IF(v_is_kids, 'Bé ', 'Viewer '), LPAD(v_i, 3, '0'), '-', v_j)
            );

            SELECT profile_id INTO v_profile_id
            FROM profile
            WHERE account_id = v_account_id
              AND profile_name = CONCAT(IF(v_is_kids, 'Bé ', 'Viewer '), LPAD(v_i, 3, '0'), '-', v_j);

            -- 10 phim trong watchlist va 12 luot xem/profile.
            SET v_catalog_size = 0;
            SELECT COUNT(*) INTO v_catalog_size
            FROM content
            WHERE title LIKE 'G12 UI %'
              AND (NOT v_is_kids OR rating_age NOT IN ('R', 'NC-17'));

            SET v_target_index = 1;
            WHILE v_target_index <= 10 DO
                SET v_target_content_id = NULL;
                SET v_target_offset = MOD(v_profile_id * 17 + v_target_index * 11, v_catalog_size);
                SELECT content_id INTO v_target_content_id
                FROM content
                WHERE title LIKE 'G12 UI %'
                  AND (NOT v_is_kids OR rating_age NOT IN ('R', 'NC-17'))
                ORDER BY content_id
                LIMIT v_target_offset, 1;

                INSERT IGNORE INTO watchlist (profile_id, content_id, added_at)
                VALUES (v_profile_id, v_target_content_id, DATE_SUB(NOW(), INTERVAL v_target_index DAY));

                SET v_target_index = v_target_index + 1;
            END WHILE;

            SET v_target_index = 1;
            WHILE v_target_index <= 12 DO
                SET v_target_content_id = NULL;
                SET v_target_offset = MOD(v_profile_id * 29 + v_target_index * 13, v_catalog_size);
                SELECT content_id INTO v_target_content_id
                FROM content
                WHERE title LIKE 'G12 UI %'
                  AND (NOT v_is_kids OR rating_age NOT IN ('R', 'NC-17'))
                ORDER BY content_id
                LIMIT v_target_offset, 1;

                INSERT IGNORE INTO watch_history (
                    profile_id, content_id, episode_id, last_watched_timestamp,
                    stopped_position_seconds, is_completed
                )
                SELECT
                    v_profile_id,
                    v_target_content_id,
                    CASE WHEN c.content_type = 'TV_SERIES' THEN (
                        SELECT MIN(ep.episode_id)
                        FROM season s
                        INNER JOIN tv_episode ep ON ep.season_id = s.season_id
                        WHERE s.content_id = c.content_id
                    ) END,
                    DATE_SUB(NOW(), INTERVAL (v_target_index * 3 + MOD(v_profile_id, 7)) HOUR),
                    300 + MOD(v_profile_id * 97 + v_target_index * 211, 3200),
                    MOD(v_target_index, 5) IN (0, 1)
                FROM content c
                WHERE c.content_id = v_target_content_id;

                SET v_target_index = v_target_index + 1;
            END WHILE;

            SET v_j = v_j + 1;
        END WHILE;

        SET v_i = v_i + 1;
    END WHILE;

    COMMIT;
END$$

DELIMITER ;

CALL seed_ui_large_mock();
DROP PROCEDURE seed_ui_large_mock;
