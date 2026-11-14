USE mini_netflix;

-- =====================================================================
-- KỊCH BẢN KIỂM THỬ CHẶN DỮ LIỆU SAI (NEGATIVE TEST CASES)
-- Khớp Bảng 5.1 trong Báo cáo Dự án Nhóm G12
-- Lưu ý: Chạy từng lệnh riêng lẻ để quan sát mã lỗi MySQL chặn lại.
-- =====================================================================

-- [TC-01] Kiểm thử Trigger 1 (BR-01 / FR-02 - trg_check_profile_limit_before_insert):
-- Tài khoản ID = 1 (Gói Basic) chỉ được tối đa 1 profile và đã có sẵn 1 profile.
-- Kỳ vọng: Error Code 1644 (SQLSTATE '45000') - Vi pham BR-01/FR-02: Tai khoan da dat gioi han so luong Profile toi da cua goi cuoc!
INSERT INTO profile (account_id, profile_name, is_kids)
VALUES (1, 'Hồ sơ vượt quá giới hạn', FALSE);

-- [TC-02] Kiểm thử Trigger 2 (BR-09 - trg_check_kids_rating_before_watch):
-- Hồ sơ ID = 3 ('Bé Bi', is_kids = TRUE) cố tình xem nội dung ID = 6 (gắn nhãn R).
-- Kỳ vọng: Error Code 1644 (SQLSTATE '45000') - Vi pham BR-09: Ho so tre em (is_kids = TRUE) bi chan truy cap noi dung gan nhan R va NC-17!
INSERT INTO watch_history (profile_id, content_id, episode_id, stopped_position_seconds, is_completed)
VALUES (3, 6, NULL, 120, FALSE);

-- [TC-03] Kiểm thử khóa UNIQUE thực thể yếu (BR-08 - uq_season_series_number):
-- Phim bộ ID = 7 đã có sẵn Mùa 1 (season_number = 1).
-- Kỳ vọng: Error Code 1062 - Duplicate entry '7-1' for key 'season.uq_season_series_number'
INSERT INTO season (content_id, season_number, season_name)
VALUES (7, 1, 'Mùa 1 bị trùng lặp');

-- [TC-04] Kiểm thử khóa ngoại toàn vẹn tham chiếu (BR-05 - fk_account_tier ON DELETE RESTRICT):
-- Cố tình xóa gói cước ID = 3 (Premium) đang có người dùng sử dụng.
-- Kỳ vọng: Error Code 1451 - Cannot delete or update a parent row: a foreign key constraint fails
DELETE FROM subscription_tier WHERE tier_id = 3;

-- [TC-05] Kiểm thử ràng buộc CHECK miền giá trị (chk_movie_duration):
-- Cố tình chèn thời lượng phim lẻ là số âm (-45 phút).
-- Kỳ vọng: Error Code 3819 - Check constraint 'chk_movie_duration' is violated.
INSERT INTO movie (content_id, duration_minutes, video_resolution)
VALUES (1, -45, '1080p');
