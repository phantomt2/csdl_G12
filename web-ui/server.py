import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

"""
Mini-Netflix Backend Server (REST API)
Học phần: Cơ sở dữ liệu | Đồ án: #2 On-Demand Streaming Platform (Mini-Netflix) - Nhóm G12
Kiến trúc: 3-Tier Architecture (Client: HTML/TailwindCSS/JS <-> Server: Flask API <-> MySQL mini_netflix)
"""

import os
import re
import time
import decimal
import datetime
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory, render_template

import mysql.connector
from mysql.connector import Error

# Tải cấu hình từ file .env
env_path = Path(__file__).resolve().parent / '.env'
load_dotenv(dotenv_path=env_path)

BASE_DIR = Path(__file__).resolve().parent
templates_dir = BASE_DIR / 'templates'
static_dir = BASE_DIR / 'static'

app = Flask(
    __name__,
    template_folder=str(templates_dir) if templates_dir.exists() else str(BASE_DIR),
    static_folder=str(static_dir) if static_dir.exists() else str(BASE_DIR),
    static_url_path=''
)

# Cấu hình CSDL
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', '123'),
    'database': os.getenv('DB_NAME', 'mini_netflix'),
    'charset': 'utf8mb4',
    'use_unicode': True
}

# Hỗ trợ CORS tự nhiên không cần cài thêm thư viện ngoài
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE,PATCH,OPTIONS'
    return response

def serialize_data(obj):
    """Chuyển đổi kiểu dữ liệu MySQL (Decimal, Date, Datetime) sang JSON an toàn."""
    if isinstance(obj, (datetime.date, datetime.datetime)):
        return obj.isoformat()
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    return obj

def get_db_connection():
    """Tạo kết nối mới tới MySQL mini_netflix."""
    return mysql.connector.connect(**DB_CONFIG)

def query(sql, params=()):
    """Thực thi câu lệnh SELECT và trả về danh sách dict chuẩn JSON."""
    conn = get_db_connection()
    try:
        cur = conn.cursor(dictionary=True)
        if params:
            cur.execute(sql, params)
        else:
            cur.execute(sql)
        rows = cur.fetchall()
        # Chuyển đổi Decimal và Date sang định dạng JSON serialize được
        cleaned_rows = [
            {k: serialize_data(v) for k, v in row.items()}
            for row in rows
        ]
        return cleaned_rows
    finally:
        cur.close()
        conn.close()

def execute(sql, params=()):
    """Thực thi INSERT / UPDATE / DELETE. Bắt chính xác lỗi từ Trigger MySQL (SQLSTATE 45000 / Error 1644)."""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        if params:
            cur.execute(sql, params)
        else:
            cur.execute(sql)
        conn.commit()
        last_id = cur.lastrowid
        return True, "Thao tác thành công!", last_id
    except Error as err:
        conn.rollback()
        # Bắt thông điệp Trigger MySQL (trg_check_profile_limit, trg_check_kids_rating)
        is_trigger = (err.sqlstate == '45000' or err.errno == 1644)
        error_info = {
            "msg": err.msg,
            "errno": err.errno,
            "sqlstate": err.sqlstate,
            "is_trigger": is_trigger
        }
        return False, error_info, None
    finally:
        cur.close()
        conn.close()

def ensure_watch_history_episode_index():
    """Đảm bảo bảng watch_history hỗ trợ lưu tiến trình riêng biệt cho từng episode_id của TV_SERIES."""
    try:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SHOW INDEX FROM watch_history WHERE Key_name = 'uq_watch_history_profile_content';")
        if cur.fetchall():
            cur.execute("""
                ALTER TABLE watch_history
                DROP INDEX uq_watch_history_profile_content,
                ADD UNIQUE INDEX uq_watch_history_profile_content_ep (profile_id, content_id, episode_id);
            """)
            conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Lưu ý: Không thể cập nhật chỉ mục watch_history: {e}")

# Tự động đảm bảo chỉ mục khi nạp máy chủ
ensure_watch_history_episode_index()


# =====================================================================
# 1. SERVE GIAO DIỆN NETFLIX (FRONTEND)
# =====================================================================
@app.route('/')
def serve_index():
    if (templates_dir / 'index.html').exists():
        return render_template('index.html')
    if (static_dir / 'index.html').exists():
        return send_from_directory(str(static_dir), 'index.html')
    if (BASE_DIR / 'index.html').exists():
        return send_from_directory(str(BASE_DIR), 'index.html')
    return "<h1>Mini-Netflix UI: index.html chưa sẵn sàng</h1>", 404

@app.route('/admin')
def serve_admin():
    if (templates_dir / 'admin.html').exists():
        return render_template('admin.html')
    if (static_dir / 'admin.html').exists():
        return send_from_directory(str(static_dir), 'admin.html')
    if (BASE_DIR / 'admin.html').exists():
        return send_from_directory(str(BASE_DIR), 'admin.html')
    return "<h1>Mini-Netflix Admin Console: admin.html chưa sẵn sàng</h1>", 404

@app.route('/api/health')
def health_check():
    try:
        conn = get_db_connection()
        conn.close()
        return jsonify({"status": "healthy", "database": DB_CONFIG['database'], "connected": True})
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e), "connected": False}), 500


# =====================================================================
# 2. API TÀI KHOẢN & ĐĂNG NHẬP (AUTH & USER ACCOUNT)
# =====================================================================
@app.route('/api/accounts', methods=['GET'])
def get_accounts():
    """Lấy danh sách các tài khoản để dễ dàng chuyển đổi demo giữa các gói cước (Basic/Standard/Premium)."""
    sql = """
        SELECT
            ua.account_id,
            ua.email,
            ua.registration_date,
            ua.account_status,
            st.tier_id,
            st.tier_name,
            st.monthly_price,
            st.max_profiles_allowed,
            st.max_concurrent_streams,
            st.resolution,
            COUNT(p.profile_id) AS current_profile_count
        FROM user_account ua
        INNER JOIN subscription_tier st ON ua.tier_id = st.tier_id
        LEFT JOIN profile p ON ua.account_id = p.account_id
        GROUP BY ua.account_id, ua.email, ua.registration_date, ua.account_status,
                 st.tier_id, st.tier_name, st.monthly_price, st.max_profiles_allowed,
                 st.max_concurrent_streams, st.resolution
        ORDER BY ua.account_id ASC;
    """
    return jsonify(query(sql))

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json or {}
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()
    
    if not email:
        return jsonify({"success": False, "error": "Vui lòng nhập địa chỉ Email."}), 400
        
    sql = """
        SELECT ua.account_id, ua.email, ua.password_hash, ua.account_status,
               st.tier_id, st.tier_name, st.max_profiles_allowed, st.resolution
        FROM user_account ua
        INNER JOIN subscription_tier st ON ua.tier_id = st.tier_id
        WHERE ua.email = %s;
    """
    acc = query(sql, (email,))
    if not acc:
        return jsonify({"success": False, "error": "Email không tồn tại trong hệ thống. Nếu bạn chưa có tài khoản, vui lòng bấm 'Đăng ký ngay'!"}), 404
        
    user = acc[0]
    if user['account_status'] != 'ACTIVE':
        return jsonify({
            "success": False,
            "error": f"Tài khoản của bạn đang ở trạng thái {user['account_status']} (Bị khóa). Vui lòng liên hệ quản trị viên để mở khóa!"
        }), 403
        
    # Xác định quyền Admin
    is_admin = (user['email'].lower() == 'admin@netflix.com' or 'admin' in user['email'].lower())
    
    # Lấy danh sách hồ sơ con (Profiles) của tài khoản
    profiles_sql = """
        SELECT profile_id, account_id, profile_name, avatar_url, is_kids, created_at
        FROM profile
        WHERE account_id = %s
        ORDER BY profile_id ASC;
    """
    profiles = query(profiles_sql, (user['account_id'],))
    
    user_info = {
        'account_id': user['account_id'],
        'email': user['email'],
        'account_status': user['account_status'],
        'tier_id': user['tier_id'],
        'tier_name': user['tier_name'],
        'max_profiles_allowed': user['max_profiles_allowed'],
        'resolution': user['resolution'],
        'is_admin': is_admin,
        'profiles': profiles
    }
    
    return jsonify({
        "success": True, 
        "account": user_info,
        "is_admin": is_admin,
        "redirect": "/admin" if is_admin else "/",
        "message": "Đăng nhập thành công!"
    })

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Đăng ký tài khoản mới: Bắt buộc ghi trực tiếp vào MySQL (user_account + profile)."""
    data = request.json or {}
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()
    tier_id = data.get('tier_id', 1)
    profile_name = data.get('profile_name', 'Người xem chính').strip() or 'Người xem chính'
    is_kids = bool(data.get('is_kids', False))
    avatar_url = data.get('avatar_url') or (
        "https://images.unsplash.com/photo-1566492031773-4f4e44671857?w=150" if is_kids 
        else "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150"
    )

    if not email:
        return jsonify({"success": False, "error": "Vui lòng nhập địa chỉ Email."}), 400
    if not password:
        return jsonify({"success": False, "error": "Vui lòng nhập Mật khẩu bảo mật."}), 400
    if '@' not in email or '.' not in email:
        return jsonify({"success": False, "error": "Định dạng Email không hợp lệ (ví dụ: user@example.com)."}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"success": False, "error": "Không thể kết nối đến máy chủ CSDL MySQL."}), 500

    try:
        cursor = conn.cursor(dictionary=True)
        # Kiểm tra trùng email
        cursor.execute("SELECT account_id FROM user_account WHERE email = %s;", (email,))
        if cursor.fetchone():
            return jsonify({"success": False, "error": "Địa chỉ Email này đã được đăng ký. Vui lòng đăng nhập hoặc sử dụng Email khác!"}), 400

        # Kiểm tra gói cước
        cursor.execute("SELECT tier_id, tier_name, max_profiles_allowed, resolution FROM subscription_tier WHERE tier_id = %s;", (tier_id,))
        tier = cursor.fetchone()
        if not tier:
            tier_id = 1
            cursor.execute("SELECT tier_id, tier_name, max_profiles_allowed, resolution FROM subscription_tier WHERE tier_id = 1;")
            tier = cursor.fetchone()

        # Thêm tài khoản mới vào bảng user_account
        password_hash = f"$2b$12${password}Hashed"
        cursor.execute("""
            INSERT INTO user_account (email, password_hash, registration_date, account_status, tier_id)
            VALUES (%s, %s, CURDATE(), 'ACTIVE', %s);
        """, (email, password_hash, tier_id))
        new_account_id = cursor.lastrowid

        # Thêm hồ sơ ban đầu vào bảng profile (Trigger trg_check_profile_limit_before_insert sẽ tự kiểm tra)
        cursor.execute("""
            INSERT INTO profile (account_id, profile_name, avatar_url, is_kids)
            VALUES (%s, %s, %s, %s);
        """, (new_account_id, profile_name, avatar_url, 1 if is_kids else 0))
        new_profile_id = cursor.lastrowid

        conn.commit()

        user_info = {
            'account_id': new_account_id,
            'email': email,
            'account_status': 'ACTIVE',
            'tier_id': tier['tier_id'],
            'tier_name': tier['tier_name'],
            'max_profiles_allowed': tier['max_profiles_allowed'],
            'resolution': tier['resolution'],
            'is_admin': False,
            'profiles': [{
                'profile_id': new_profile_id,
                'account_id': new_account_id,
                'profile_name': profile_name,
                'avatar_url': avatar_url,
                'is_kids': is_kids
            }]
        }

        return jsonify({
            "success": True,
            "message": "Đăng ký tài khoản thành công! Dữ liệu đã được cập nhật vào CSDL.",
            "account": user_info,
            "is_admin": False,
            "redirect": "/"
        }), 201

    except mysql.connector.Error as err:
        conn.rollback()
        if err.errno == 1644 or err.sqlstate == '45000':
            return jsonify({"success": False, "error": f"Ràng buộc CSDL: {err.msg}"}), 400
        return jsonify({"success": False, "error": f"Lỗi CSDL MySQL ({err.errno}): {err.msg}"}), 400
    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        conn.close()


# =====================================================================
# 3. API QUẢN LÝ HỒ SƠ CON (PROFILE - BR-01, BR-02, FR-02)
# =====================================================================
@app.route('/api/profiles', methods=['GET'])
def get_profiles():
    account_id = request.args.get('account_id', type=int)
    if not account_id:
        return jsonify({"error": "Thiếu tham số account_id"}), 400
        
    sql = """
        SELECT profile_id, account_id, profile_name, avatar_url, is_kids, created_at
        FROM profile
        WHERE account_id = %s
        ORDER BY profile_id ASC;
    """
    return jsonify(query(sql, (account_id,)))

@app.route('/api/profiles', methods=['POST'])
def create_profile():
    """Tạo hồ sơ mới. Kích hoạt TRIGGER trg_check_profile_limit_before_insert nếu vượt hạn mức gói cước."""
    data = request.json or {}
    account_id = data.get('account_id')
    profile_name = data.get('profile_name', '').strip()
    is_kids = bool(data.get('is_kids', False))
    avatar_url = data.get('avatar_url') or (
        "https://images.unsplash.com/photo-1566492031773-4f4e44671857?w=150" if is_kids 
        else "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150"
    )

    if not account_id or not profile_name:
        return jsonify({"success": False, "error": "Vui lòng nhập đầy đủ account_id và tên hồ sơ."}), 400

    sql = """
        INSERT INTO profile (account_id, profile_name, avatar_url, is_kids)
        VALUES (%s, %s, %s, %s);
    """
    ok, err_or_msg, new_id = execute(sql, (account_id, profile_name, avatar_url, is_kids))
    if ok:
        return jsonify({"success": True, "message": "Khởi tạo hồ sơ thành công!", "profile_id": new_id}), 201
    
    # Bắt lỗi từ Trigger BR-01/FR-02
    return jsonify({
        "success": False,
        "error": err_or_msg["msg"],
        "is_trigger": err_or_msg["is_trigger"],
        "rule": "BR-01 / FR-02: Giới hạn số lượng Profile theo gói cước"
    }), 400

@app.route('/api/profiles/<int:profile_id>', methods=['DELETE'])
def delete_profile(profile_id):
    """Xóa hồ sơ. Kiểm tra BR-01: Mỗi tài khoản phải duy trì tối thiểu 1 hồ sơ (1..N). Không thể xóa hồ sơ cuối cùng."""
    cnt_check = query(
        "SELECT COUNT(*) AS cnt FROM profile WHERE account_id = (SELECT account_id FROM profile WHERE profile_id = %s);",
        (profile_id,)
    )
    if not cnt_check or cnt_check[0]['cnt'] <= 1:
        return jsonify({
            "success": False,
            "error": "Vi phạm BR-01: Mỗi tài khoản phải duy trì tối thiểu 1 hồ sơ (1..N). Không thể xóa hồ sơ cuối cùng!"
        }), 400

    sql = "DELETE FROM profile WHERE profile_id = %s;"
    ok, err_or_msg, _ = execute(sql, (profile_id,))
    if ok:
        return jsonify({"success": True, "message": "Đã xóa hồ sơ thành công!", "profile_id": profile_id})
    return jsonify({"success": False, "error": err_or_msg["msg"]}), 400

@app.route('/api/profiles/<int:profile_id>', methods=['PUT'])
def update_profile(profile_id):
    """Cập nhật thông tin hồ sơ (profile_name, is_kids, avatar_url) - FR-02."""
    data = request.json or {}
    profile_name = data.get('profile_name')
    is_kids = data.get('is_kids')
    avatar_url = data.get('avatar_url')

    existing = query("SELECT profile_id, profile_name, is_kids, avatar_url FROM profile WHERE profile_id = %s;", (profile_id,))
    if not existing:
        return jsonify({"success": False, "error": f"Không tìm thấy hồ sơ với ID {profile_id}"}), 404

    cur_p = existing[0]
    new_name = profile_name.strip() if (profile_name is not None and str(profile_name).strip()) else cur_p['profile_name']
    new_is_kids = int(bool(is_kids)) if is_kids is not None else cur_p['is_kids']
    new_avatar = avatar_url if avatar_url is not None else cur_p['avatar_url']

    sql = """
        UPDATE profile
        SET profile_name = %s,
            is_kids = %s,
            avatar_url = %s
        WHERE profile_id = %s;
    """
    ok, err_or_msg, _ = execute(sql, (new_name, new_is_kids, new_avatar, profile_id))
    if ok:
        return jsonify({
            "success": True,
            "message": "Cập nhật hồ sơ thành công!",
            "profile_id": profile_id
        })
    return jsonify({"success": False, "error": err_or_msg["msg"]}), 400


# =====================================================================
# 4. API DANH MỤC PHIM & NỘI DUNG (CATALOG & METADATA - FR-03, FR-06)
# =====================================================================
@app.route('/api/catalog', methods=['GET'])
def get_catalog():
    search = request.args.get('q', '').strip()
    genre = request.args.get('genre', '').strip()
    genres_param = request.args.get('genres', '').strip()
    ctype = request.args.get('type', '').strip().upper()
    lang = request.args.get('lang', '').strip()
    is_kids = request.args.get('kids', 'false').lower() == 'true'
    resolution = request.args.get('resolution', '').strip()
    limit = request.args.get('limit', 60, type=int)

    sql = """
        SELECT
            v.content_id,
            v.title,
            v.content_type,
            v.release_year,
            v.rating_age,
            v.original_language,
            v.genres,
            v.movie_duration_mins,
            v.movie_resolution,
            v.series_total_seasons,
            v.series_status,
            c.description,
            c.language_code
        FROM vw_content_full_catalog v
        INNER JOIN content c ON v.content_id = c.content_id
        WHERE 1=1
    """
    params = []

    if search:
        sql += " AND (v.title LIKE %s OR c.description LIKE %s)"
        params.extend([f"%{search}%", f"%{search}%"])

    # BR-09: Tự động loại bỏ nội dung R / NC-17 đối với hồ sơ Trẻ em
    if is_kids:
        sql += " AND v.rating_age NOT IN ('R', 'NC-17')"

    # Hỗ trợ lọc nhiều thể loại (Multi-Genre Filtering) từ 'genres' hoặc 'genre'
    raw_genre_str = genres_param if genres_param else genre
    selected_genres = [g.strip() for g in raw_genre_str.split(',') if g.strip()]
    for g in selected_genres:
        sql += " AND v.genres LIKE %s"
        params.append(f"%{g}%")

    if ctype in ('MOVIE', 'TV_SERIES'):
        sql += " AND v.content_type = %s"
        params.append(ctype)

    if lang:
        sql += " AND c.language_code = %s"
        params.append(lang)

    if resolution:
        sql += " AND v.movie_resolution = %s"
        params.append(resolution)

    sql += " ORDER BY v.release_year DESC, v.title ASC LIMIT %s;"
    params.append(limit)

    return jsonify(query(sql, tuple(params)))

@app.route('/api/content/<int:content_id>', methods=['GET'])
def get_content_detail(content_id):
    sql = """
        SELECT
            v.*,
            c.description,
            c.language_code
        FROM vw_content_full_catalog v
        INNER JOIN content c ON v.content_id = c.content_id
        WHERE v.content_id = %s;
    """
    items = query(sql, (content_id,))
    if not items:
        return jsonify({"error": "Không tìm thấy nội dung yêu cầu."}), 404
        
    item = items[0]
    profile_id = request.args.get('profile_id', type=int)

    # Nếu là TV_SERIES, truy vấn thêm phân cấp Seasons và Episodes (BR-04, BR-08)
    if item['content_type'] == 'TV_SERIES':
        seasons_sql = """
            SELECT s.season_id, s.season_number, s.season_name, s.release_date
            FROM season s
            WHERE s.content_id = %s
            ORDER BY s.season_number ASC;
        """
        seasons = query(seasons_sql, (content_id,))
        for s in seasons:
            episodes_sql = """
                SELECT episode_id, episode_number, episode_title, duration_minutes
                FROM tv_episode
                WHERE season_id = %s
                ORDER BY episode_number ASC;
            """
            s['episodes'] = query(episodes_sql, (s['season_id'],))
        item['seasons'] = seasons

        # Lấy lịch sử xem theo từng tập nếu có profile_id
        ep_history_map = {}
        rows = []
        if profile_id:
            rows = query(
                "SELECT * FROM watch_history WHERE profile_id = %s AND content_id = %s ORDER BY last_watched_timestamp DESC;",
                (profile_id, content_id)
            )
            ep_history_map = {r['episode_id']: r for r in rows if r.get('episode_id')}

        item['user_watch_history'] = rows[0] if rows else None

        total_episodes = 0
        completed_episodes = 0
        for s in seasons:
            for ep in s.get('episodes', []):
                total_episodes += 1
                history_entry = ep_history_map.get(ep['episode_id'])
                stopped_sec = (
                    history_entry['stopped_position_seconds']
                    if history_entry and history_entry.get('stopped_position_seconds') is not None
                    else 0
                )
                dur_minutes = ep.get('duration_minutes') or 1
                is_completed = bool(stopped_sec >= dur_minutes * 60)
                ep['stopped_position_seconds'] = stopped_sec
                ep['is_episode_completed'] = is_completed
                if is_completed:
                    completed_episodes += 1

        item['series_total_episodes'] = total_episodes
        item['series_completed_episodes'] = completed_episodes
        item['series_all_completed'] = bool(total_episodes > 0 and completed_episodes >= total_episodes)
    else:
        # MOVIE
        rows = []
        if profile_id:
            rows = query(
                "SELECT * FROM watch_history WHERE profile_id = %s AND content_id = %s ORDER BY last_watched_timestamp DESC;",
                (profile_id, content_id)
            )
        item['user_watch_history'] = rows[0] if rows else None
        
    return jsonify(item)

@app.route('/api/genres', methods=['GET'])
def get_genres():
    return jsonify(query("SELECT genre_id, genre_name FROM genre ORDER BY genre_name ASC;"))

@app.route('/api/languages', methods=['GET'])
def get_languages():
    return jsonify(query("SELECT language_code, language_name FROM language ORDER BY language_name ASC;"))

@app.route('/api/tiers', methods=['GET'])
def get_tiers():
    return jsonify(query("SELECT * FROM subscription_tier ORDER BY tier_id ASC;"))


# =====================================================================
# 5. API DANH SÁCH XEM SAU (WATCHLIST - BR-07, FR-04)
# =====================================================================
@app.route('/api/watchlist', methods=['GET'])
def get_watchlist():
    profile_id = request.args.get('profile_id', type=int)
    if not profile_id:
        return jsonify({"error": "Thiếu tham số profile_id"}), 400
        
    sql = """
        SELECT
            w.content_id,
            w.added_at,
            v.title,
            v.content_type,
            v.release_year,
            v.rating_age,
            v.genres,
            v.movie_duration_mins,
            v.movie_resolution,
            v.series_total_seasons
        FROM watchlist w
        INNER JOIN vw_content_full_catalog v ON w.content_id = v.content_id
        WHERE w.profile_id = %s
        ORDER BY w.added_at DESC;
    """
    return jsonify(query(sql, (profile_id,)))

@app.route('/api/watchlist', methods=['POST'])
def add_to_watchlist():
    data = request.json or {}
    profile_id = data.get('profile_id')
    content_id = data.get('content_id')
    
    if not profile_id or not content_id:
        return jsonify({"error": "Thiếu profile_id hoặc content_id"}), 400

    sql = "INSERT INTO watchlist (profile_id, content_id, added_at) VALUES (%s, %s, NOW());"
    ok, err_or_msg, _ = execute(sql, (profile_id, content_id))
    if ok:
        return jsonify({"success": True, "message": "Đã thêm vào danh sách xem sau!"}), 201
    return jsonify({"success": False, "error": err_or_msg["msg"]}), 400

@app.route('/api/watchlist', methods=['DELETE'])
def remove_from_watchlist():
    data = request.json or {}
    profile_id = data.get('profile_id')
    content_id = data.get('content_id')
    
    sql = "DELETE FROM watchlist WHERE profile_id = %s AND content_id = %s;"
    ok, err_or_msg, _ = execute(sql, (profile_id, content_id))
    if ok:
        return jsonify({"success": True, "message": "Đã xóa khỏi danh sách xem sau!"})
    return jsonify({"success": False, "error": err_or_msg["msg"]}), 400


# =====================================================================
# 6. API TIẾN TRÌNH & LỊCH SỬ XEM (WATCH HISTORY - BR-06, BR-09, FR-05)
# =====================================================================
@app.route('/api/watch-history', methods=['GET'])
def get_watch_history():
    profile_id = request.args.get('profile_id', type=int)
    if not profile_id:
        return jsonify({"error": "Thiếu tham số profile_id"}), 400

    sql = """
        SELECT
            wh.history_id,
            wh.profile_id,
            wh.content_id,
            wh.episode_id,
            wh.last_watched_timestamp,
            wh.stopped_position_seconds,
            wh.is_completed,
            c.title,
            c.content_type,
            c.rating_age,
            m.duration_minutes AS movie_duration,
            ep.duration_minutes AS episode_duration,
            COALESCE(
                CONCAT('Mùa ', s.season_number, ' - Tập ', ep.episode_number, ': ', ep.episode_title),
                'Phim điện ảnh'
            ) AS current_episode_info
        FROM watch_history wh
        INNER JOIN content c ON wh.content_id = c.content_id
        LEFT JOIN movie m ON c.content_id = m.content_id
        LEFT JOIN tv_episode ep ON wh.episode_id = ep.episode_id
        LEFT JOIN season s ON ep.season_id = s.season_id
        WHERE wh.profile_id = %s
        ORDER BY wh.last_watched_timestamp DESC;
    """
    return jsonify(query(sql, (profile_id,)))

@app.route('/api/watch-history', methods=['POST'])
def save_watch_history():
    """Lưu tiến trình xem. TRIGGER trg_check_kids_rating_before_watch sẽ CHẶN nếu Kids xem phim R/NC-17!"""
    data = request.json or {}
    profile_id = data.get('profile_id')
    content_id = data.get('content_id')
    episode_id = data.get('episode_id') # Có thể None nếu là MOVIE
    raw_stopped_sec = data.get('stopped_position_seconds', 0)
    req_is_completed = bool(data.get('is_completed', False))
    mark_episode_completed = bool(data.get('mark_episode_completed', False))

    if not profile_id or not content_id:
        return jsonify({"success": False, "error": "Thiếu profile_id hoặc content_id"}), 400

    try:
        stopped_sec = int(float(raw_stopped_sec))
    except (ValueError, TypeError):
        stopped_sec = 0

    conn = get_db_connection()
    try:
        cur = conn.cursor(dictionary=True)

        # 1. Tra cứu loại nội dung (content_type)
        cur.execute("SELECT content_id, content_type FROM content WHERE content_id = %s;", (content_id,))
        content_row = cur.fetchone()
        if not content_row:
            return jsonify({"success": False, "error": "Không tìm thấy nội dung yêu cầu."}), 404

        content_type = content_row['content_type']

        if content_type == 'MOVIE':
            # Phim lẻ: Lấy duration_minutes từ movie (mặc định 120)
            cur.execute("SELECT duration_minutes FROM movie WHERE content_id = %s;", (content_id,))
            movie_row = cur.fetchone()
            dur_mins = movie_row['duration_minutes'] if (movie_row and movie_row.get('duration_minutes')) else 120
            max_sec = dur_mins * 60

            # Giới hạn stopped_sec trong [0, max_sec]
            stopped_sec = max(0, min(stopped_sec, max_sec))

            # Xử lý hoàn tất phim
            if req_is_completed:
                stopped_sec = max_sec

            is_completed_val = bool(req_is_completed or stopped_sec >= max_sec)
            if is_completed_val:
                stopped_sec = max_sec

            # Xóa bản ghi cũ trong transaction để câu INSERT luôn kích hoạt trigger trg_check_kids_rating_before_watch
            cur.execute("DELETE FROM watch_history WHERE profile_id = %s AND content_id = %s;", (profile_id, content_id))

            insert_sql = """
                INSERT INTO watch_history (profile_id, content_id, episode_id, last_watched_timestamp, stopped_position_seconds, is_completed)
                VALUES (%s, %s, NULL, NOW(), %s, %s);
            """
            cur.execute(insert_sql, (profile_id, content_id, stopped_sec, 1 if is_completed_val else 0))
            new_hid = cur.lastrowid
            conn.commit()

            return jsonify({
                "success": True,
                "message": "Đã hoàn tất phim điện ảnh!" if is_completed_val else "Đã cập nhật tiến trình xem phim thành công!",
                "history_id": new_hid,
                "stopped_position_seconds": stopped_sec,
                "max_duration_seconds": max_sec,
                "is_completed": is_completed_val
            })

        else:
            # TV_SERIES
            # Nếu episode_id không truyền, tìm tập đầu tiên của series
            if not episode_id:
                cur.execute("""
                    SELECT ep.episode_id, ep.duration_minutes
                    FROM tv_episode ep
                    INNER JOIN season s ON ep.season_id = s.season_id
                    WHERE s.content_id = %s
                    ORDER BY s.season_number ASC, ep.episode_number ASC
                    LIMIT 1;
                """, (content_id,))
                first_ep = cur.fetchone()
                if first_ep:
                    episode_id = first_ep['episode_id']

            # Lấy thời lượng của tập phim (mặc định 45 phút)
            if episode_id:
                cur.execute("SELECT duration_minutes FROM tv_episode WHERE episode_id = %s;", (episode_id,))
                ep_row = cur.fetchone()
                dur_mins = ep_row['duration_minutes'] if (ep_row and ep_row.get('duration_minutes')) else 45
            else:
                dur_mins = 45

            max_sec = dur_mins * 60
            stopped_sec = max(0, min(stopped_sec, max_sec))

            # Xác định tập hiện tại có hoàn thành không
            this_ep_completed = bool(mark_episode_completed or stopped_sec >= max_sec)
            if this_ep_completed:
                stopped_sec = max_sec

            # Lấy tổng số tập của series và thời lượng từng tập
            cur.execute("""
                SELECT ep.episode_id, ep.duration_minutes
                FROM tv_episode ep
                INNER JOIN season s ON ep.season_id = s.season_id
                WHERE s.content_id = %s;
            """, (content_id,))
            all_eps = cur.fetchall()
            total_eps = len(all_eps)
            ep_dur_map = {row['episode_id']: (row['duration_minutes'] or 45) * 60 for row in all_eps}

            # Lấy danh sách episodes_progress gửi từ client nếu có
            episodes_progress = data.get('episodes_progress')

            # Nếu client gửi kèm episodes_progress (mảng các tập đã xem trong memory)
            if isinstance(episodes_progress, list) and len(episodes_progress) > 0:
                # Đảm bảo tập hiện tại có trong danh sách với stopped_sec chính xác
                cur_in_list = False
                for ep_item in episodes_progress:
                    if ep_item.get('episode_id') == episode_id:
                        ep_item['stopped_position_seconds'] = stopped_sec
                        cur_in_list = True
                        break
                if not cur_in_list and episode_id:
                    episodes_progress.append({'episode_id': episode_id, 'stopped_position_seconds': stopped_sec})

                new_hid = None
                for ep_item in episodes_progress:
                    e_id = ep_item.get('episode_id')
                    if not e_id or e_id not in ep_dur_map:
                        continue
                    try:
                        e_sec = int(float(ep_item.get('stopped_position_seconds', 0)))
                    except (ValueError, TypeError):
                        e_sec = 0
                    e_max = ep_dur_map[e_id]
                    e_sec = max(0, min(e_sec, e_max))

                    cur.execute("""
                        DELETE FROM watch_history
                        WHERE profile_id = %s AND content_id = %s AND (episode_id = %s OR episode_id IS NULL);
                    """, (profile_id, content_id, e_id))

                    cur.execute("""
                        INSERT INTO watch_history (profile_id, content_id, episode_id, last_watched_timestamp, stopped_position_seconds, is_completed)
                        VALUES (%s, %s, %s, NOW(), %s, 0);
                    """, (profile_id, content_id, e_id, e_sec))
                    if e_id == episode_id or new_hid is None:
                        new_hid = cur.lastrowid

            else:
                # Fallback: Chỉ lưu tập hiện tại (episode_id)
                if episode_id:
                    cur.execute("""
                        DELETE FROM watch_history
                        WHERE profile_id = %s AND content_id = %s AND (episode_id = %s OR episode_id IS NULL);
                    """, (profile_id, content_id, episode_id))
                else:
                    cur.execute("""
                        DELETE FROM watch_history
                        WHERE profile_id = %s AND content_id = %s AND episode_id IS NULL;
                    """, (profile_id, content_id))

                cur.execute("""
                    INSERT INTO watch_history (profile_id, content_id, episode_id, last_watched_timestamp, stopped_position_seconds, is_completed)
                    VALUES (%s, %s, %s, NOW(), %s, 0);
                """, (profile_id, content_id, episode_id, stopped_sec))
                new_hid = cur.lastrowid

            # Đếm số tập đã xem 100% trong watch_history (cả các tập vừa insert và các tập đã xem trước đó)
            cur.execute("""
                SELECT episode_id, stopped_position_seconds
                FROM watch_history
                WHERE profile_id = %s AND content_id = %s AND episode_id IS NOT NULL;
            """, (profile_id, content_id))
            all_watched_rows = cur.fetchall()
            completed_eps_count = 0
            for r in all_watched_rows:
                target_dur = ep_dur_map.get(r['episode_id'], 45 * 60)
                if (r.get('stopped_position_seconds') or 0) >= target_dur:
                    completed_eps_count += 1

            all_episodes_done = bool(total_eps > 0 and completed_eps_count >= total_eps)

            # Nếu yêu cầu is_completed = True cho cả Series nhưng chưa xem hết tất cả các tập
            if req_is_completed and not all_episodes_done and total_eps > 1:
                conn.rollback()
                return jsonify({
                    "success": False,
                    "error": f"Chưa thể đánh dấu hoàn tất toàn bộ Series! Bạn mới xem hết {completed_eps_count}/{total_eps} tập. Bắt buộc phải xem hết 100% tất cả các mùa và tập mới được đánh dấu is_completed = TRUE.",
                    "is_trigger": False
                }), 400

            # Cập nhật trạng thái is_completed đồng bộ cho các tập của series
            if all_episodes_done:
                cur.execute("UPDATE watch_history SET is_completed = 1 WHERE profile_id = %s AND content_id = %s;", (profile_id, content_id))
            else:
                cur.execute("UPDATE watch_history SET is_completed = 0 WHERE profile_id = %s AND content_id = %s;", (profile_id, content_id))

            conn.commit()

            return jsonify({
                "success": True,
                "message": "Đã hoàn tất toàn bộ series!" if all_episodes_done else "Đã cập nhật tiến trình tập phim thành công!",
                "history_id": new_hid,
                "stopped_position_seconds": stopped_sec,
                "max_duration_seconds": max_sec,
                "series_completed_episodes": completed_eps_count,
                "series_total_episodes": total_eps,
                "is_completed": all_episodes_done
            })

    except Error as err:
        conn.rollback()
        is_trigger = (err.sqlstate == '45000' or err.errno == 1644)
        return jsonify({
            "success": False,
            "error": err.msg,
            "is_trigger": is_trigger,
            "rule": "BR-09: Chặn hồ sơ Trẻ em (is_kids = TRUE) tiếp cận nội dung nhãn R và NC-17"
        }), 400
    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/api/watch-history/<int:history_id>', methods=['DELETE'])
def delete_watch_history(history_id):
    """Xóa một mục khỏi lịch sử xem (FR-05)."""
    sql = "DELETE FROM watch_history WHERE history_id = %s;"
    ok, err_or_msg, _ = execute(sql, (history_id,))
    if ok:
        return jsonify({
            "success": True,
            "message": "Đã xóa mục lịch sử xem thành công!",
            "history_id": history_id
        })
    return jsonify({"success": False, "error": err_or_msg["msg"]}), 400


# =====================================================================
# 7. API QUẢN TRỊ VIÊN & PHÂN TÍCH (ADMIN & ANALYTICS - PHASE 3 QUERIES)
# =====================================================================
@app.route('/api/admin/revenue', methods=['GET'])
def get_revenue_summary():
    """Báo cáo doanh thu theo View vw_subscription_revenue_summary."""
    return jsonify(query("SELECT * FROM vw_subscription_revenue_summary;"))

@app.route('/api/admin/users', methods=['GET'])
def get_admin_users():
    sql = """
        SELECT
            ua.account_id,
            ua.email,
            ua.registration_date,
            ua.account_status,
            st.tier_id,
            st.tier_name,
            st.monthly_price,
            st.max_profiles_allowed,
            st.resolution,
            COUNT(p.profile_id) AS profile_count,
            COUNT(p.profile_id) AS current_profile_count,
            GROUP_CONCAT(CONCAT(p.profile_name, IF(p.is_kids, ' (Kids)', '')) SEPARATOR ', ') AS profiles_str
        FROM user_account ua
        INNER JOIN subscription_tier st ON ua.tier_id = st.tier_id
        LEFT JOIN profile p ON ua.account_id = p.account_id
        GROUP BY ua.account_id, ua.email, ua.registration_date, ua.account_status,
                 st.tier_id, st.tier_name, st.monthly_price, st.max_profiles_allowed, st.resolution
        ORDER BY ua.account_id DESC
        LIMIT 100;
    """
    return jsonify(query(sql))

@app.route('/api/admin/users/<int:account_id>', methods=['PATCH'])
def update_user_status(account_id):
    data = request.json or {}
    status = data.get('account_status')
    tier_id = data.get('tier_id')

    if status and tier_id:
        sql = "UPDATE user_account SET account_status = %s, tier_id = %s WHERE account_id = %s;"
        params = (status, tier_id, account_id)
    elif status:
        sql = "UPDATE user_account SET account_status = %s WHERE account_id = %s;"
        params = (status, account_id)
    elif tier_id:
        sql = "UPDATE user_account SET tier_id = %s WHERE account_id = %s;"
        params = (tier_id, account_id)
    else:
        return jsonify({"error": "Không có thông tin cần cập nhật"}), 400

    ok, err_or_msg, _ = execute(sql, params)
    if ok:
        return jsonify({"success": True, "message": "Đã cập nhật trạng thái tài khoản thành công!"})
    return jsonify({"success": False, "error": err_or_msg["msg"]}), 400

@app.route('/api/admin/content', methods=['POST'])
def add_new_content():
    """Thêm sản phẩm nội dung mới vào CSDL."""
    data = request.json or {}
    title = data.get('title', '').strip()
    description = data.get('description', '').strip()
    release_year = data.get('release_year', 2025)
    rating_age = data.get('rating_age', 'PG-13')
    content_type = data.get('content_type', 'MOVIE')
    language_code = data.get('language_code', 'vi')
    genre_ids = data.get('genre_ids', [1])

    if not title:
        return jsonify({"error": "Tiêu đề không được để trống"}), 400

    conn = get_db_connection()
    try:
        cur = conn.cursor()
        # 1. Thêm CONTENT
        cur.execute("""
            INSERT INTO content (title, description, release_year, rating_age, content_type, language_code)
            VALUES (%s, %s, %s, %s, %s, %s);
        """, (title, description, release_year, rating_age, content_type, language_code))
        new_content_id = cur.lastrowid

        # 2. Thêm vào phân lớp MOVIE hoặc TV_SERIES
        if content_type == 'MOVIE':
            duration = data.get('duration_minutes', 120)
            res = data.get('video_resolution', '4K')
            cur.execute("""
                INSERT INTO movie (content_id, duration_minutes, video_resolution)
                VALUES (%s, %s, %s);
            """, (new_content_id, duration, res))
        else:
            seasons = data.get('total_seasons', 1)
            status = data.get('series_status', 'ONGOING')
            cur.execute("""
                INSERT INTO tv_series (content_id, total_seasons, series_status)
                VALUES (%s, %s, %s);
            """, (new_content_id, seasons, status))
            # Tạo sẵn Season 1
            cur.execute("""
                INSERT INTO season (content_id, season_number, season_name, release_date)
                VALUES (%s, 1, 'Mùa 1', CURRENT_DATE);
            """, (new_content_id,))
            s1_id = cur.lastrowid
            # Tạo sẵn Tập 1
            cur.execute("""
                INSERT INTO tv_episode (season_id, episode_number, episode_title, duration_minutes)
                VALUES (%s, 1, 'Tập mở màn', 45);
            """, (s1_id,))

        # 3. Thêm Thể loại CONTENT_GENRE
        for gid in genre_ids:
            cur.execute("""
                INSERT INTO content_genre (content_id, genre_id)
                VALUES (%s, %s);
            """, (new_content_id, gid))

        conn.commit()
        return jsonify({"success": True, "message": f"Đã thêm phim '{title}' thành công!", "content_id": new_content_id}), 201
    except Error as e:
        conn.rollback()
        return jsonify({"success": False, "error": e.msg}), 400
    finally:
        cur.close()
        conn.close()

@app.route('/api/admin/content/<int:content_id>', methods=['DELETE'])
def delete_admin_content(content_id):
    """Xóa sản phẩm nội dung. Tự động ON DELETE CASCADE xuống Movie/TV_Series, Season, Episode, Thể loại, Watchlist, Lịch sử xem."""
    sql = "DELETE FROM content WHERE content_id = %s;"
    ok, err_or_msg, _ = execute(sql, (content_id,))
    if ok:
        return jsonify({
            "success": True,
            "message": f"Đã xóa tác phẩm ID {content_id} và toàn bộ dữ liệu phân cấp EER liên quan thành công!",
            "content_id": content_id
        })
    return jsonify({"success": False, "error": err_or_msg["msg"]}), 400

@app.route('/api/admin/seasons', methods=['POST'])
def add_admin_season():
    """Thêm mùa mới (SEASON - BR-04) cho Phim bộ và đồng bộ total_seasons trong tv_series."""
    data = request.json or {}
    content_id = data.get('content_id')
    season_number = data.get('season_number')
    season_name = data.get('season_name', '').strip() or None
    release_date = data.get('release_date') or None

    if not content_id:
        return jsonify({"success": False, "error": "Thiếu content_id cho TV_SERIES"}), 400

    conn = get_db_connection()
    try:
        cur = conn.cursor(dictionary=True)
        # Kiểm tra content_id có phải TV_SERIES
        cur.execute("SELECT content_type FROM content WHERE content_id = %s;", (content_id,))
        c = cur.fetchone()
        if not c or c['content_type'] != 'TV_SERIES':
            return jsonify({"success": False, "error": f"Nội dung ID {content_id} không phải là Phim bộ (TV_SERIES)"}), 400

        # Nếu không truyền season_number, tự động tăng tiếp theo
        if not season_number:
            cur.execute("SELECT COALESCE(MAX(season_number), 0) + 1 AS next_sn FROM season WHERE content_id = %s;", (content_id,))
            season_number = cur.fetchone()['next_sn']
        else:
            season_number = int(season_number)

        if not season_name:
            season_name = f"Mùa {season_number}"

        insert_sql = """
            INSERT INTO season (content_id, season_number, season_name, release_date)
            VALUES (%s, %s, %s, %s);
        """
        cur.execute(insert_sql, (content_id, season_number, season_name, release_date))
        season_id = cur.lastrowid

        # Đồng bộ tv_series.total_seasons
        update_sql = """
            UPDATE tv_series
            SET total_seasons = (SELECT COUNT(*) FROM season WHERE content_id = %s)
            WHERE content_id = %s;
        """
        cur.execute(update_sql, (content_id, content_id))
        conn.commit()

        return jsonify({
            "success": True,
            "message": f"Thêm {season_name} thành công!",
            "season_id": season_id,
            "season_number": season_number
        }), 201
    except Error as e:
        conn.rollback()
        return jsonify({"success": False, "error": e.msg}), 400
    finally:
        cur.close()
        conn.close()

@app.route('/api/admin/episodes', methods=['POST'])
def add_admin_episode():
    """Thêm tập phim mới (TV_EPISODE - BR-08) vào một Mùa (SEASON)."""
    data = request.json or {}
    season_id = data.get('season_id')
    episode_number = data.get('episode_number')
    episode_title = data.get('episode_title', '').strip()
    duration_minutes = int(data.get('duration_minutes', 45))

    if not season_id:
        return jsonify({"success": False, "error": "Thiếu season_id"}), 400

    conn = get_db_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT season_id, season_number FROM season WHERE season_id = %s;", (season_id,))
        s = cur.fetchone()
        if not s:
            return jsonify({"success": False, "error": f"Không tìm thấy Mùa (SEASON) với ID {season_id}"}), 404

        if not episode_number:
            cur.execute("SELECT COALESCE(MAX(episode_number), 0) + 1 AS next_ep FROM tv_episode WHERE season_id = %s;", (season_id,))
            episode_number = cur.fetchone()['next_ep']
        else:
            episode_number = int(episode_number)

        if not episode_title:
            episode_title = f"Tập {episode_number}"

        insert_sql = """
            INSERT INTO tv_episode (season_id, episode_number, episode_title, duration_minutes)
            VALUES (%s, %s, %s, %s);
        """
        cur.execute(insert_sql, (season_id, episode_number, episode_title, duration_minutes))
        episode_id = cur.lastrowid
        conn.commit()

        return jsonify({
            "success": True,
            "message": f"Thêm '{episode_title}' vào Mùa {s['season_number']} thành công!",
            "episode_id": episode_id,
            "episode_number": episode_number
        }), 201
    except Error as e:
        conn.rollback()
        return jsonify({"success": False, "error": e.msg}), 400
    finally:
        cur.close()
        conn.close()

@app.route('/api/admin/genres', methods=['POST'])
def add_admin_genre():
    """Thêm thể loại mới (GENRE - FR-07)."""
    data = request.json or {}
    genre_name = data.get('genre_name', '').strip()
    if not genre_name:
        return jsonify({"success": False, "error": "Tên thể loại không được để trống"}), 400

    sql = "INSERT INTO genre (genre_name) VALUES (%s);"
    ok, err_or_msg, new_id = execute(sql, (genre_name,))
    if ok:
        return jsonify({
            "success": True,
            "message": f"Đã thêm thể loại '{genre_name}' thành công!",
            "genre_id": new_id
        }), 201
    return jsonify({"success": False, "error": err_or_msg["msg"]}), 400

@app.route('/api/admin/languages', methods=['POST'])
def add_admin_language():
    """Thêm ngôn ngữ mới (LANGUAGE - FR-06)."""
    data = request.json or {}
    lang_code = (data.get('iso_code') or data.get('language_code', '')).strip().lower()
    lang_name = data.get('language_name', '').strip()

    if not lang_code or not lang_name:
        return jsonify({"success": False, "error": "Vui lòng nhập cả mã ngôn ngữ (iso_code) và tên ngôn ngữ (language_name)"}), 400

    sql = "INSERT INTO language (language_code, language_name) VALUES (%s, %s);"
    ok, err_or_msg, _ = execute(sql, (lang_code, lang_name))
    if ok:
        return jsonify({
            "success": True,
            "message": f"Đã thêm ngôn ngữ '{lang_name}' ({lang_code}) thành công!",
            "language_id": lang_code,
            "language_code": lang_code
        }), 201
    return jsonify({"success": False, "error": err_or_msg["msg"]}), 400

# 10 Câu truy vấn chuẩn môn học từ 03_queries.sql
QUERIES = {
    1: {
        "title": "Truy vấn 1: Phim lẻ (MOVIE) chuẩn 4K HDR",
        "description": "Multi-table JOIN (5 bảng): Lấy danh sách phim lẻ 4K kèm ngôn ngữ gốc và các thể loại.",
        "sql": """
            SELECT
                c.content_id,
                c.title AS movie_title,
                c.release_year,
                c.rating_age,
                l.language_name AS original_language,
                m.duration_minutes,
                m.video_resolution,
                GROUP_CONCAT(g.genre_name ORDER BY g.genre_name SEPARATOR ', ') AS genres
            FROM content c
            INNER JOIN movie m ON c.content_id = m.content_id
            INNER JOIN language l ON c.language_code = l.language_code
            INNER JOIN content_genre cg ON c.content_id = cg.content_id
            INNER JOIN genre g ON cg.genre_id = g.genre_id
            WHERE m.video_resolution = '4K'
            GROUP BY c.content_id, c.title, c.release_year, c.rating_age, l.language_name, m.duration_minutes, m.video_resolution
            ORDER BY c.release_year DESC
            LIMIT 50;
        """
    },
    2: {
        "title": "Truy vấn 2: Cấu trúc phân cấp Phim bộ (TV_SERIES)",
        "description": "Hierarchical 4-Table JOIN: Truy xuất toàn bộ chuỗi kế thừa CONTENT -> TV_SERIES -> SEASON -> TV_EPISODE.",
        "sql": """
            SELECT
                c.title AS series_title,
                tv.series_status,
                s.season_number,
                s.season_name,
                ep.episode_number,
                ep.episode_title,
                ep.duration_minutes
            FROM content c
            INNER JOIN tv_series tv ON c.content_id = tv.content_id
            INNER JOIN season s ON tv.content_id = s.content_id
            INNER JOIN tv_episode ep ON s.season_id = ep.season_id
            ORDER BY c.title ASC, s.season_number ASC, ep.episode_number ASC
            LIMIT 100;
        """
    },
    3: {
        "title": "Truy vấn 3: Tiếp tục xem (Continue Watching) - BR-06, FR-05",
        "description": "LEFT JOIN & Continuous Playback: Hiển thị các nội dung đang xem dở (is_completed = FALSE) của các Profile.",
        "sql": """
            SELECT
                p.profile_name,
                c.title AS content_title,
                c.content_type,
                COALESCE(CONCAT('Mùa ', s.season_number, ' - Tập ', ep.episode_number, ': ', ep.episode_title), 'Phim lẻ') AS current_episode_info,
                ROUND(wh.stopped_position_seconds / 60, 1) AS stopped_at_minute,
                wh.last_watched_timestamp
            FROM watch_history wh
            INNER JOIN profile p ON wh.profile_id = p.profile_id
            INNER JOIN content c ON wh.content_id = c.content_id
            LEFT JOIN tv_episode ep ON wh.episode_id = ep.episode_id
            LEFT JOIN season s ON ep.season_id = s.season_id
            WHERE wh.is_completed = FALSE
            ORDER BY wh.last_watched_timestamp DESC
            LIMIT 50;
        """
    },
    4: {
        "title": "Truy vấn 4: Top 5 nội dung ăn khách nhất hệ thống",
        "description": "GROUP BY & Aggregation: Thống kê tổng lượt xem và số lượt xem trọn vẹn theo từng tựa phim.",
        "sql": """
            SELECT
                c.content_id,
                c.title,
                c.content_type,
                c.rating_age,
                COUNT(wh.history_id) AS total_views,
                SUM(CASE WHEN wh.is_completed = TRUE THEN 1 ELSE 0 END) AS completed_views
            FROM content c
            INNER JOIN watch_history wh ON c.content_id = wh.content_id
            GROUP BY c.content_id, c.title, c.content_type, c.rating_age
            ORDER BY total_views DESC, completed_views DESC
            LIMIT 5;
        """
    },
    5: {
        "title": "Truy vấn 5: Báo cáo doanh thu theo Gói cước (Revenue Analysis)",
        "description": "Doanh thu hàng tháng dự kiến, số tài khoản ACTIVE và tổng hồ sơ được tạo trên từng gói cước.",
        "sql": """
            SELECT
                st.tier_name,
                st.monthly_price,
                COUNT(DISTINCT ua.account_id) AS active_accounts,
                COUNT(p.profile_id) AS total_profiles_created,
                COUNT(DISTINCT ua.account_id) * st.monthly_price AS monthly_revenue_vnd
            FROM subscription_tier st
            LEFT JOIN user_account ua ON st.tier_id = ua.tier_id AND ua.account_status = 'ACTIVE'
            LEFT JOIN profile p ON ua.account_id = p.account_id
            GROUP BY st.tier_id, st.tier_name, st.monthly_price
            ORDER BY monthly_revenue_vnd DESC;
        """
    },
    6: {
        "title": "Truy vấn 6: Tỷ lệ xem hoàn thành theo từng Profile",
        "description": "GROUP BY & Completion Rate: Tổng số phim đã xem, tổng số phút xem và tỷ lệ % xem hết nội dung.",
        "sql": """
            SELECT
                ua.email AS account_email,
                p.profile_name,
                p.is_kids,
                COUNT(wh.history_id) AS total_titles_watched,
                ROUND(SUM(wh.stopped_position_seconds) / 60.0, 1) AS total_minutes_streamed,
                ROUND(AVG(CASE WHEN wh.is_completed = TRUE THEN 100.0 ELSE 0.0 END), 1) AS completion_rate_percent
            FROM profile p
            INNER JOIN user_account ua ON p.account_id = ua.account_id
            INNER JOIN watch_history wh ON p.profile_id = wh.profile_id
            GROUP BY ua.email, p.profile_id, p.profile_name, p.is_kids
            ORDER BY total_minutes_streamed DESC
            LIMIT 50;
        """
    },
    7: {
        "title": "Truy vấn 7: Phim trong Watchlist nhưng chưa từng xem",
        "description": "Correlated Subquery (NOT EXISTS): Tìm các tựa phim người dùng đã lưu xem sau nhưng chưa xem lần nào.",
        "sql": """
            SELECT
                p.profile_name,
                c.title AS unwatched_saved_title,
                c.content_type,
                w.added_at AS saved_to_watchlist_at
            FROM watchlist w
            INNER JOIN profile p ON w.profile_id = p.profile_id
            INNER JOIN content c ON w.content_id = c.content_id
            WHERE NOT EXISTS (
                SELECT 1 FROM watch_history wh
                WHERE wh.profile_id = w.profile_id AND wh.content_id = w.content_id
            )
            ORDER BY w.added_at ASC
            LIMIT 50;
        """
    },
    8: {
        "title": "Truy vấn 8: Phim lẻ dài hơn thời lượng trung bình toàn hệ thống",
        "description": "Scalar Subquery: So sánh thời lượng phim với giá trị AVG(duration_minutes).",
        "sql": """
            SELECT
                c.title,
                c.release_year,
                m.duration_minutes,
                (SELECT ROUND(AVG(duration_minutes), 1) FROM movie) AS system_avg_duration
            FROM content c
            INNER JOIN movie m ON c.content_id = m.content_id
            WHERE m.duration_minutes > (SELECT AVG(duration_minutes) FROM movie)
            ORDER BY m.duration_minutes DESC
            LIMIT 50;
        """
    },
    9: {
        "title": "Truy vấn 9: Thống kê thể loại (Genre) được xem nhiều nhất",
        "description": "Subquery & Grouping: Đếm số lượng đầu phim và tổng lượt xem thực tế theo từng thể loại.",
        "sql": """
            SELECT
                g.genre_name,
                COUNT(DISTINCT cg.content_id) AS total_catalog_titles,
                COUNT(wh.history_id) AS total_stream_views
            FROM genre g
            LEFT JOIN content_genre cg ON g.genre_id = cg.genre_id
            LEFT JOIN watch_history wh ON cg.content_id = wh.content_id
            GROUP BY g.genre_id, g.genre_name
            HAVING COUNT(wh.history_id) > 0
            ORDER BY total_stream_views DESC, total_catalog_titles DESC;
        """
    },
    10: {
        "title": "Truy vấn 10: Danh mục phim an toàn cho Trẻ em (Kids Safe - BR-09)",
        "description": "Lọc tự động các phim không gắn nhãn R và NC-17 phù hợp với hồ sơ thiếu nhi.",
        "sql": """
            SELECT
                c.content_id,
                c.title,
                c.content_type,
                c.rating_age,
                l.language_name,
                GROUP_CONCAT(g.genre_name SEPARATOR ', ') AS genres
            FROM content c
            INNER JOIN language l ON c.language_code = l.language_code
            INNER JOIN content_genre cg ON c.content_id = cg.content_id
            INNER JOIN genre g ON cg.genre_id = g.genre_id
            WHERE c.rating_age NOT IN ('R', 'NC-17')
            GROUP BY c.content_id, c.title, c.content_type, c.rating_age, l.language_name
            ORDER BY c.rating_age ASC, c.title ASC
            LIMIT 50;
        """
    }
}

@app.route('/api/admin/queries', methods=['GET'])
def list_analytics_queries():
    result = [
        {"id": qid, "title": qdata["title"], "description": qdata["description"]}
        for qid, qdata in QUERIES.items()
    ]
    return jsonify(result)

@app.route('/api/admin/queries/<int:query_id>', methods=['GET'])
def run_analytics_query(query_id):
    if query_id not in QUERIES:
        return jsonify({"error": "Không tìm thấy truy vấn số " + str(query_id)}), 404
        
    qdata = QUERIES[query_id]
    try:
        data = query(qdata["sql"])
        return jsonify({
            "success": True,
            "id": query_id,
            "title": qdata["title"],
            "description": qdata["description"],
            "sql": qdata["sql"].strip(),
            "count": len(data),
            "data": data
        })
    except Error as e:
        return jsonify({"success": False, "error": e.msg, "sql": qdata["sql"]}), 400

@app.route('/api/admin/tables/<table_name>', methods=['GET'])
def inspect_table(table_name):
    allowed_tables = [
        "subscription_tier", "user_account", "profile", "language", "genre",
        "content", "content_genre", "movie", "tv_series", "season",
        "tv_episode", "watchlist", "watch_history",
        "vw_content_full_catalog", "vw_subscription_revenue_summary"
    ]
    if table_name not in allowed_tables:
        return jsonify({"error": "Tên bảng không hợp lệ hoặc bị cấm."}), 400

    limit = request.args.get('limit', 100, type=int)
    if limit is None:
        limit = 100
    limit = min(max(limit, 1), 300)
    sql = f"SELECT * FROM `{table_name}` LIMIT {limit};"
    return jsonify(query(sql))


# =====================================================================
# 8. DYNAMIC MULTI-FILTER QUERY BUILDER & SAFE READ-ONLY SQL RUNNER
# =====================================================================

def format_readable_sql(sql, params):
    """Tạo chuỗi SQL đẹp, có thể đọc được bằng cách thay thế an toàn các tham số %s."""
    if not params:
        return sql.strip()
    formatted = sql
    for param in params:
        if param is None:
            rep = "NULL"
        elif isinstance(param, (int, float)):
            rep = str(param)
        elif isinstance(param, bool):
            rep = "1" if param else "0"
        else:
            escaped = str(param).replace("'", "''")
            rep = f"'{escaped}'"
        formatted = formatted.replace("%s", rep, 1)
    return formatted.strip()

def build_dynamic_query(payload):
    """Xây dựng câu lệnh SQL có tham số (%s) cho Bộ Lọc Đa Chiều (Dynamic Query Builder)."""
    domain = payload.get('domain', 'content')
    content_type = payload.get('content_type', '').strip().upper()

    genre_id = payload.get('genre_id')
    try:
        genre_id = int(genre_id) if genre_id not in ('', None) else None
    except (ValueError, TypeError):
        genre_id = None

    language_id = payload.get('language_id')
    if language_id in ('', None):
        language_id = None

    rating_age = payload.get('rating_age', '').strip().upper()
    max_resolution = payload.get('max_resolution', '').strip()
    norm_res = None
    if max_resolution:
        res_u = max_resolution.upper()
        if '4K' in res_u:
            norm_res = '4K'
        elif '2K' in res_u:
            norm_res = '2K'
        elif '1080' in res_u or 'HD' in res_u:
            norm_res = '1080p'
        else:
            norm_res = max_resolution

    year_from = payload.get('year_from')
    try:
        year_from = int(year_from) if year_from not in ('', None) else None
    except (ValueError, TypeError):
        year_from = None

    year_to = payload.get('year_to')
    try:
        year_to = int(year_to) if year_to not in ('', None) else None
    except (ValueError, TypeError):
        year_to = None

    tier_id = payload.get('tier_id')
    try:
        tier_id = int(tier_id) if tier_id not in ('', None) else None
    except (ValueError, TypeError):
        tier_id = None

    account_status = payload.get('account_status', '').strip().upper()
    country_code = payload.get('country_code', '').strip().lower()

    is_kids = payload.get('is_kids')
    is_kids_val = None
    if is_kids not in ('', None):
        if str(is_kids).lower() in ('1', 'true', 'yes'):
            is_kids_val = 1
        elif str(is_kids).lower() in ('0', 'false', 'no'):
            is_kids_val = 0

    is_completed = payload.get('is_completed')
    is_completed_val = None
    if is_completed not in ('', None):
        if str(is_completed).lower() in ('1', 'true', 'yes'):
            is_completed_val = 1
        elif str(is_completed).lower() in ('0', 'false', 'no'):
            is_completed_val = 0

    group_by = payload.get('group_by', '').strip().lower()
    min_count = payload.get('min_count')
    try:
        min_count = int(min_count) if min_count not in ('', None) else None
    except (ValueError, TypeError):
        min_count = None

    sort_by = payload.get('sort_by', '').strip()
    if sort_by and not re.match(r'^[a-zA-Z0-9_]+$', sort_by):
        sort_by = ''

    sort_dir = payload.get('sort_dir', 'DESC').strip().upper()
    if sort_dir not in ('ASC', 'DESC'):
        sort_dir = 'DESC'

    try:
        limit = min(max(int(payload.get('limit', 50)), 1), 300)
    except (ValueError, TypeError):
        limit = 50

    # -------------------------------------------------------------
    # DOMAIN 1: Kho Nội Dung & Phân Cấp EER (CONTENT)
    # -------------------------------------------------------------
    if domain == 'content':
        where = ["1=1"]
        params = []

        if content_type in ('MOVIE', 'TV_SERIES'):
            where.append("c.content_type = %s")
            params.append(content_type)
        if genre_id is not None:
            where.append("cg.genre_id = %s")
            params.append(genre_id)
        if language_id is not None:
            where.append("(c.language_code = %s OR l.language_code = %s OR l.language_name = %s)")
            params.extend([str(language_id), str(language_id), str(language_id)])
        if rating_age in ('G', 'PG', 'PG-13', 'R', 'NC-17'):
            where.append("c.rating_age = %s")
            params.append(rating_age)
        if norm_res:
            where.append("m.video_resolution = %s")
            params.append(norm_res)
        if year_from is not None:
            where.append("c.release_year >= %s")
            params.append(year_from)
        if year_to is not None:
            where.append("c.release_year <= %s")
            params.append(year_to)
        if is_kids_val == 1:
            where.append("c.rating_age NOT IN ('R', 'NC-17')")

        where_str = " AND ".join(where)

        if group_by == 'genre':
            select_clause = """
                SELECT
                    g.genre_id,
                    g.genre_name,
                    COUNT(DISTINCT c.content_id) AS total_titles,
                    COUNT(DISTINCT wh.history_id) AS total_views,
                    COUNT(DISTINCT wl.profile_id) AS watchlist_saves,
                    ROUND(AVG(c.release_year), 0) AS avg_release_year
                FROM genre g
                INNER JOIN content_genre cg ON g.genre_id = cg.genre_id
                INNER JOIN content c ON cg.content_id = c.content_id
                LEFT JOIN movie m ON c.content_id = m.content_id
                LEFT JOIN tv_series tv ON c.content_id = tv.content_id
                LEFT JOIN language l ON c.language_code = l.language_code
                LEFT JOIN watch_history wh ON c.content_id = wh.content_id
                LEFT JOIN watchlist wl ON c.content_id = wl.content_id
            """
            group_clause = "GROUP BY g.genre_id, g.genre_name"
            default_sort = "total_views DESC, total_titles DESC"
            having_clause = ""
            if min_count is not None:
                having_clause = "HAVING COUNT(DISTINCT c.content_id) >= %s"
                params.append(min_count)

        elif group_by == 'language':
            select_clause = """
                SELECT
                    l.language_code,
                    l.language_name,
                    COUNT(DISTINCT c.content_id) AS total_titles,
                    COUNT(DISTINCT wh.history_id) AS total_views,
                    ROUND(AVG(c.release_year), 0) AS avg_release_year
                FROM language l
                INNER JOIN content c ON l.language_code = c.language_code
                LEFT JOIN movie m ON c.content_id = m.content_id
                LEFT JOIN tv_series tv ON c.content_id = tv.content_id
                LEFT JOIN content_genre cg ON c.content_id = cg.content_id
                LEFT JOIN genre g ON cg.genre_id = g.genre_id
                LEFT JOIN watch_history wh ON c.content_id = wh.content_id
            """
            group_clause = "GROUP BY l.language_code, l.language_name"
            default_sort = "total_views DESC, total_titles DESC"
            having_clause = ""
            if min_count is not None:
                having_clause = "HAVING COUNT(DISTINCT c.content_id) >= %s"
                params.append(min_count)

        elif group_by == 'content_type':
            select_clause = """
                SELECT
                    c.content_type,
                    COUNT(DISTINCT c.content_id) AS total_titles,
                    COUNT(DISTINCT wh.history_id) AS total_views,
                    ROUND(AVG(c.release_year), 0) AS avg_release_year
                FROM content c
                LEFT JOIN movie m ON c.content_id = m.content_id
                LEFT JOIN tv_series tv ON c.content_id = tv.content_id
                LEFT JOIN language l ON c.language_code = l.language_code
                LEFT JOIN content_genre cg ON c.content_id = cg.content_id
                LEFT JOIN genre g ON cg.genre_id = g.genre_id
                LEFT JOIN watch_history wh ON c.content_id = wh.content_id
            """
            group_clause = "GROUP BY c.content_type"
            default_sort = "total_views DESC"
            having_clause = ""
            if min_count is not None:
                having_clause = "HAVING COUNT(DISTINCT c.content_id) >= %s"
                params.append(min_count)

        elif group_by == 'rating_age':
            select_clause = """
                SELECT
                    c.rating_age,
                    COUNT(DISTINCT c.content_id) AS total_titles,
                    COUNT(DISTINCT wh.history_id) AS total_views
                FROM content c
                LEFT JOIN movie m ON c.content_id = m.content_id
                LEFT JOIN tv_series tv ON c.content_id = tv.content_id
                LEFT JOIN language l ON c.language_code = l.language_code
                LEFT JOIN content_genre cg ON c.content_id = cg.content_id
                LEFT JOIN genre g ON cg.genre_id = g.genre_id
                LEFT JOIN watch_history wh ON c.content_id = wh.content_id
            """
            group_clause = "GROUP BY c.rating_age"
            default_sort = "total_views DESC"
            having_clause = ""
            if min_count is not None:
                having_clause = "HAVING COUNT(DISTINCT c.content_id) >= %s"
                params.append(min_count)

        else:
            # Detail rows
            select_clause = """
                SELECT
                    c.content_id,
                    c.title,
                    c.content_type,
                    c.release_year,
                    c.rating_age,
                    l.language_name AS original_language,
                    GROUP_CONCAT(DISTINCT g.genre_name ORDER BY g.genre_name SEPARATOR ', ') AS genres,
                    m.duration_minutes AS movie_duration_mins,
                    COALESCE(m.video_resolution, 'N/A') AS video_resolution,
                    tv.total_seasons,
                    tv.series_status,
                    COUNT(DISTINCT wh.history_id) AS total_views,
                    COUNT(DISTINCT wl.profile_id) AS watchlist_count
                FROM content c
                LEFT JOIN movie m ON c.content_id = m.content_id
                LEFT JOIN tv_series tv ON c.content_id = tv.content_id
                LEFT JOIN language l ON c.language_code = l.language_code
                LEFT JOIN content_genre cg ON c.content_id = cg.content_id
                LEFT JOIN genre g ON cg.genre_id = g.genre_id
                LEFT JOIN watch_history wh ON c.content_id = wh.content_id
                LEFT JOIN watchlist wl ON c.content_id = wl.content_id
            """
            group_clause = """
                GROUP BY c.content_id, c.title, c.content_type, c.release_year, c.rating_age,
                         l.language_name, m.duration_minutes, m.video_resolution, tv.total_seasons, tv.series_status
            """
            default_sort = "c.release_year DESC, c.title ASC"
            having_clause = ""
            if min_count is not None:
                having_clause = "HAVING COUNT(DISTINCT wh.history_id) >= %s"
                params.append(min_count)

        order_str = f"ORDER BY {sort_by} {sort_dir}" if sort_by else f"ORDER BY {default_sort}"
        sql = f"""
            {select_clause.strip()}
            WHERE {where_str}
            {group_clause.strip()}
            {having_clause}
            {order_str}
            LIMIT %s;
        """
        params.append(limit)
        return sql, params

    # -------------------------------------------------------------
    # DOMAIN 2: Hành Vi Xem & Tương Tác (WATCH_BEHAVIOR)
    # -------------------------------------------------------------
    elif domain == 'watch_behavior':
        where = ["1=1"]
        params = []

        if content_type in ('MOVIE', 'TV_SERIES'):
            where.append("c.content_type = %s")
            params.append(content_type)
        if genre_id is not None:
            where.append("cg.genre_id = %s")
            params.append(genre_id)
        if language_id is not None:
            where.append("(c.language_code = %s OR l.language_code = %s)")
            params.extend([str(language_id), str(language_id)])
        if rating_age in ('G', 'PG', 'PG-13', 'R', 'NC-17'):
            where.append("c.rating_age = %s")
            params.append(rating_age)
        if year_from is not None:
            where.append("c.release_year >= %s")
            params.append(year_from)
        if year_to is not None:
            where.append("c.release_year <= %s")
            params.append(year_to)
        if tier_id is not None:
            where.append("st.tier_id = %s")
            params.append(tier_id)
        if account_status:
            where.append("ua.account_status = %s")
            params.append(account_status)
        if country_code:
            where.append("ua.email LIKE %s")
            params.append(f"%{country_code}%")
        if is_kids_val is not None:
            where.append("p.is_kids = %s")
            params.append(is_kids_val)
        if is_completed_val is not None:
            where.append("wh.is_completed = %s")
            params.append(is_completed_val)

        where_str = " AND ".join(where)

        from_tables = """
            FROM watch_history wh
            INNER JOIN profile p ON wh.profile_id = p.profile_id
            INNER JOIN user_account ua ON p.account_id = ua.account_id
            INNER JOIN subscription_tier st ON ua.tier_id = st.tier_id
            INNER JOIN content c ON wh.content_id = c.content_id
            LEFT JOIN movie m ON c.content_id = m.content_id
            LEFT JOIN tv_episode ep ON wh.episode_id = ep.episode_id
            LEFT JOIN season s ON ep.season_id = s.season_id
            LEFT JOIN content_genre cg ON c.content_id = cg.content_id
            LEFT JOIN genre g ON cg.genre_id = g.genre_id
            LEFT JOIN language l ON c.language_code = l.language_code
        """

        if group_by == 'profile':
            select_clause = f"""
                SELECT
                    p.profile_id,
                    p.profile_name,
                    p.is_kids,
                    ua.email AS account_email,
                    st.tier_name,
                    COUNT(DISTINCT wh.history_id) AS total_views,
                    COUNT(DISTINCT wh.content_id) AS distinct_titles,
                    ROUND(SUM(wh.stopped_position_seconds) / 60.0, 1) AS total_minutes_watched,
                    SUM(CASE WHEN wh.is_completed = 1 THEN 1 ELSE 0 END) AS completed_views,
                    ROUND(AVG(CASE WHEN wh.is_completed = 1 THEN 100.0 ELSE 0.0 END), 1) AS completion_rate_pct
                {from_tables}
            """
            group_clause = "GROUP BY p.profile_id, p.profile_name, p.is_kids, ua.email, st.tier_name"
            default_sort = "total_minutes_watched DESC"
            having_clause = ""
            if min_count is not None:
                having_clause = "HAVING COUNT(DISTINCT wh.history_id) >= %s"
                params.append(min_count)

        elif group_by == 'content':
            select_clause = f"""
                SELECT
                    c.content_id,
                    c.title,
                    c.content_type,
                    c.rating_age,
                    COUNT(DISTINCT wh.history_id) AS total_views,
                    SUM(CASE WHEN wh.is_completed = 1 THEN 1 ELSE 0 END) AS completed_views,
                    ROUND(SUM(wh.stopped_position_seconds) / 60.0, 1) AS total_minutes_streamed,
                    ROUND(AVG(CASE WHEN wh.is_completed = 1 THEN 100.0 ELSE 0.0 END), 1) AS completion_rate_pct
                {from_tables}
            """
            group_clause = "GROUP BY c.content_id, c.title, c.content_type, c.rating_age"
            default_sort = "total_views DESC, completed_views DESC"
            having_clause = ""
            if min_count is not None:
                having_clause = "HAVING COUNT(DISTINCT wh.history_id) >= %s"
                params.append(min_count)

        elif group_by == 'genre':
            select_clause = f"""
                SELECT
                    g.genre_id,
                    g.genre_name,
                    COUNT(DISTINCT wh.history_id) AS total_views,
                    COUNT(DISTINCT c.content_id) AS distinct_titles,
                    ROUND(SUM(wh.stopped_position_seconds) / 60.0, 1) AS total_minutes_streamed
                {from_tables}
            """
            group_clause = "GROUP BY g.genre_id, g.genre_name"
            default_sort = "total_views DESC"
            having_clause = ""
            if min_count is not None:
                having_clause = "HAVING COUNT(DISTINCT wh.history_id) >= %s"
                params.append(min_count)

        elif group_by == 'tier':
            select_clause = f"""
                SELECT
                    st.tier_id,
                    st.tier_name,
                    COUNT(DISTINCT wh.history_id) AS total_views,
                    COUNT(DISTINCT p.profile_id) AS active_profiles,
                    ROUND(SUM(wh.stopped_position_seconds) / 60.0, 1) AS total_minutes_streamed
                {from_tables}
            """
            group_clause = "GROUP BY st.tier_id, st.tier_name"
            default_sort = "total_views DESC"
            having_clause = ""
            if min_count is not None:
                having_clause = "HAVING COUNT(DISTINCT wh.history_id) >= %s"
                params.append(min_count)

        elif group_by == 'content_type':
            select_clause = f"""
                SELECT
                    c.content_type,
                    COUNT(DISTINCT wh.history_id) AS total_views,
                    SUM(CASE WHEN wh.is_completed = 1 THEN 1 ELSE 0 END) AS completed_views,
                    ROUND(SUM(wh.stopped_position_seconds) / 60.0, 1) AS total_minutes_streamed
                {from_tables}
            """
            group_clause = "GROUP BY c.content_type"
            default_sort = "total_views DESC"
            having_clause = ""
            if min_count is not None:
                having_clause = "HAVING COUNT(DISTINCT wh.history_id) >= %s"
                params.append(min_count)

        elif group_by == 'rating_age':
            select_clause = f"""
                SELECT
                    c.rating_age,
                    COUNT(DISTINCT wh.history_id) AS total_views,
                    SUM(CASE WHEN wh.is_completed = 1 THEN 1 ELSE 0 END) AS completed_views
                {from_tables}
            """
            group_clause = "GROUP BY c.rating_age"
            default_sort = "total_views DESC"
            having_clause = ""
            if min_count is not None:
                having_clause = "HAVING COUNT(DISTINCT wh.history_id) >= %s"
                params.append(min_count)

        elif group_by == 'country':
            select_clause = f"""
                SELECT
                    UPPER(SUBSTRING_INDEX(ua.email, '.', -1)) AS country_code,
                    COUNT(DISTINCT wh.history_id) AS total_views,
                    COUNT(DISTINCT p.profile_id) AS active_profiles,
                    ROUND(SUM(wh.stopped_position_seconds) / 60.0, 1) AS total_minutes_streamed
                {from_tables}
            """
            group_clause = "GROUP BY UPPER(SUBSTRING_INDEX(ua.email, '.', -1))"
            default_sort = "total_views DESC"
            having_clause = ""
            if min_count is not None:
                having_clause = "HAVING COUNT(DISTINCT wh.history_id) >= %s"
                params.append(min_count)

        else:
            # Detail rows
            select_clause = f"""
                SELECT
                    wh.history_id,
                    p.profile_id,
                    p.profile_name,
                    p.is_kids,
                    ua.email AS account_email,
                    st.tier_name,
                    c.content_id,
                    c.title,
                    c.content_type,
                    c.rating_age,
                    COALESCE(CONCAT('Mùa ', s.season_number, ' - Tập ', ep.episode_number, ': ', ep.episode_title), 'Phim lẻ') AS episode_info,
                    wh.stopped_position_seconds,
                    ROUND(wh.stopped_position_seconds / 60, 1) AS stopped_minutes,
                    wh.is_completed,
                    wh.last_watched_timestamp
                {from_tables}
            """
            group_clause = """
                GROUP BY wh.history_id, p.profile_id, p.profile_name, p.is_kids, ua.email, st.tier_name,
                         c.content_id, c.title, c.content_type, c.rating_age,
                         s.season_number, ep.episode_number, ep.episode_title,
                         wh.stopped_position_seconds, wh.is_completed, wh.last_watched_timestamp
            """
            default_sort = "wh.last_watched_timestamp DESC"
            having_clause = ""
            if min_count is not None:
                having_clause = "HAVING COUNT(DISTINCT wh.history_id) >= %s"
                params.append(min_count)

        order_str = f"ORDER BY {sort_by} {sort_dir}" if sort_by else f"ORDER BY {default_sort}"
        sql = f"""
            {select_clause.strip()}
            WHERE {where_str}
            {group_clause.strip()}
            {having_clause}
            {order_str}
            LIMIT %s;
        """
        params.append(limit)
        return sql, params

    # -------------------------------------------------------------
    # DOMAIN 3: Tài Khoản & Gói Cước Doanh Thu (SUBSCRIPTION)
    # -------------------------------------------------------------
    elif domain == 'subscription':
        where = ["1=1"]
        params = []

        if tier_id is not None:
            where.append("st.tier_id = %s")
            params.append(tier_id)
        if account_status:
            where.append("ua.account_status = %s")
            params.append(account_status)
        if country_code:
            where.append("ua.email LIKE %s")
            params.append(f"%{country_code}%")
        if norm_res:
            where.append("st.resolution = %s")
            params.append(norm_res)
        if is_kids_val is not None:
            where.append("p.is_kids = %s")
            params.append(is_kids_val)

        where_str = " AND ".join(where)

        if group_by in ('tier', 'subscription'):
            select_clause = """
                SELECT
                    st.tier_id,
                    st.tier_name,
                    st.monthly_price,
                    st.max_profiles_allowed,
                    st.resolution,
                    COUNT(DISTINCT ua.account_id) AS total_accounts,
                    SUM(CASE WHEN ua.account_status = 'ACTIVE' THEN 1 ELSE 0 END) AS active_accounts,
                    COUNT(p.profile_id) AS total_profiles_created,
                    ROUND(SUM(CASE WHEN ua.account_status = 'ACTIVE' THEN st.monthly_price ELSE 0 END), 2) AS monthly_revenue_vnd
                FROM subscription_tier st
                LEFT JOIN user_account ua ON st.tier_id = ua.tier_id
                LEFT JOIN profile p ON ua.account_id = p.account_id
            """
            group_clause = "GROUP BY st.tier_id, st.tier_name, st.monthly_price, st.max_profiles_allowed, st.resolution"
            default_sort = "monthly_revenue_vnd DESC"
            having_clause = ""
            if min_count is not None:
                having_clause = "HAVING COUNT(DISTINCT ua.account_id) >= %s"
                params.append(min_count)

        elif group_by == 'account_status':
            select_clause = """
                SELECT
                    ua.account_status,
                    COUNT(DISTINCT ua.account_id) AS total_accounts,
                    COUNT(p.profile_id) AS total_profiles,
                    ROUND(SUM(st.monthly_price), 2) AS potential_revenue_vnd
                FROM user_account ua
                INNER JOIN subscription_tier st ON ua.tier_id = st.tier_id
                LEFT JOIN profile p ON ua.account_id = p.account_id
            """
            group_clause = "GROUP BY ua.account_status"
            default_sort = "total_accounts DESC"
            having_clause = ""
            if min_count is not None:
                having_clause = "HAVING COUNT(DISTINCT ua.account_id) >= %s"
                params.append(min_count)

        elif group_by == 'country':
            select_clause = """
                SELECT
                    UPPER(SUBSTRING_INDEX(ua.email, '.', -1)) AS country_code,
                    COUNT(DISTINCT ua.account_id) AS total_accounts,
                    SUM(CASE WHEN ua.account_status = 'ACTIVE' THEN 1 ELSE 0 END) AS active_accounts,
                    ROUND(SUM(CASE WHEN ua.account_status = 'ACTIVE' THEN st.monthly_price ELSE 0 END), 2) AS monthly_revenue_vnd
                FROM user_account ua
                INNER JOIN subscription_tier st ON ua.tier_id = st.tier_id
                LEFT JOIN profile p ON ua.account_id = p.account_id
            """
            group_clause = "GROUP BY UPPER(SUBSTRING_INDEX(ua.email, '.', -1))"
            default_sort = "total_accounts DESC"
            having_clause = ""
            if min_count is not None:
                having_clause = "HAVING COUNT(DISTINCT ua.account_id) >= %s"
                params.append(min_count)

        else:
            # Detail rows
            select_clause = """
                SELECT
                    ua.account_id,
                    ua.email,
                    ua.registration_date,
                    ua.account_status,
                    st.tier_id,
                    st.tier_name,
                    st.monthly_price,
                    st.max_profiles_allowed,
                    st.resolution,
                    COUNT(p.profile_id) AS profile_count,
                    COUNT(p.profile_id) AS current_profile_count,
                    GROUP_CONCAT(CONCAT(p.profile_name, IF(p.is_kids, ' (Kids)', '')) SEPARATOR ', ') AS profiles_str
                FROM user_account ua
                INNER JOIN subscription_tier st ON ua.tier_id = st.tier_id
                LEFT JOIN profile p ON ua.account_id = p.account_id
            """
            group_clause = """
                GROUP BY ua.account_id, ua.email, ua.registration_date, ua.account_status,
                         st.tier_id, st.tier_name, st.monthly_price, st.max_profiles_allowed, st.resolution
            """
            default_sort = "ua.account_id DESC"
            having_clause = ""
            if min_count is not None:
                having_clause = "HAVING COUNT(p.profile_id) >= %s"
                params.append(min_count)

        order_str = f"ORDER BY {sort_by} {sort_dir}" if sort_by else f"ORDER BY {default_sort}"
        sql = f"""
            {select_clause.strip()}
            WHERE {where_str}
            {group_clause.strip()}
            {having_clause}
            {order_str}
            LIMIT %s;
        """
        params.append(limit)
        return sql, params

    # -------------------------------------------------------------
    # DOMAIN 4: Truy Xuất Bảng / View Nguyên Bản (RAW_TABLE)
    # -------------------------------------------------------------
    else:
        table_name = payload.get('table_name', 'content').strip()
        allowed_tables = [
            "subscription_tier", "user_account", "profile", "language", "genre",
            "content", "content_genre", "movie", "tv_series", "season",
            "tv_episode", "watchlist", "watch_history",
            "vw_content_full_catalog", "vw_subscription_revenue_summary"
        ]
        if table_name not in allowed_tables:
            table_name = "content"

        order_str = f"ORDER BY {sort_by} {sort_dir}" if sort_by else ""
        sql = f"SELECT * FROM `{table_name}` {order_str} LIMIT %s;"
        params = [limit]
        return sql, params

@app.route('/api/admin/query-builder', methods=['POST'])
def dynamic_query_builder():
    """Engine Truy vấn Động Đa Chiều (Dynamic Multi-Filter Analytics Engine)."""
    data = request.json or {}
    domain = data.get('domain', 'content')

    try:
        sql, params = build_dynamic_query(data)
        readable_sql = format_readable_sql(sql, params)

        start_time = time.perf_counter()
        rows = query(sql, tuple(params))
        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

        return jsonify({
            "success": True,
            "domain": domain,
            "generated_sql": readable_sql,
            "row_count": len(rows),
            "execution_time_ms": elapsed_ms,
            "rows": rows
        })
    except Error as e:
        return jsonify({
            "success": False,
            "error": f"MySQL Error ({e.errno}): {e.msg}",
            "generated_sql": readable_sql if 'readable_sql' in locals() else ""
        }), 400
    except Exception as ex:
        return jsonify({
            "success": False,
            "error": str(ex),
            "generated_sql": readable_sql if 'readable_sql' in locals() else ""
        }), 500

@app.route('/api/admin/sql-runner', methods=['POST'])
def run_custom_sql():
    """Chạy câu lệnh SQL Read-Only Sandbox (SELECT, SHOW, DESCRIBE, EXPLAIN). Chặn DML/DDL."""
    data = request.json or {}
    raw_sql = data.get('sql', '').strip()

    if not raw_sql:
        return jsonify({"success": False, "error": "Vui lòng nhập câu lệnh SQL để thực thi."}), 400

    clean_sql = raw_sql.rstrip(';')
    upper_sql = clean_sql.upper().strip()

    # Chỉ cho phép các từ khóa truy vấn đọc
    allowed_verbs = ('SELECT', 'SHOW', 'DESCRIBE', 'EXPLAIN', 'WITH')
    if not any(upper_sql.startswith(verb) for verb in allowed_verbs):
        return jsonify({
            "success": False,
            "error": "Chỉ cho phép các câu lệnh truy vấn đọc dữ liệu (SELECT, SHOW, DESCRIBE, EXPLAIN). Chế độ bảo mật chặn các lệnh ghi và cấu trúc."
        }), 400

    # Chặn các từ khóa DML/DDL phá hoại (từ khóa đứng riêng biệt)
    forbidden_words = [
        'INSERT', 'UPDATE', 'DELETE', 'DROP', 'ALTER', 'TRUNCATE',
        'CREATE', 'GRANT', 'REVOKE', 'RENAME', 'REPLACE', 'LOCK', 'UNLOCK'
    ]
    for word in forbidden_words:
        if re.search(r'\b' + word + r'\b', upper_sql):
            return jsonify({
                "success": False,
                "error": f"Lệnh bị từ chối: Từ khóa nguy hiểm '{word}' bị cấm trong Read-Only SQL Sandbox."
            }), 400

    try:
        start_time = time.perf_counter()
        rows = query(clean_sql)
        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

        return jsonify({
            "success": True,
            "generated_sql": clean_sql,
            "row_count": len(rows),
            "execution_time_ms": elapsed_ms,
            "rows": rows
        })
    except Error as e:
        return jsonify({
            "success": False,
            "error": f"MySQL Error ({e.errno}): {e.msg}",
            "generated_sql": clean_sql
        }), 400
    except Exception as ex:
        return jsonify({
            "success": False,
            "error": str(ex),
            "generated_sql": clean_sql
        }), 500


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print("=" * 70)
    print("🎬 MINI-NETFLIX BACKEND SERVER (FLASK API)")
    print(f"📡 Máy chủ đang lắng nghe tại: http://localhost:{port}")
    print(f"🗄️ Kết nối CSDL MySQL: {DB_CONFIG['user']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")
    print("=" * 70)
    app.run(host='0.0.0.0', port=port, debug=True)
