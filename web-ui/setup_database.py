"""
Mini-Netflix Database Setup & Connection Verification Script
Học phần: Cơ sở dữ liệu | Đồ án: #2 On-Demand Streaming Platform (Mini-Netflix) - Nhóm G12

Công dụng:
1. Kiểm tra kết nối tới MySQL Server theo cấu hình trong `.env`.
2. Tự động khởi tạo CSDL `mini_netflix` (13 Bảng, 2 Views, 2 Triggers) từ `database/01_schema.sql`
   và nạp dữ liệu mẫu từ `database/02_mock_data.sql` nếu CSDL chưa tồn tại (hoặc khi truyền cờ `--reset`).
3. Đảm bảo chỉ mục `uq_watch_history_profile_content_ep (profile_id, content_id, episode_id)` hoạt động.

Cách dùng:
  python setup_database.py          # Kiểm tra kết nối & tự động tạo CSDL nếu chưa có
  python setup_database.py --reset  # Xóa và nạp lại toàn bộ Schema + Mock Data từ đầu
"""

import os
import re
import sys
from pathlib import Path
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(dotenv_path=BASE_DIR / '.env')

DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = int(os.getenv('DB_PORT', 3306))
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '123')
DB_NAME = os.getenv('DB_NAME', 'mini_netflix')


def find_sql_file(filename: str) -> Path:
    candidates = [
        BASE_DIR / 'database' / filename,
        BASE_DIR.parent / 'database_Phase 3' / filename,
    ]
    for p in candidates:
        if p.exists():
            return p
    raise FileNotFoundError(f"Không tìm thấy file SQL: {filename}")


def execute_sql_script(cursor, sql_text: str):
    """Thực thi file SQL có hỗ trợ khối DELIMITER $$ (Triggers / Procedures)."""
    # Tách theo DELIMITER nếu có
    if 'DELIMITER $$' in sql_text:
        parts = sql_text.split('DELIMITER $$')
        # Phần trước DELIMITER $$
        normal_sql = parts[0]
        for stmt in normal_sql.split(';'):
            stmt = stmt.strip()
            if stmt:
                cursor.execute(stmt)

        for block in parts[1:]:
            if 'DELIMITER ;' in block:
                delim_part, rest_part = block.split('DELIMITER ;', 1)
            else:
                delim_part, rest_part = block, ''

            for trig_stmt in delim_part.split('$$'):
                trig_stmt = trig_stmt.strip()
                if trig_stmt:
                    cursor.execute(trig_stmt)

            for stmt in rest_part.split(';'):
                stmt = stmt.strip()
                if stmt:
                    cursor.execute(stmt)
    else:
        for stmt in sql_text.split(';'):
            stmt = stmt.strip()
            if stmt:
                cursor.execute(stmt)


def main():
    force_reset = '--reset' in sys.argv
    print("=" * 72)
    print("  MINI-NETFLIX MYSQL DATABASE SETUP & CONNECTION CHECKER (NHÓM G12)")
    print("=" * 72)
    print(f"• MySQL Host : {DB_HOST}:{DB_PORT}")
    print(f"• MySQL User : {DB_USER}")
    print(f"• Database   : {DB_NAME}")
    print("-" * 72)

    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            charset='utf8mb4',
            use_unicode=True
        )
        cursor = conn.cursor()
        print("[OK] Kết nối tới MySQL Server thành công!")

        cursor.execute("SHOW DATABASES LIKE %s;", (DB_NAME,))
        db_exists = cursor.fetchone() is not None

        if force_reset or not db_exists:
            action_label = "TÁI KHỞI TẠO (--reset)" if force_reset else "KHỞI TẠO MỚI"
            print(f"[INFO] Đang {action_label} cơ sở dữ liệu `{DB_NAME}`...")

            schema_path = find_sql_file('01_schema.sql')
            mock_path = find_sql_file('02_mock_data.sql')

            print(f"  -> Đang chạy Schema DDL: {schema_path.name}")
            execute_sql_script(cursor, schema_path.read_text(encoding='utf-8'))
            conn.commit()

            print(f"  -> Đang nạp Mock Data DML: {mock_path.name}")
            execute_sql_script(cursor, mock_path.read_text(encoding='utf-8'))
            conn.commit()
            print(f"[OK] Đã khởi tạo xong Schema & Dữ liệu mẫu cho `{DB_NAME}`!")
        else:
            print(f"[INFO] Cơ sở dữ liệu `{DB_NAME}` đã tồn tại. Đang kiểm tra cấu trúc...")

        cursor.execute(f"USE `{DB_NAME}`;")

        # Đảm bảo index uq_watch_history_profile_content_ep tồn tại cho tính năng lưu tiến trình từng tập
        cursor.execute("SHOW INDEX FROM watch_history WHERE Key_name = 'uq_watch_history_profile_content';")
        if cursor.fetchall():
            print("[INFO] Đang nâng cấp Unique Index trên `watch_history` sang (profile_id, content_id, episode_id)...")
            cursor.execute("""
                ALTER TABLE watch_history
                DROP INDEX uq_watch_history_profile_content,
                ADD UNIQUE INDEX uq_watch_history_profile_content_ep (profile_id, content_id, episode_id);
            """)
            conn.commit()

        # Thống kê 13 bảng, 2 views, 2 triggers
        cursor.execute("SHOW FULL TABLES WHERE Table_type = 'BASE TABLE';")
        tables = [row[0] for row in cursor.fetchall()]

        cursor.execute("SHOW FULL TABLES WHERE Table_type = 'VIEW';")
        views = [row[0] for row in cursor.fetchall()]

        cursor.execute("SHOW TRIGGERS;")
        triggers = [row[0] for row in cursor.fetchall()]

        print("-" * 72)
        print(f"• Số lượng Bảng (Base Tables) : {len(tables)} / 13 bảng ({', '.join(tables)})")
        print(f"• Số lượng Khung nhìn (Views) : {len(views)} / 2 views ({', '.join(views)})")
        print(f"• Số lượng Triggers           : {len(triggers)} / 2 triggers ({', '.join(triggers)})")
        print("=" * 72)
        print("[HOÀN TẤT] Hệ thống CSDL Mini-Netflix đã sẵn sàng! Chạy `python server.py` để mở Web.")

        cursor.close()
        conn.close()

    except Error as err:
        print(f"[LỖI MYSQL] Không thể kết nối hoặc thực thi SQL: {err}")
        print("Hãy kiểm tra lại thông số DB_HOST, DB_PORT, DB_USER, DB_PASSWORD trong file `.env`!")
        sys.exit(1)


if __name__ == '__main__':
    main()
