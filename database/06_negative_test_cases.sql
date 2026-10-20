-- Trigger 1 
INSERT INTO profile (account_id, profile_name, is_kids)
VALUES (1, 'Hồ sơ vượt quá giới hạn', FALSE);

-- Trigger 2
INSERT INTO watch_history (profile_id, content_id, episode_id, stopped_position_seconds, is_completed)
VALUES (3, 6, NULL, 120, FALSE);

--  khóa CHECK (chk_movie_duration)
INSERT INTO movie (content_id, duration_minutes, video_resolution)
VALUES (1, -45, '1080p');

--  khóa UNIQUE (uq_season_series_number)
INSERT INTO season (content_id, season_number, season_name)
VALUES (7, 1, 'Mùa 1 bị trùng lặp');

-- khóa ngoại (fk_account_tier)
DELETE FROM subscription_tier WHERE tier_id = 3;