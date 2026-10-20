USE mini_netflix;

-- 1. Tạo 3 nhóm quyền (Roles) theo kiến trúc bảo mật RBAC
DROP ROLE IF EXISTS 'role_system_admin', 'role_content_manager', 'role_streaming_client';
CREATE ROLE 'role_system_admin', 'role_content_manager', 'role_streaming_client';

-- 2. Cấp toàn quyền cho Quản trị viên hệ thống (DBA)
GRANT ALL PRIVILEGES ON mini_netflix.* TO 'role_system_admin' WITH GRANT OPTION;

-- 3. Cấp quyền cho Biên tập viên nội dung (Chỉ quản lý kho phim, không được xem User Account)
GRANT SELECT, INSERT, UPDATE, DELETE ON mini_netflix.language TO 'role_content_manager';
GRANT SELECT, INSERT, UPDATE, DELETE ON mini_netflix.genre TO 'role_content_manager';
GRANT SELECT, INSERT, UPDATE, DELETE ON mini_netflix.content TO 'role_content_manager';
GRANT SELECT, INSERT, UPDATE, DELETE ON mini_netflix.content_genre TO 'role_content_manager';
GRANT SELECT, INSERT, UPDATE, DELETE ON mini_netflix.movie TO 'role_content_manager';
GRANT SELECT, INSERT, UPDATE, DELETE ON mini_netflix.tv_series TO 'role_content_manager';
GRANT SELECT, INSERT, UPDATE, DELETE ON mini_netflix.season TO 'role_content_manager';
GRANT SELECT, INSERT, UPDATE, DELETE ON mini_netflix.tv_episode TO 'role_content_manager';
GRANT SELECT ON mini_netflix.vw_content_full_catalog TO 'role_content_manager';

-- 4. Cấp quyền tối thiểu (Least Privilege) cho Ứng dụng Client phía người dùng
GRANT SELECT ON mini_netflix.subscription_tier TO 'role_streaming_client';
GRANT SELECT, UPDATE (email, password_hash) ON mini_netflix.user_account TO 'role_streaming_client';
GRANT SELECT, INSERT, UPDATE, DELETE ON mini_netflix.profile TO 'role_streaming_client';
GRANT SELECT ON mini_netflix.vw_content_full_catalog TO 'role_streaming_client';
GRANT SELECT ON mini_netflix.content TO 'role_streaming_client';
GRANT SELECT ON mini_netflix.movie TO 'role_streaming_client';
GRANT SELECT ON mini_netflix.tv_series TO 'role_streaming_client';
GRANT SELECT ON mini_netflix.season TO 'role_streaming_client';
GRANT SELECT ON mini_netflix.tv_episode TO 'role_streaming_client';
GRANT SELECT, INSERT, DELETE ON mini_netflix.watchlist TO 'role_streaming_client';
GRANT SELECT, INSERT, UPDATE, DELETE ON mini_netflix.watch_history TO 'role_streaming_client';

-- 5. Minh họa thu hồi quyền (REVOKE): Cấm ứng dụng Client xóa lịch sử xem để bảo toàn dữ liệu phân tích
REVOKE DELETE ON mini_netflix.watch_history FROM 'role_streaming_client';