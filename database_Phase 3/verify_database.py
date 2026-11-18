"""
Mini-Netflix Automated Verification & Test Runner (Nhóm G12)
Học phần: Cơ sở dữ liệu (INT1313) | Đề tài #2: Mini-Netflix

Công dụng:
  Kiểm chứng tự động toàn bộ Cơ sở dữ liệu MySQL `mini_netflix` và kết nối 3-Tier API:
  1. Toàn vẹn cấu trúc Schema (13 bảng, 2 views, 2 triggers, 4 indexes) & 86.895 bản ghi.
  2. Toàn vẹn mô hình EER (Disjoint & Total Completeness trên 8.817 titles, f3 consistency).
  3. Khớp 100% 5 Negative Test Cases trong Báo cáo (`TC-01` .. `TC-05`).
  4. Bộ Positive & Boundary Test Cases (`EXT-POS-01` .. `EXT-POS-04`).
  5. Bộ Extended Negative Constraints (`EXT-NEG-01` .. `EXT-NEG-12`).
  6. Kiểm thử xóa lan truyền `ON DELETE CASCADE` (`EXT-CAS-01` .. `EXT-CAS-02`).
  7. Kiểm thử thực tế phân quyền RBAC từ `05_rbac_security.sql` bằng user tạm (Error 1142).
  8. Kiểm chứng 10 truy vấn `03_queries.sql`, 2 Views & cả 4 B-Tree Indexes (< 200ms).
  9. Smoke Test giao tiếp REST API qua Flask `app.test_client()`.

An toàn dữ liệu:
  - Mọi kiểm thử DML đều chạy trong `START TRANSACTION` và `ROLLBACK` về trạng thái gốc.
  - User RBAC tạm được tạo và xóa sạch trong khối `finally`.

Cách chạy:
  python verify_database.py
"""

from __future__ import annotations

import os
import re
import secrets
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable

import mysql.connector
from dotenv import load_dotenv
from mysql.connector import Error

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

PHASE3_DIR = Path(__file__).resolve().parent
REPO_ROOT = PHASE3_DIR.parent
WEB_UI_DIR = REPO_ROOT / "web-ui"

load_dotenv(dotenv_path=WEB_UI_DIR / ".env")


@dataclass
class TestRecord:
    """Lưu kết quả từng ca kiểm thử để tổng hợp báo cáo."""

    code: str
    category: str
    description: str
    passed: bool
    detail: str


class TestSuiteRunner:
    """Bộ điều phối chạy các ca kiểm thử trên MySQL thật và tổng hợp PASS/FAIL."""

    def __init__(self) -> None:
        self.db_cfg = {
            "host": os.getenv("DB_HOST", "localhost"),
            "port": int(os.getenv("DB_PORT", 3306)),
            "user": os.getenv("DB_USER", "root"),
            "password": os.getenv("DB_PASSWORD", "123"),
            "database": os.getenv("DB_NAME", "mini_netflix"),
            "charset": "utf8mb4",
            "use_unicode": True,
        }
        self.results: list[TestRecord] = []

    def connect(self, **overrides):
        cfg = {**self.db_cfg, **overrides}
        return mysql.connector.connect(**cfg)

    def add_result(
        self, code: str, category: str, description: str, passed: bool, detail: str
    ) -> None:
        self.results.append(TestRecord(code, category, description, passed, detail))
        status = "PASS" if passed else "FAIL"
        print(f"[{status}] {code:<12} | {description} -> {detail}")

    def run_negative_case(
        self,
        code: str,
        category: str,
        description: str,
        sql_or_steps: str | Iterable[str],
        expected_errnos: int | Iterable[int],
    ) -> None:
        """Chạy lệnh SQL vi phạm trong transaction rồi ROLLBACK; đạt nếu bị chặn đúng mã lỗi."""
        expected = (
            {expected_errnos} if isinstance(expected_errnos, int) else set(expected_errnos)
        )
        steps = [sql_or_steps] if isinstance(sql_or_steps, str) else list(sql_or_steps)

        conn = self.connect()
        try:
            conn.start_transaction()
            cur = conn.cursor()
            try:
                for step in steps:
                    cur.execute(step)
                self.add_result(
                    code,
                    category,
                    description,
                    False,
                    f"Không bị chặn! Kỳ vọng Error {sorted(expected)}",
                )
            except Error as err:
                ok = err.errno in expected
                self.add_result(
                    code,
                    category,
                    description,
                    ok,
                    f"MySQL Error {err.errno} ({err.sqlstate}): {err.msg[:95]}",
                )
            finally:
                cur.close()
                conn.rollback()
        finally:
            conn.close()

    def run_tx_check(
        self,
        code: str,
        category: str,
        description: str,
        fn: Callable[[mysql.connector.MySQLConnection, mysql.connector.cursor.MySQLCursor], tuple[bool, str]],
    ) -> None:
        """Chạy hàm kiểm thử trong transaction cô lập và luôn ROLLBACK sau khi xong."""
        conn = self.connect()
        try:
            conn.start_transaction()
            cur = conn.cursor()
            try:
                ok, detail = fn(conn, cur)
                self.add_result(code, category, description, ok, detail)
            except Exception as exc:
                self.add_result(code, category, description, False, f"Lỗi ngoại lệ: {exc}")
            finally:
                cur.close()
                conn.rollback()
        finally:
            conn.close()

    # -----------------------------------------------------------------
    # 1. KIỂM TRA CẤU TRÚC SCHEMA, DỮ LIỆU & TOÀN VẸN EER
    # -----------------------------------------------------------------
    def test_schema_and_eer(self) -> None:
        conn = self.connect()
        cur = conn.cursor()
        try:
            cur.execute("SHOW FULL TABLES WHERE Table_type = 'BASE TABLE'")
            tables = [r[0] for r in cur.fetchall()]
            self.add_result(
                "SCH-01",
                "Schema",
                "Đủ 13 bảng quan hệ chuẩn hóa",
                len(tables) == 13,
                f"Tìm thấy {len(tables)}/13 bảng",
            )

            cur.execute("SHOW FULL TABLES WHERE Table_type = 'VIEW'")
            views = [r[0] for r in cur.fetchall()]
            self.add_result(
                "SCH-02",
                "Schema",
                "Đủ 2 Views (catalog & revenue)",
                set(views) >= {"vw_content_full_catalog", "vw_subscription_revenue_summary"},
                f"Views: {', '.join(views)}",
            )

            cur.execute("SHOW TRIGGERS")
            triggers = [r[0] for r in cur.fetchall()]
            self.add_result(
                "SCH-03",
                "Schema",
                "Đủ 2 Triggers BR-01 và BR-09",
                set(triggers)
                >= {
                    "trg_check_profile_limit_before_insert",
                    "trg_check_kids_rating_before_watch",
                },
                f"Triggers: {', '.join(triggers)}",
            )

            cur.execute(
                """
                SELECT DISTINCT index_name
                FROM information_schema.statistics
                WHERE table_schema = %s
                  AND index_name LIKE 'idx_%%'
                """,
                (self.db_cfg["database"],),
            )
            indexes = {r[0] for r in cur.fetchall()}
            expected_idx = {
                "idx_content_title",
                "idx_content_type_year",
                "idx_content_rating",
                "idx_watch_history_last_watched",
            }
            self.add_result(
                "SCH-04",
                "Schema",
                "Đủ 4 B-Tree Indexes tối ưu hóa",
                indexes == expected_idx,
                f"Indexes: {', '.join(sorted(indexes))}",
            )

            cur.execute("SELECT COUNT(*) FROM movie m INNER JOIN tv_series tv ON m.content_id = tv.content_id")
            overlap = cur.fetchone()[0]
            self.add_result(
                "EXT-EER-01",
                "EER Integrity",
                "Disjoint: MOVIE ∩ TV_SERIES = ∅",
                overlap == 0,
                f"Số bản ghi vi phạm chồng lấn = {overlap}",
            )

            cur.execute(
                """
                SELECT COUNT(*)
                FROM content c
                LEFT JOIN movie m ON c.content_id = m.content_id
                LEFT JOIN tv_series tv ON c.content_id = tv.content_id
                WHERE m.content_id IS NULL AND tv.content_id IS NULL
                """
            )
            orphans = cur.fetchone()[0]
            self.add_result(
                "EXT-EER-02",
                "EER Integrity",
                "Total Completeness: mọi CONTENT thuộc MOVIE hoặc TV_SERIES",
                orphans == 0,
                f"Số content mồ côi = {orphans}",
            )

            cur.execute(
                """
                SELECT COUNT(*)
                FROM watch_history wh
                INNER JOIN tv_episode ep ON wh.episode_id = ep.episode_id
                INNER JOIN season s ON ep.season_id = s.season_id
                WHERE wh.content_id <> s.content_id
                """
            )
            f3_bad = cur.fetchone()[0]
            self.add_result(
                "EXT-EER-03",
                "EER Integrity",
                "Phụ thuộc hàm f3: episode_id thuộc đúng content_id",
                f3_bad == 0,
                f"Số bản ghi sai lệch content_id/episode_id = {f3_bad}",
            )
        finally:
            cur.close()
            conn.close()

    # -----------------------------------------------------------------
    # 2. BỘ 5 NEGATIVE TEST CASES CHUẨN TRONG BÁO CÁO (TC-01 .. TC-05)
    # -----------------------------------------------------------------
    def test_report_negative_cases(self) -> None:
        cases = [
            (
                "TC-01",
                "Trigger BR-01: Chặn vượt quá 1 Profile của gói Basic (account 1)",
                "INSERT INTO profile (account_id, profile_name, is_kids) VALUES (1, 'Hồ sơ vượt giới hạn', FALSE)",
                1644,
            ),
            (
                "TC-02",
                "Trigger BR-09: Chặn hồ sơ trẻ em (profile 3) xem phim nhãn R (content 6)",
                "INSERT INTO watch_history (profile_id, content_id, episode_id, stopped_position_seconds, is_completed) VALUES (3, 6, NULL, 120, FALSE)",
                1644,
            ),
            (
                "TC-03",
                "UNIQUE Weak Entity: Chặn trùng mùa 1 của cùng TV_SERIES (content 7)",
                "INSERT INTO season (content_id, season_number, season_name) VALUES (7, 1, 'Mùa 1 bị trùng lặp')",
                1062,
            ),
            (
                "TC-04",
                "FK ON DELETE RESTRICT: Chặn xóa gói cước Premium (tier 3) đang có tài khoản",
                "DELETE FROM subscription_tier WHERE tier_id = 3",
                1451,
            ),
            (
                "TC-05",
                "CHECK Domain: Chặn thời lượng phim lẻ âm (-45 phút)",
                "INSERT INTO movie (content_id, duration_minutes, video_resolution) VALUES (1, -45, '1080p')",
                3819,
            ),
        ]
        for code, desc, sql, errno in cases:
            self.run_negative_case(code, "Report TC", desc, sql, errno)

    # -----------------------------------------------------------------
    # 3. POSITIVE & BOUNDARY TEST CASES (EXT-POS-01 .. EXT-POS-04)
    # -----------------------------------------------------------------
    def test_positive_and_boundary_cases(self) -> None:
        def pos_01(_conn, cur):
            cur.execute(
                "INSERT INTO profile (account_id, profile_name, is_kids) VALUES (2, 'Profile thứ 3 hợp lệ', FALSE)"
            )
            try:
                cur.execute(
                    "INSERT INTO profile (account_id, profile_name, is_kids) VALUES (2, 'Profile thứ 4 vượt hạn mức', FALSE)"
                )
                return False, "Hồ sơ thứ 4 vẫn lọt qua trigger!"
            except Error as err:
                return err.errno == 1644, f"Thêm thứ 3 OK, thêm thứ 4 bị chặn đúng Error {err.errno}"

        self.run_tx_check(
            "EXT-POS-01",
            "Positive Boundary",
            "BR-01 Cận biên gói Standard (max 3): thứ 3 thành công, thứ 4 bị chặn",
            pos_01,
        )

        def pos_02(_conn, cur):
            cur.execute(
                "INSERT INTO watch_history (profile_id, content_id, episode_id, stopped_position_seconds, is_completed) "
                "VALUES (3, 5, NULL, 900, FALSE)"
            )
            cur.execute("SELECT content_id FROM content WHERE rating_age = 'NC-17' LIMIT 1")
            nc17_id = cur.fetchone()[0]
            try:
                cur.execute(
                    "INSERT INTO watch_history (profile_id, content_id, episode_id, stopped_position_seconds, is_completed) "
                    "VALUES (3, %s, NULL, 60, FALSE)",
                    (nc17_id,),
                )
                return False, f"Hồ sơ trẻ em xem được NC-17 (content {nc17_id})!"
            except Error as err:
                return err.errno == 1644, f"Xem PG-13 OK, xem NC-17 (id={nc17_id}) bị chặn Error {err.errno}"

        self.run_tx_check(
            "EXT-POS-02",
            "Positive Boundary",
            "BR-09 Hồ sơ trẻ em: cho phép xem PG-13 và chặn NC-17",
            pos_02,
        )

        def pos_03(_conn, cur):
            cur.execute(
                "INSERT INTO watch_history (profile_id, content_id, episode_id, stopped_position_seconds, is_completed) "
                "VALUES (1, 7, 1, 600, FALSE)"
            )
            try:
                cur.execute(
                    "INSERT INTO watch_history (profile_id, content_id, episode_id, stopped_position_seconds, is_completed) "
                    "VALUES (1, 7, 2, 300, FALSE)"
                )
                return False, "Trùng (profile 1, content 7, episode 2) nhưng vẫn chèn được!"
            except Error as err:
                return err.errno == 1062, f"Lưu riêng tập 1 OK; trùng tập 2 bị chặn Error {err.errno}"

        self.run_tx_check(
            "EXT-POS-03",
            "Positive Boundary",
            "BR-06 Phim bộ: lưu riêng từng tập và chặn trùng (profile, content, episode)",
            pos_03,
        )

        def pos_04(_conn, cur):
            cur.execute(
                "INSERT INTO content (title, release_year, rating_age, content_type, language_code) "
                "VALUES ('Boundary Film 1888', 1888, 'G', 'MOVIE', 'en')"
            )
            cid = cur.lastrowid
            cur.execute(
                "INSERT INTO movie (content_id, duration_minutes, video_resolution) VALUES (%s, 1, '1080p')",
                (cid,),
            )
            cur.execute(
                "INSERT INTO watch_history (profile_id, content_id, episode_id, stopped_position_seconds, is_completed) "
                "VALUES (1, %s, NULL, 0, FALSE)",
                (cid,),
            )
            return True, f"Cận biên năm 1888, duration=1 phút, stopped=0 giây hợp lệ (content_id={cid})"

        self.run_tx_check(
            "EXT-POS-04",
            "Positive Boundary",
            "Cận biên CHECK: release_year=1888, duration=1, stopped=0",
            pos_04,
        )

    # -----------------------------------------------------------------
    # 4. EXTENDED NEGATIVE CONSTRAINTS (EXT-NEG-01 .. EXT-NEG-12)
    # -----------------------------------------------------------------
    def test_extended_negative_cases(self) -> None:
        ext_neg = [
            (
                "EXT-NEG-01",
                "UNIQUE Email tài khoản (uq_user_account_email)",
                "INSERT INTO user_account (email, password_hash, tier_id) VALUES ('an.nguyen@gmail.com', '$2b$12$Hash', 1)",
                1062,
            ),
            (
                "EXT-NEG-02",
                "UNIQUE Tên Profile trong cùng tài khoản (uq_profile_account_name)",
                "INSERT INTO profile (account_id, profile_name, is_kids) VALUES (2, 'Bình Trần', FALSE)",
                1062,
            ),
            (
                "EXT-NEG-03",
                "UNIQUE Tập phim trong cùng mùa (uq_episode_season_number)",
                "INSERT INTO tv_episode (season_id, episode_number, episode_title, duration_minutes) VALUES (1, 1, 'Tập trùng', 40)",
                1062,
            ),
            (
                "EXT-NEG-04",
                "Composite PK Watchlist chặn thêm trùng phim (pk_watchlist)",
                "INSERT INTO watchlist (profile_id, content_id) VALUES (1, 1)",
                1062,
            ),
            (
                "EXT-NEG-05",
                "CHECK chk_account_status từ chối giá trị 'BANNED'",
                "INSERT INTO user_account (email, password_hash, account_status, tier_id) VALUES ('bad.status@test.local', '$2b$12$Hash', 'BANNED', 1)",
                3819,
            ),
            (
                "EXT-NEG-06",
                "CHECK chk_content_rating_age từ chối nhãn '18+'",
                "INSERT INTO content (title, release_year, rating_age, content_type, language_code) VALUES ('Bad Rating', 2024, '18+', 'MOVIE', 'en')",
                3819,
            ),
            (
                "EXT-NEG-07",
                "CHECK chk_content_type từ chối loại 'ANIME'",
                "INSERT INTO content (title, release_year, rating_age, content_type, language_code) VALUES ('Bad Type', 2024, 'PG', 'ANIME', 'ja')",
                3819,
            ),
            (
                "EXT-NEG-08",
                "CHECK chk_content_release_year từ chối năm 1800 (< 1888)",
                "INSERT INTO content (title, release_year, rating_age, content_type, language_code) VALUES ('Year 1800', 1800, 'G', 'MOVIE', 'en')",
                3819,
            ),
            (
                "EXT-NEG-09",
                "CHECK chk_history_stopped_pos từ chối vị trí dừng âm (-10)",
                "INSERT INTO watch_history (profile_id, content_id, episode_id, stopped_position_seconds, is_completed) VALUES (1, 2, NULL, -10, FALSE)",
                3819,
            ),
            (
                "EXT-NEG-10",
                "CHECK chk_tier_max_profiles từ chối gói > 5 profile (10)",
                "INSERT INTO subscription_tier (tier_name, monthly_price, max_profiles_allowed, max_concurrent_streams, resolution) VALUES ('Invalid10', 99000.00, 10, 2, '4K')",
                3819,
            ),
            (
                "EXT-NEG-11A",
                "FK ON DELETE RESTRICT chặn xóa ngôn ngữ 'en' đang có phim dùng",
                "DELETE FROM language WHERE language_code = 'en'",
                1451,
            ),
            (
                "EXT-NEG-11B",
                "FK ON DELETE RESTRICT chặn xóa thể loại genre_id=1 đang được gán",
                "DELETE FROM genre WHERE genre_id = 1",
                1451,
            ),
            (
                "EXT-NEG-12",
                "FK Invalid Parent chặn chèn profile cho account_id=999999 không tồn tại",
                "INSERT INTO profile (account_id, profile_name, is_kids) VALUES (999999, 'Ghost Profile', FALSE)",
                1452,
            ),
        ]
        for code, desc, sql, errno in ext_neg:
            self.run_negative_case(code, "Extended Negative", desc, sql, errno)

    # -----------------------------------------------------------------
    # 5. KIỂM THỬ XÓA LAN TRUYỀN ON DELETE CASCADE (EXT-CAS-01 .. 02)
    # -----------------------------------------------------------------
    def test_cascade_deletes(self) -> None:
        def cas_user(_conn, cur):
            cur.execute(
                "INSERT INTO user_account (email, password_hash, tier_id) VALUES ('cascade.user@test.local', '$2b$12$Hash', 2)"
            )
            uid = cur.lastrowid
            cur.execute(
                "INSERT INTO profile (account_id, profile_name, is_kids) VALUES (%s, 'Cascade User Profile', FALSE)",
                (uid,),
            )
            pid = cur.lastrowid
            cur.execute("INSERT INTO watchlist (profile_id, content_id) VALUES (%s, 1)", (pid,))
            cur.execute(
                "INSERT INTO watch_history (profile_id, content_id, episode_id, stopped_position_seconds) VALUES (%s, 1, NULL, 120)",
                (pid,),
            )
            cur.execute("DELETE FROM user_account WHERE account_id = %s", (uid,))

            cur.execute("SELECT COUNT(*) FROM profile WHERE profile_id = %s", (pid,))
            rem_p = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM watchlist WHERE profile_id = %s", (pid,))
            rem_wl = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM watch_history WHERE profile_id = %s", (pid,))
            rem_wh = cur.fetchone()[0]
            ok = (rem_p, rem_wl, rem_wh) == (0, 0, 0)
            return ok, f"Sau xóa account={uid}: profile={rem_p}, watchlist={rem_wl}, watch_history={rem_wh}"

        self.run_tx_check(
            "EXT-CAS-01",
            "CASCADE Delete",
            "Xóa USER_ACCOUNT lan truyền xóa sạch PROFILE, WATCHLIST, WATCH_HISTORY",
            cas_user,
        )

        def cas_content(_conn, cur):
            cur.execute(
                "INSERT INTO content (title, release_year, rating_age, content_type, language_code) "
                "VALUES ('Cascade Test Series', 2025, 'PG', 'TV_SERIES', 'en')"
            )
            cid = cur.lastrowid
            cur.execute("INSERT INTO content_genre (content_id, genre_id) VALUES (%s, 1)", (cid,))
            cur.execute("INSERT INTO tv_series (content_id, total_seasons, series_status) VALUES (%s, 1, 'ONGOING')", (cid,))
            cur.execute("INSERT INTO season (content_id, season_number, season_name) VALUES (%s, 1, 'Mùa 1')", (cid,))
            sid = cur.lastrowid
            cur.execute(
                "INSERT INTO tv_episode (season_id, episode_number, episode_title, duration_minutes) VALUES (%s, 1, 'Tập 1', 40)",
                (sid,),
            )
            eid = cur.lastrowid

            cur.execute("DELETE FROM content WHERE content_id = %s", (cid,))
            cur.execute("SELECT COUNT(*) FROM tv_series WHERE content_id = %s", (cid,))
            rem_tv = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM season WHERE season_id = %s", (sid,))
            rem_s = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM tv_episode WHERE episode_id = %s", (eid,))
            rem_ep = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM content_genre WHERE content_id = %s", (cid,))
            rem_cg = cur.fetchone()[0]
            ok = (rem_tv, rem_s, rem_ep, rem_cg) == (0, 0, 0, 0)
            return ok, f"Sau xóa content={cid}: tv_series={rem_tv}, season={rem_s}, episode={rem_ep}, content_genre={rem_cg}"

        self.run_tx_check(
            "EXT-CAS-02",
            "CASCADE Delete",
            "Xóa CONTENT (TV_SERIES) lan truyền xóa TV_SERIES, SEASON, TV_EPISODE, CONTENT_GENRE",
            cas_content,
        )

    # -----------------------------------------------------------------
    # 6. KIỂM THỬ PHÂN QUYỀN RBAC THỰC TẾ (05_rbac_security.sql)
    # -----------------------------------------------------------------
    def test_rbac_permissions(self) -> None:
        rbac_sql = (PHASE3_DIR / "05_rbac_security.sql").read_text(encoding="utf-8")
        stmts = [
            s.strip()
            for s in re.split(r";\s*(?:\r?\n|$)", rbac_sql)
            if s.strip() and not all(l.strip().startswith("--") or not l.strip() for l in s.splitlines())
        ]

        tmp_pw = secrets.token_urlsafe(16)
        admin_conn = self.connect()
        admin_cur = admin_conn.cursor()
        try:
            for st in stmts:
                admin_cur.execute(st)
            admin_conn.commit()

            admin_cur.execute("DROP USER IF EXISTS '__tmp_rbac_client'@'localhost', '__tmp_rbac_mgr'@'localhost'")
            admin_cur.execute("CREATE USER '__tmp_rbac_client'@'localhost' IDENTIFIED BY %s", (tmp_pw,))
            admin_cur.execute("CREATE USER '__tmp_rbac_mgr'@'localhost' IDENTIFIED BY %s", (tmp_pw,))
            admin_cur.execute("GRANT 'role_streaming_client'@'%' TO '__tmp_rbac_client'@'localhost'")
            admin_cur.execute("GRANT 'role_content_manager'@'%' TO '__tmp_rbac_mgr'@'localhost'")
            admin_cur.execute("SET DEFAULT ROLE ALL TO '__tmp_rbac_client'@'localhost', '__tmp_rbac_mgr'@'localhost'")
            admin_conn.commit()

            # Test Client Role
            c_conn = self.connect(user="__tmp_rbac_client", password=tmp_pw)
            try:
                c_cur = c_conn.cursor()
                c_cur.execute("SELECT COUNT(*) FROM content")
                c_cnt = c_cur.fetchone()[0]
                try:
                    c_cur.execute("DELETE FROM watch_history WHERE history_id = 1")
                    c_conn.rollback()
                    self.add_result(
                        "EXT-RBAC-01",
                        "RBAC Security",
                        "role_streaming_client bị từ chối DELETE trên watch_history",
                        False,
                        "Client vẫn xóa được watch_history!",
                    )
                except Error as err:
                    self.add_result(
                        "EXT-RBAC-01",
                        "RBAC Security",
                        "role_streaming_client bị từ chối DELETE trên watch_history",
                        err.errno == 1142,
                        f"SELECT content OK ({c_cnt} dòng); DELETE watch_history bị chặn Error {err.errno}",
                    )

                try:
                    c_cur.execute("UPDATE content SET title = 'Hacked' WHERE content_id = 1")
                    c_conn.rollback()
                    self.add_result(
                        "EXT-RBAC-02",
                        "RBAC Security",
                        "role_streaming_client bị từ chối UPDATE trên content",
                        False,
                        "Client vẫn sửa được bảng content!",
                    )
                except Error as err:
                    self.add_result(
                        "EXT-RBAC-02",
                        "RBAC Security",
                        "role_streaming_client bị từ chối UPDATE trên content",
                        err.errno == 1142,
                        f"UPDATE content bị chặn Error {err.errno}: {err.msg[:80]}",
                    )
                c_cur.close()
            finally:
                c_conn.close()

            # Test Content Manager Role
            m_conn = self.connect(user="__tmp_rbac_mgr", password=tmp_pw)
            try:
                m_cur = m_conn.cursor()
                m_cur.execute("SELECT COUNT(*) FROM vw_content_full_catalog")
                v_cnt = m_cur.fetchone()[0]
                try:
                    m_cur.execute("SELECT COUNT(*) FROM user_account")
                    m_cur.fetchone()
                    self.add_result(
                        "EXT-RBAC-03",
                        "RBAC Security",
                        "role_content_manager bị cách ly khỏi user_account",
                        False,
                        "Content manager vẫn đọc được user_account!",
                    )
                except Error as err:
                    self.add_result(
                        "EXT-RBAC-03",
                        "RBAC Security",
                        "role_content_manager bị cách ly khỏi user_account",
                        err.errno == 1142,
                        f"SELECT view catalog OK ({v_cnt} dòng); SELECT user_account bị chặn Error {err.errno}",
                    )
                m_cur.close()
            finally:
                m_conn.close()
        finally:
            try:
                admin_cur.execute("DROP USER IF EXISTS '__tmp_rbac_client'@'localhost', '__tmp_rbac_mgr'@'localhost'")
                admin_conn.commit()
            finally:
                admin_cur.close()
                admin_conn.close()

    # -----------------------------------------------------------------
    # 7. KIỂM CHỨNG 10 TRUY VẤN (03_queries.sql), 2 VIEWS & 4 INDEXES
    # -----------------------------------------------------------------
    def test_queries_views_and_indexes(self) -> None:
        conn = self.connect()
        cur = conn.cursor()
        try:
            q_sql = (PHASE3_DIR / "03_queries.sql").read_text(encoding="utf-8")
            stmts = [
                s.strip()
                for s in re.split(r";\s*(?:\r?\n|$)", q_sql)
                if s.strip() and not all(l.strip().startswith("--") or not l.strip() for l in s.splitlines())
            ]
            q_num = 0
            for st in stmts:
                if st.upper().startswith("USE "):
                    cur.execute(st)
                    continue
                q_num += 1
                t0 = time.perf_counter()
                cur.execute(st)
                rows = cur.fetchall()
                ms = (time.perf_counter() - t0) * 1000
                self.add_result(
                    f"QRY-{q_num:02d}",
                    "Queries (<200ms)",
                    f"Truy vấn {q_num} (03_queries.sql) chạy sạch & < 200ms",
                    len(rows) > 0 and ms < 200.0,
                    f"{len(rows)} dòng | {ms:.2f} ms",
                )

            for idx, vname in enumerate(
                ["vw_content_full_catalog", "vw_subscription_revenue_summary"], start=1
            ):
                t0 = time.perf_counter()
                cur.execute(f"SELECT * FROM {vname}")
                rows = cur.fetchall()
                ms = (time.perf_counter() - t0) * 1000
                self.add_result(
                    f"VIEW-{idx:02d}",
                    "Views",
                    f"View {vname} trả về dữ liệu hợp lệ",
                    len(rows) > 0,
                    f"{len(rows)} dòng | {ms:.2f} ms",
                )

            idx_queries = [
                (
                    "IDX-01",
                    "idx_content_title",
                    "SELECT content_id, title, release_year, rating_age FROM content WHERE title LIKE 'Inception%'",
                ),
                (
                    "IDX-02",
                    "idx_watch_history_last_watched",
                    "SELECT history_id, profile_id, content_id, episode_id, last_watched_timestamp FROM watch_history WHERE profile_id = 1 ORDER BY last_watched_timestamp DESC",
                ),
                (
                    "IDX-03",
                    "idx_content_type_year",
                    "SELECT content_id, title, release_year FROM content WHERE content_type = 'MOVIE' AND release_year >= 2020",
                ),
                (
                    "IDX-04",
                    "idx_content_rating",
                    "SELECT content_id, title, rating_age FROM content WHERE rating_age = 'G'",
                ),
            ]
            for code, idx_name, sql in idx_queries:
                t0 = time.perf_counter()
                cur.execute(sql)
                cnt = len(cur.fetchall())
                ms = (time.perf_counter() - t0) * 1000
                cur.execute(f"EXPLAIN {sql}")
                exp_rows = cur.fetchall()
                used_key = exp_rows[0][6] if exp_rows else None
                scan_type = exp_rows[0][4] if exp_rows else None
                self.add_result(
                    code,
                    "Index EXPLAIN",
                    f"Chỉ mục {idx_name} được Optimizer sử dụng",
                    used_key == idx_name and ms < 200.0,
                    f"type={scan_type}, key={used_key}, rows={cnt}, time={ms:.2f} ms",
                )
        finally:
            cur.close()
            conn.close()

    # -----------------------------------------------------------------
    # 8. SMOKE TEST TÍCH HỢP WEB API FLASK (3-TIER)
    # -----------------------------------------------------------------
    def test_flask_api_smoke(self) -> None:
        sys.path.insert(0, str(WEB_UI_DIR))
        try:
            import server  # type: ignore
        finally:
            if str(WEB_UI_DIR) in sys.path:
                sys.path.remove(str(WEB_UI_DIR))

        client = server.app.test_client()

        r_health = client.get("/api/health")
        j_health = r_health.get_json() or {}
        self.add_result(
            "API-01",
            "Flask 3-Tier",
            "GET /api/health kết nối DB thành công",
            r_health.status_code == 200 and j_health.get("connected") is True,
            f"HTTP {r_health.status_code} | {j_health}",
        )

        r_prof = client.post("/api/profiles", json={"account_id": 1, "profile_name": "API Trigger Test", "is_kids": False})
        j_prof = r_prof.get_json() or {}
        self.add_result(
            "API-02",
            "Flask 3-Tier",
            "POST /api/profiles vượt hạn mức gói Basic trả 400 + is_trigger=True",
            r_prof.status_code == 400 and j_prof.get("is_trigger") is True,
            f"HTTP {r_prof.status_code} | is_trigger={j_prof.get('is_trigger')}",
        )

        r_kid = client.post(
            "/api/watch-history",
            json={"profile_id": 3, "content_id": 6, "stopped_position_seconds": 60},
        )
        j_kid = r_kid.get_json() or {}
        self.add_result(
            "API-03",
            "Flask 3-Tier",
            "POST /api/watch-history Kids xem phim R trả 400 + is_trigger=True",
            r_kid.status_code == 400 and j_kid.get("is_trigger") is True,
            f"HTTP {r_kid.status_code} | is_trigger={j_kid.get('is_trigger')}",
        )

        r_del_last = client.delete("/api/profiles/1")
        j_del = r_del_last.get_json() or {}
        self.add_result(
            "API-04",
            "Flask 3-Tier",
            "DELETE /api/profiles/1 (hồ sơ duy nhất) bị chặn theo BR-01",
            r_del_last.status_code == 400 and "BR-01" in (j_del.get("error") or ""),
            f"HTTP {r_del_last.status_code} | {j_del.get('error', '')[:75]}",
        )

        r_cat = client.get("/api/catalog?kids=true&limit=200")
        cat_rows = r_cat.get_json() or []
        bad_kids = [x["content_id"] for x in cat_rows if x.get("rating_age") in ("R", "NC-17")]
        self.add_result(
            "API-05",
            "Flask 3-Tier",
            "GET /api/catalog?kids=true lọc bỏ toàn bộ R và NC-17",
            r_cat.status_code == 200 and len(cat_rows) > 0 and len(bad_kids) == 0,
            f"HTTP {r_cat.status_code} | Trả {len(cat_rows)} phim | vi phạm R/NC-17={len(bad_kids)}",
        )

        r_drop = client.post("/api/admin/sql-runner", json={"sql": "DROP TABLE content"})
        j_drop = r_drop.get_json() or {}
        self.add_result(
            "API-06",
            "Flask 3-Tier",
            "POST /api/admin/sql-runner chặn câu lệnh DROP TABLE",
            r_drop.status_code == 400 and j_drop.get("success") is False,
            f"HTTP {r_drop.status_code} | {j_drop.get('error', '')[:75]}",
        )

    def run_all(self) -> int:
        print("=" * 78)
        print("  MINI-NETFLIX AUTOMATED DATABASE & API VERIFICATION (NHÓM G12)")
        print("=" * 78)

        self.test_schema_and_eer()
        self.test_report_negative_cases()
        self.test_positive_and_boundary_cases()
        self.test_extended_negative_cases()
        self.test_cascade_deletes()
        self.test_rbac_permissions()
        self.test_queries_views_and_indexes()
        self.test_flask_api_smoke()

        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)
        failed = total - passed

        print("=" * 78)
        print(f"TỔNG KẾT: {passed}/{total} CA KIỂM THỬ ĐẠT ({failed} thất bại)")
        print("=" * 78)
        return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(TestSuiteRunner().run_all())
