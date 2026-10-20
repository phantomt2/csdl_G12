import os
from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory
import mysql.connector
from mysql.connector import Error

# Load các biến môi trường từ file .env
load_dotenv()

app = Flask(__name__, static_folder='static', static_url_path='')

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD'), # Lấy từ file .env
    'database': os.getenv('DB_NAME', 'mini_netflix')
}

# =====================================================================
# HÀM TRỢ GIÚP TRUY VẤN
# =====================================================================
def query(sql, params=()):
    """Chạy SELECT và trả về list các dict."""
    conn = mysql.connector.connect(**DB_CONFIG)
    cur = conn.cursor(dictionary=True)
    cur.execute(sql, params)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def execute(sql, params=()):
    """Chạy INSERT/UPDATE/DELETE. Trả về (bool, message)."""
    conn = mysql.connector.connect(**DB_CONFIG)
    try:
        cur = conn.cursor()
        cur.execute(sql, params)
        conn.commit()
        return True, "Thành công!"
    except Error as err:
        # Bắt lỗi từ Trigger (BR-01, BR-09...)
        return False, f"[{err.errno}] {err.msg}"
    finally:
        conn.close()

# =====================================================================
# 1. SERVE GIAO DIỆN HTML
# =====================================================================
@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

# =====================================================================
# 2. API CỔNG NGƯỜI DÙNG (USER PORTAL)
# =====================================================================

@app.route('/api/auth/accounts', methods=['GET'])
def get_accounts():
    sql = """
        SELECT ua.account_id, ua.email, ua.account_status,
               st.tier_name, st.max_profiles_allowed, st.resolution
        FROM user_account ua
        INNER JOIN subscription_tier st ON ua.tier_id = st.tier_id
        ORDER BY ua.account_id;
    """
    return jsonify(query(sql))

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    # Demo: Kiểm tra password đơn giản (giống app.py)
    acc = query("SELECT account_id, account_status FROM user_account WHERE email = %s", (email,))
    if not acc:
        return jsonify({"message": "Tài khoản không tồn tại."}), 401
        
    acc = acc[0]
    if acc['account_status'] != 'ACTIVE':
        return jsonify({"message": f"🚫 Tài khoản đang ở trạng thái {acc['account_status']}!"}), 403
        
    return jsonify({"account_id": acc['account_id'], "message": "Đăng nhập thành công"})

@app.route('/api/profiles', methods=['GET'])
def get_profiles():
    account_id = request.args.get('account_id')
    profiles = query("SELECT * FROM profile WHERE account_id = %s ORDER BY profile_id;", (account_id,))
    return jsonify(profiles)

@app.route('/api/profiles', methods=['POST'])
def create_profile():
    data = request.json
    ok, msg = execute(
        "INSERT INTO profile (account_id, profile_name, avatar_url, is_kids) VALUES (%s, %s, %s, %s)",
        (data['account_id'], data['profile_name'], "https://cdn.mininetflix.vn/avatars/default.png", data['is_kids'])
    )
    if ok:
        return jsonify({"message": "Tạo hồ sơ thành công"}), 201
    return jsonify({"error": f"TRIGGER MYSQL ĐÃ CHẶN: {msg}"}), 400

@app.route('/api/profiles/<int:profile_id>', methods=['DELETE'])
def delete_profile(profile_id):
    ok, msg = execute("DELETE FROM profile WHERE profile_id = %s", (profile_id,))
    if ok:
        return jsonify({"message": "Đã xóa hồ sơ"})
    return jsonify({"error": msg}), 400

@app.route('/api/catalog', methods=['GET'])
def get_catalog():
    search = request.args.get('q', '')
    genre = request.args.get('genre', '')
    ctype = request.args.get('type', '')
    lang = request.args.get('lang', '')
    is_kids = request.args.get('kids') == 'true'

    # Xây dựng câu SQL động y hệt app.py
    sql = """
        SELECT v.*, c.description, c.language_code
        FROM vw_content_full_catalog v
        INNER JOIN content c ON v.content_id = c.content_id
        WHERE (v.title LIKE %s OR c.description LIKE %s)
    """
    params = [f"%{search}%", f"%{search}%"]

    if is_kids:
        sql += " AND v.rating_age NOT IN ('R', 'NC-17')"
    if genre:
        sql += " AND v.content_id IN (SELECT cg.content_id FROM content_genre cg INNER JOIN genre g ON cg.genre_id = g.genre_id WHERE g.genre_name = %s)"
        params.append(genre)
    if ctype:
        sql += " AND v.content_type = %s"
        params.append(ctype)
    if lang:
        sql += " AND c.language_code = %s"
        params.append(lang)

    sql += " ORDER BY v.release_year DESC, v.title ASC;"
    return jsonify(query(sql, tuple(params)))

@app.route('/api/content/<int:content_id>', methods=['GET'])
def get_content_detail(content_id):
    sql = """
        SELECT v.*, c.description
        FROM vw_content_full_catalog v
        INNER JOIN content c ON v.content_id = c.content_id
        WHERE v.content_id = %s
    """
    rows = query(sql, (content_id,))
    if not rows: return jsonify({"error": "Không tìm thấy"}), 404
    
    item = rows[0]
    if item['content_type'] == 'TV_SERIES':
        item['seasons'] = query("SELECT season_id, season_number, season_name FROM season WHERE content_id = %s ORDER BY season_number;", (content_id,))
        
    return jsonify(item)

@app.route('/api/watchlist', methods=['GET'])
def get_watchlist():
    profile_id = request.args.get('profile_id')
    sql = """
        SELECT w.content_id, c.title, c.content_type, c.rating_age
        FROM watchlist w
        INNER JOIN content c ON w.content_id = c.content_id
        WHERE w.profile_id = %s ORDER BY w.added_at DESC;
    """
    return jsonify(query(sql, (profile_id,)))

@app.route('/api/watchlist', methods=['POST', 'DELETE'])
def toggle_watchlist():
    data = request.json
    profile_id = data['profile_id']
    content_id = data['content_id']
    
    if request.method == 'POST':
        ok, msg = execute("INSERT INTO watchlist (profile_id, content_id, added_at) VALUES (%s, %s, NOW())", (profile_id, content_id))
        if ok: return jsonify({"action": "added"})
    else:
        ok, msg = execute("DELETE FROM watchlist WHERE profile_id = %s AND content_id = %s", (profile_id, content_id))
        if ok: return jsonify({"action": "removed"})
        
    return jsonify({"error": msg}), 400

@app.route('/api/watch-history', methods=['GET'])
def get_history():
    profile_id = request.args.get('profile_id')
    sql = """
        SELECT wh.history_id, c.content_id, c.title, c.content_type, c.rating_age,
               COALESCE(CONCAT('Mùa ', s.season_number, ' - Tập ', ep.episode_number, ': ', ep.episode_title), 'Phim lẻ nguyên bản') AS episode_info,
               wh.stopped_position_seconds, wh.is_completed, wh.last_watched_timestamp
        FROM watch_history wh
        INNER JOIN content c ON wh.content_id = c.content_id
        LEFT JOIN tv_episode ep ON wh.episode_id = ep.episode_id
        LEFT JOIN season s ON ep.season_id = s.season_id
        WHERE wh.profile_id = %s ORDER BY wh.last_watched_timestamp DESC;
    """
    return jsonify(query(sql, (profile_id,)))

@app.route('/api/watch-history', methods=['POST'])
def save_history():
    data = request.json
    profile_id = data['profile_id']
    content_id = data['content_id']
    episode_id = data.get('episode_id') # Có thể None
    stopped_sec = data['stopped_seconds']
    is_completed = data['is_completed']

    # Kiểm tra xem đã có record chưa (giống app.py)
    existing = query("SELECT history_id FROM watch_history WHERE profile_id = %s AND content_id = %s", (profile_id, content_id))
    
    if not existing:
        ok, msg = execute("""
            INSERT INTO watch_history (profile_id, content_id, episode_id, last_watched_timestamp, stopped_position_seconds, is_completed)
            VALUES (%s, %s, %s, NOW(), %s, %s)
        """, (profile_id, content_id, episode_id, stopped_sec, is_completed))
    else:
        ok, msg = execute("""
            UPDATE watch_history SET episode_id = %s, last_watched_timestamp = NOW(), stopped_position_seconds = %s, is_completed = %s
            WHERE profile_id = %s AND content_id = %s
        """, (episode_id, stopped_sec, is_completed, profile_id, content_id))

    if ok: return jsonify({"message": "Lưu thành công"})
    return jsonify({"error": f"TRIGGER CHẶN (BR-09): {msg}"}), 400


# =====================================================================
# 3. API CỔNG QUẢN TRỊ (ADMIN & DBA PORTAL)
# =====================================================================

@app.route('/api/admin/users', methods=['GET'])
def admin_get_users():
    sql = """
        SELECT ua.account_id, ua.email, ua.password_hash, ua.registration_date,
               ua.account_status, st.tier_name, st.monthly_price, st.max_profiles_allowed,
               COUNT(p.profile_id) AS current_profiles_count,
               GROUP_CONCAT(CONCAT(p.profile_name, IF(p.is_kids, ' (Kids)', '')) SEPARATOR ', ') AS profiles_list
        FROM user_account ua
        INNER JOIN subscription_tier st ON ua.tier_id = st.tier_id
        LEFT JOIN profile p ON ua.account_id = p.account_id
        GROUP BY ua.account_id, ua.email, ua.password_hash, ua.registration_date,
                 ua.account_status, st.tier_name, st.monthly_price, st.max_profiles_allowed
        ORDER BY ua.account_id;
    """
    return jsonify(query(sql))

@app.route('/api/admin/users/<int:account_id>', methods=['PATCH'])
def admin_update_user(account_id):
    data = request.json
    ok, msg = execute(
        "UPDATE user_account SET account_status = %s, tier_id = %s WHERE account_id = %s",
        (data['status'], data['tier_id'], account_id)
    )
    if ok: return jsonify({"message": "Cập nhật thành công"})
    return jsonify({"error": msg}), 400

@app.route('/api/admin/tiers', methods=['GET'])
def admin_get_tiers():
    return jsonify(query("SELECT tier_id, tier_name FROM subscription_tier ORDER BY tier_id;"))

@app.route('/api/admin/content', methods=['POST'])
def admin_add_content():
    data = request.json
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # 1. Insert CONTENT
        cur.execute("""
            INSERT INTO content (title, description, release_year, rating_age, content_type, language_code)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (data['title'], data['description'], data['release_year'], data['rating_age'], data['content_type'], data['language_code']))
        new_cid = cur.lastrowid

        # 2. Insert MOVIE hoặc TV_SERIES
        if data['content_type'] == 'MOVIE':
            cur.execute("INSERT INTO movie (content_id, duration_minutes, video_resolution) VALUES (%s, %s, %s)",
                        (new_cid, data['duration_minutes'], data['video_resolution']))
        else:
            cur.execute("INSERT INTO tv_series (content_id, total_seasons, series_status) VALUES (%s, %s, %s)",
                        (new_cid, data['total_seasons'], data['series_status']))

        # 3. Insert CONTENT_GENRE
        for gid in data['genre_ids']:
            cur.execute("INSERT INTO content_genre (content_id, genre_id) VALUES (%s, %s)", (new_cid, gid))

        conn.commit()
        return jsonify({"message": f"Đã thêm '{data['title']}' thành công", "content_id": new_cid}), 201
    except Error as err:
        conn.rollback()
        return jsonify({"error": err.msg}), 400
    finally:
        conn.close()

@app.route('/api/admin/tables/<table_name>', methods=['GET'])
def admin_get_table(table_name):
    # Bảo mật cơ bản: Chỉ cho phép select từ các bảng có thật
    allowed_tables = [
        "subscription_tier", "user_account", "profile", "language", "genre",
        "content", "content_genre", "movie", "tv_series", "season",
        "tv_episode", "watchlist", "watch_history",
        "vw_content_full_catalog", "vw_subscription_revenue_summary"
    ]
    if table_name not in allowed_tables:
        return jsonify({"error": "Bảng không hợp lệ"}), 400
        
    # Lấy tối đa 500 dòng để tránh treo web
    return jsonify(query(f"SELECT * FROM {table_name} LIMIT 500;"))

@app.route('/api/admin/analytics/<int:query_id>', methods=['GET'])
def admin_run_analytics(query_id):
    queries = {
        1: """SELECT c.content_id, c.title AS movie_title, c.release_year, c.rating_age, l.language_name AS original_language, m.duration_minutes, m.video_resolution, GROUP_CONCAT(g.genre_name ORDER BY g.genre_name SEPARATOR ', ') AS genres FROM content c INNER JOIN movie m ON c.content_id = m.content_id INNER JOIN language l ON c.language_code = l.language_code INNER JOIN content_genre cg ON c.content_id = cg.content_id INNER JOIN genre g ON cg.genre_id = g.genre_id WHERE m.video_resolution = '4K' GROUP BY c.content_id, c.title, c.release_year, c.rating_age, l.language_name, m.duration_minutes, m.video_resolution ORDER BY c.release_year DESC;""",
        2: """SELECT c.title AS series_title, tv.series_status, s.season_number, s.season_name, ep.episode_number, ep.episode_title, ep.duration_minutes FROM content c INNER JOIN tv_series tv ON c.content_id = tv.content_id INNER JOIN season s ON tv.content_id = s.content_id INNER JOIN tv_episode ep ON s.season_id = ep.season_id ORDER BY c.title ASC, s.season_number ASC, ep.episode_number ASC;""",
        3: """SELECT p.profile_name, c.title AS content_title, c.content_type, COALESCE(CONCAT('Mùa ', s.season_number, ' - Tập ', ep.episode_number, ': ', ep.episode_title), 'Phim lẻ nguyên bản') AS current_episode_info, ROUND(wh.stopped_position_seconds / 60, 1) AS stopped_at_minute, wh.last_watched_timestamp FROM watch_history wh INNER JOIN profile p ON wh.profile_id = p.profile_id INNER JOIN content c ON wh.content_id = c.content_id LEFT JOIN tv_episode ep ON wh.episode_id = ep.episode_id LEFT JOIN season s ON ep.season_id = s.season_id WHERE wh.is_completed = FALSE ORDER BY wh.last_watched_timestamp DESC;""",
        4: """SELECT c.content_id, c.title, c.content_type, c.rating_age, COUNT(wh.history_id) AS total_views, SUM(CASE WHEN wh.is_completed = TRUE THEN 1 ELSE 0 END) AS completed_views FROM content c INNER JOIN watch_history wh ON c.content_id = wh.content_id GROUP BY c.content_id, c.title, c.content_type, c.rating_age ORDER BY total_views DESC, completed_views DESC LIMIT 5;""",
        5: """SELECT st.tier_name, st.monthly_price, COUNT(DISTINCT ua.account_id) AS active_accounts, COUNT(p.profile_id) AS total_profiles_created, COUNT(DISTINCT ua.account_id) * st.monthly_price AS monthly_revenue_vnd FROM subscription_tier st LEFT JOIN user_account ua ON st.tier_id = ua.tier_id AND ua.account_status = 'ACTIVE' LEFT JOIN profile p ON ua.account_id = p.account_id GROUP BY st.tier_id, st.tier_name, st.monthly_price ORDER BY monthly_revenue_vnd DESC;""",
        6: """SELECT ua.email AS account_email, p.profile_name, p.is_kids, COUNT(wh.history_id) AS total_titles_watched, ROUND(SUM(wh.stopped_position_seconds) / 60.0, 1) AS total_minutes_streamed, ROUND(AVG(CASE WHEN wh.is_completed = TRUE THEN 100.0 ELSE 0.0 END), 1) AS completion_rate_percent FROM profile p INNER JOIN user_account ua ON p.account_id = ua.account_id INNER JOIN watch_history wh ON p.profile_id = wh.profile_id GROUP BY ua.email, p.profile_id, p.profile_name, p.is_kids ORDER BY total_minutes_streamed DESC;""",
        7: """SELECT p.profile_name, c.title AS unwatched_saved_title, c.content_type, w.added_at AS saved_to_watchlist_at FROM watchlist w INNER JOIN profile p ON w.profile_id = p.profile_id INNER JOIN content c ON w.content_id = c.content_id WHERE NOT EXISTS (SELECT 1 FROM watch_history wh WHERE wh.profile_id = w.profile_id AND wh.content_id = w.content_id) ORDER BY w.added_at ASC;""",
        8: """SELECT c.title, c.release_year, m.duration_minutes, (SELECT ROUND(AVG(duration_minutes), 1) FROM movie) AS system_avg_duration FROM content c INNER JOIN movie m ON c.content_id = m.content_id WHERE m.duration_minutes > (SELECT AVG(duration_minutes) FROM movie) ORDER BY m.duration_minutes DESC;""",
        9: """SELECT g.genre_name, COUNT(DISTINCT cg.content_id) AS total_catalog_titles, COUNT(wh.history_id) AS total_stream_views FROM genre g LEFT JOIN content_genre cg ON g.genre_id = cg.genre_id LEFT JOIN watch_history wh ON cg.content_id = wh.content_id GROUP BY g.genre_id, g.genre_name HAVING COUNT(wh.history_id) > 0 ORDER BY total_stream_views DESC, total_catalog_titles DESC;""",
        10: """SELECT c.content_id, c.title, c.content_type, c.rating_age, l.language_name, GROUP_CONCAT(g.genre_name SEPARATOR ', ') AS genres FROM content c INNER JOIN language l ON c.language_code = l.language_code INNER JOIN content_genre cg ON c.content_id = cg.content_id INNER JOIN genre g ON cg.genre_id = g.genre_id WHERE c.rating_age NOT IN ('R', 'NC-17') GROUP BY c.content_id, c.title, c.content_type, c.rating_age, l.language_name ORDER BY c.rating_age ASC, c.title ASC;"""
    }
    
    if query_id not in queries:
        return jsonify({"error": "Query ID không hợp lệ"}), 400
        
    try:
        return jsonify(query(queries[query_id]))
    except Error as err:
        return jsonify({"error": err.msg}), 400

if __name__ == '__main__':
    print("🚀 Đang khởi chạy Mini-Netflix API tại http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
