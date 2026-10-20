import streamlit as st
import mysql.connector
import pandas as pd

# =====================================================================
# CẤU HÌNH TRANG & GIAO DIỆN NETFLIX DARK MODE CSS
# =====================================================================
st.set_page_config(
    page_title="Mini-Netflix | G12 Streaming & Admin Portal",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .stApp { background-color: #141414; color: #FFFFFF; }
    .netflix-logo {
        color: #E50914; font-size: 36px; font-weight: 900;
        letter-spacing: 2px; margin-bottom: 5px;
    }
    .movie-card {
        background-color: #1f1f1f; border-radius: 10px; padding: 16px;
        margin-bottom: 16px; border: 1px solid #333333;
        box-shadow: 0 4px 10px rgba(0,0,0,0.6);
    }
    .badge-type {
        background-color: #E50914; color: white; padding: 2px 8px;
        border-radius: 4px; font-size: 11px; font-weight: bold; margin-right: 6px;
    }
    .badge-age {
        background-color: #444444; color: #FFD700; padding: 2px 8px;
        border-radius: 4px; font-size: 11px; font-weight: bold; margin-right: 6px;
        border: 1px solid #FFD700;
    }
    .badge-res {
        background-color: #0071eb; color: white; padding: 2px 8px;
        border-radius: 4px; font-size: 11px; font-weight: bold;
    }
    .profile-box {
        background: linear-gradient(135deg, #2b2b2b, #1a1a1a);
        border: 2px solid #444; border-radius: 12px; padding: 18px;
        text-align: center; margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# =====================================================================
# KẾT NỐI MYSQL & HÀM TRợ GIÚP TRUY VẤN
# =====================================================================
DEFAULT_DB_PASS = "123"  # <-- Điền mật khẩu root MySQL của bạn tại đây (hoặc nhập trên Sidebar)

if "db_pass" not in st.session_state:
    st.session_state.db_pass = DEFAULT_DB_PASS
if "logged_account" not in st.session_state:
    st.session_state.logged_account = None
if "active_profile" not in st.session_state:
    st.session_state.active_profile = None
if "selected_content_id" not in st.session_state:
    st.session_state.selected_content_id = None

def get_conn():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password=st.session_state.db_pass,
        database="mini_netflix"
    )

def query_df(sql, params=None):
    conn = get_conn()
    try:
        return pd.read_sql(sql, conn, params=params)
    finally:
        conn.close()

def execute_sql(sql, params=None):
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute(sql, params or ())
        conn.commit()
        return True, "Thành công!"
    except mysql.connector.Error as err:
        return False, f"Error Code {err.errno}: {err.msg}"
    finally:
        conn.close()

# =====================================================================
# SIDEBAR: ĐIỀU HƯỚNG CỔNG NGƯỜI DÙNG vs CỔNG ADMIN (RBAC)
# =====================================================================
with st.sidebar:
    st.markdown('<div class="netflix-logo">MINI-NETFLIX</div>', unsafe_allow_html=True)
    st.caption("Đồ án Cơ sở dữ liệu - Nhóm G12")

    with st.expander("⚙️ Cấu hình kết nối MySQL", expanded=False):
        st.session_state.db_pass = st.text_input("Mật khẩu root MySQL:", value=st.session_state.db_pass, type="password")

    portal_mode = st.radio(
        "🔀 Chọn phân hệ truy cập (RBAC):",
        [
            "🍿 Cổng Người dùng (Streaming Client)",
            "🔐 Cổng Quản trị (Admin & DBA Portal)"
        ]
    )
    st.divider()

# Kiểm tra kết nối trước khi chạy
try:
    _test = get_conn()
    _test.close()
except Exception as e:
    st.error(f"⚠️ Không thể kết nối MySQL (`mini_netflix`). Hãy kiểm tra mật khẩu ở thanh bên trái! Chi tiết: {e}")
    st.stop()

# =====================================================================
# PHÂN HỆ 1: CỔNG NGƯỜI DÙNG XEM PHIM (STREAMING CLIENT)
# =====================================================================
if portal_mode == "🍿 Cổng Người dùng (Streaming Client)":

    # -----------------------------------------------------------------
    # BƯỚC 1: MÀN HÌNH ĐĂNG NHẬP TÀI KHOẢN (USER_ACCOUNT)
    # -----------------------------------------------------------------
    if st.session_state.logged_account is None:
        st.markdown("## 🔐 Đăng nhập Tài khoản Mini-Netflix")
        st.info("💡 Chọn nhanh 1 trong 5 tài khoản mẫu trong CSDL hoặc nhập Email để kiểm tra phân quyền gói cước & trạng thái tài khoản (`BR-05`, `FR-01`).")

        accounts_df = query_df("""
            SELECT ua.account_id, ua.email, ua.password_hash, ua.account_status,
                   ua.registration_date, st.tier_id, st.tier_name, st.monthly_price,
                   st.max_profiles_allowed, st.max_concurrent_streams, st.resolution
            FROM user_account ua
            INNER JOIN subscription_tier st ON ua.tier_id = st.tier_id
            ORDER BY ua.account_id;
        """)

        col_login, col_info = st.columns([1.2, 1.8])
        with col_login:
            email_options = accounts_df["email"].tolist()
            selected_email = st.selectbox(
                "Chọn Email tài khoản đăng nhập:",
                email_options,
                format_func=lambda x: f"{x} ({accounts_df[accounts_df['email']==x]['tier_name'].values[0]} - {accounts_df[accounts_df['email']==x]['account_status'].values[0]})"
            )
            pwd_input = st.text_input("Mật khẩu (Đã xác thực qua chuỗi Hash):", value="123456", type="password")

            if st.button("🚀 Đăng nhập vào hệ thống", use_container_width=True):
                acc_row = accounts_df[accounts_df["email"] == selected_email].iloc[0].to_dict()
                if acc_row["account_status"] != "ACTIVE":
                    st.error(f"🚫 Tài khoản `{selected_email}` hiện đang ở trạng thái `{acc_row['account_status']}`! Hệ thống từ chối truy cập.")
                else:
                    st.session_state.logged_account = acc_row
                    st.session_state.active_profile = None
                    st.rerun()

        with col_info:
            st.markdown("#### 📋 Danh sách Tài khoản mẫu trong CSDL hiện tại")
            st.dataframe(
                accounts_df[["account_id", "email", "tier_name", "max_profiles_allowed", "resolution", "account_status"]],
                use_container_width=True, hide_index=True
            )

    # -----------------------------------------------------------------
    # BƯỚC 2: MÀN HÌNH "AI ĐANG XEM?" (PROFILE SELECTION & CREATION - BR-01)
    # -----------------------------------------------------------------
    elif st.session_state.active_profile is None:
        acc = st.session_state.logged_account
        st.sidebar.success(f"👤 Tài khoản: **{acc['email']}**\n\n💎 Gói cước: **{acc['tier_name']} ({acc['resolution']})**")
        if st.sidebar.button("🚪 Đăng xuất tài khoản", use_container_width=True):
            st.session_state.logged_account = None
            st.rerun()

        st.markdown("<h1 style='text-align: center;'>👋 Ai đang xem? (Who's Watching?)</h1>", unsafe_allow_html=True)

        profiles_df = query_df(
            "SELECT * FROM profile WHERE account_id = %s ORDER BY profile_id;",
            params=(acc["account_id"],)
        )
        current_count = len(profiles_df)
        max_allowed = acc["max_profiles_allowed"]

        st.markdown(
            f"<p style='text-align: center; color: #aaa;'>Gói <b>{acc['tier_name']}</b> của bạn cho phép tạo tối đa <b>{max_allowed}</b> hồ sơ. Hiện đã tạo: <b>{current_count}/{max_allowed}</b> hồ sơ (Quy tắc <code>BR-01</code> & <code>FR-02</code>).</p>",
            unsafe_allow_html=True
        )
        st.write("")

        # Hiển thị các Profile hiện có thành các cột giống Netflix
        cols = st.columns(max(len(profiles_df), 1))
        for idx, row in profiles_df.iterrows():
            with cols[idx]:
                icon = "👶" if row["is_kids"] else "🧑"
                mode_label = "Hồ sơ Trẻ em (Kids - Chặn R/NC-17)" if row["is_kids"] else "Hồ sơ Người lớn (Full Catalog)"
                st.markdown(f"""
                <div class="profile-box">
                    <div style="font-size: 52px;">{icon}</div>
                    <h3 style="margin: 8px 0;">{row['profile_name']}</h3>
                    <p style="font-size: 12px; color: {'#46d369' if row['is_kids'] else '#aaa'};">{mode_label}</p>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"▶️ Chọn {row['profile_name']}", key=f"sel_prof_{row['profile_id']}", use_container_width=True):
                    st.session_state.active_profile = row.to_dict()
                    st.session_state.selected_content_id = None
                    st.rerun()
                if current_count > 1:
                    if st.button(f"🗑️ Xóa {row['profile_name']}", key=f"del_prof_{row['profile_id']}", use_container_width=True):
                        ok, msg = execute_sql("DELETE FROM profile WHERE profile_id = %s", (row["profile_id"],))
                        if ok:
                            st.rerun()

        st.divider()
        # Khu vực tạo thêm Profile mới (Kiểm chứng Trigger trg_check_profile_limit_before_insert)
        with st.expander(f"➕ Tạo thêm Hồ sơ mới (Hiện có {current_count}/{max_allowed} - Bấm thử khi đầy để test Trigger BR-01)", expanded=(current_count >= max_allowed)):
            c1, c2, c3 = st.columns([2, 1, 1])
            with c1:
                new_p_name = st.text_input("Tên hồ sơ mới:", placeholder="Ví dụ: Bé Na, Anh Hai...")
            with c2:
                new_p_kids = st.checkbox("👶 Đây là Hồ sơ Trẻ em (is_kids = TRUE)")
            with c3:
                st.write("")
                if st.button("➕ Tạo Hồ sơ vào CSDL", use_container_width=True):
                    if not new_p_name.strip():
                        st.warning("Vui lòng nhập tên hồ sơ!")
                    else:
                        ok, msg = execute_sql(
                            "INSERT INTO profile (account_id, profile_name, avatar_url, is_kids) VALUES (%s, %s, %s, %s)",
                            (acc["account_id"], new_p_name.strip(), "https://cdn.mininetflix.vn/avatars/default.png", new_p_kids)
                        )
                        if ok:
                            st.success(f"✅ Đã tạo hồ sơ '{new_p_name}' thành công!")
                            st.rerun()
                        else:
                            st.error(f"🚨 TRIGGER MYSQL ĐÃ CHẶN THAO TÁC (BR-01 / FR-02):\n\n`{msg}`")

    # -----------------------------------------------------------------
    # BƯỚC 3: MÀN HÌNH TRẢI NGHIỆM XEM PHIM NETFLIX ( SAU KHI CHỌN PROFILE )
    # -----------------------------------------------------------------
    else:
        acc = st.session_state.logged_account
        prof = st.session_state.active_profile
        is_kids = bool(prof["is_kids"])

        # Thông tin Profile đang xem ở Sidebar
        with st.sidebar:
            st.markdown(f"### {'👶' if is_kids else '🧑'} Hồ sơ: **{prof['profile_name']}**")
            if is_kids:
                st.warning("🛡️ **CHẾ ĐỘ TRẺ EM (`is_kids = TRUE`)**\n\nTheo quy tắc `BR-09`, hệ thống tự động lọc bỏ phim nhãn `R` & `NC-17` và kích hoạt Trigger bảo vệ.")
                bypass_filter_for_demo = st.checkbox("🛠️ [Demo Giảng viên] Hiện thử phim nhãn R trên kệ để bấm test Trigger chặn")
            else:
                st.info(f"💎 Gói **{acc['tier_name']}** • Độ phân giải tối đa: **{acc['resolution']}**")
                bypass_filter_for_demo = False

            if st.button("🔄 Đổi Hồ sơ xem (Switch Profile)", use_container_width=True):
                st.session_state.active_profile = None
                st.session_state.selected_content_id = None
                st.rerun()
            if st.button("🚪 Đăng xuất tài khoản", use_container_width=True):
                st.session_state.logged_account = None
                st.session_state.active_profile = None
                st.session_state.selected_content_id = None
                st.rerun()

        # Thanh Tìm kiếm & Bộ lọc Đa chiều chuẩn Netflix
        st.markdown(f"## 🍿 Khám phá Kho Phim Mini-Netflix — Xin chào, **{prof['profile_name']}**!")
        f_col1, f_col2, f_col3, f_col4 = st.columns([2.2, 1.3, 1.2, 1.2])

        with f_col1:
            search_text = st.text_input("🔍 Tìm kiếm tên phim hoặc nội dung mô tả:", placeholder="Gõ tên phim (VD: Inception, Squid Game, Doraemon...)")
        with f_col2:
            genres_list = ["Tất cả thể loại"] + query_df("SELECT genre_name FROM genre ORDER BY genre_name;")["genre_name"].tolist()
            selected_genre = st.selectbox("🎭 Phân loại Thể loại (GENRE):", genres_list)
        with f_col3:
            selected_type = st.selectbox("🎞️ Loại hình EER (CONTENT_TYPE):", ["Tất cả", "MOVIE (Phim lẻ)", "TV_SERIES (Phim bộ)"])
        with f_col4:
            langs_df = query_df("SELECT language_code, language_name FROM language ORDER BY language_name;")
            lang_options = ["Tất cả ngôn ngữ"] + [f"{r['language_name']} ({r['language_code']})" for _, r in langs_df.iterrows()]
            selected_lang = st.selectbox("🌐 Ngôn ngữ gốc (LANGUAGE):", lang_options)

        # Tabs trải nghiệm người dùng
        user_tab1, user_tab2, user_tab3 = st.tabs([
            "🎬 Kho Phim & Trình Phát (Browse & Stream)",
            "▶️ Tiếp tục xem & Lịch sử (Continue Watching - BR-06)",
            "❤️ Danh sách xem sau của tôi (My Watchlist - BR-07)"
        ])

        # -------------------------------------------------------------
        # TAB USER 1: DUYỆT KHO PHIM & BẤM XEM PHIM / CHỌN TẬP PHIM BỘ
        # -------------------------------------------------------------
        with user_tab1:
            # Xây dựng câu truy vấn động kết hợp View vw_content_full_catalog và bảng content
            sql_browse = """
                SELECT v.*, c.description, c.language_code
                FROM vw_content_full_catalog v
                INNER JOIN content c ON v.content_id = c.content_id
                WHERE (v.title LIKE %s OR c.description LIKE %s)
            """
            params_browse = [f"%{search_text}%", f"%{search_text}%"]

            # Lọc độ tuổi nếu là Hồ sơ Trẻ em (trừ khi bật công tắc test Trigger cho giảng viên)
            if is_kids and not bypass_filter_for_demo:
                sql_browse += " AND v.rating_age NOT IN ('R', 'NC-17')"

            if selected_genre != "Tất cả thể loại":
                sql_browse += """
                    AND v.content_id IN (
                        SELECT cg.content_id FROM content_genre cg
                        INNER JOIN genre g ON cg.genre_id = g.genre_id
                        WHERE g.genre_name = %s
                    )
                """
                params_browse.append(selected_genre)

            if selected_type == "MOVIE (Phim lẻ)":
                sql_browse += " AND v.content_type = 'MOVIE'"
            elif selected_type == "TV_SERIES (Phim bộ)":
                sql_browse += " AND v.content_type = 'TV_SERIES'"

            if selected_lang != "Tất cả ngôn ngữ":
                lang_code = selected_lang.split("(")[-1].replace(")", "")
                sql_browse += " AND c.language_code = %s"
                params_browse.append(lang_code)

            sql_browse += " ORDER BY v.release_year DESC, v.title ASC;"
            catalog_df = query_df(sql_browse, params=tuple(params_browse))

            # Lấy danh sách content_id đã có trong Watchlist của Profile này
            wl_ids = set(query_df("SELECT content_id FROM watchlist WHERE profile_id = %s", (prof["profile_id"],))["content_id"].tolist())

            st.caption(f"Tìm thấy **{len(catalog_df)}** tác phẩm phù hợp.")

            # Nếu người dùng đang bấm mở Trình phát (Player) cho 1 bộ phim cụ thể
            if st.session_state.selected_content_id is not None:
                sel_cid = st.session_state.selected_content_id
                detail_df = query_df("""
                    SELECT v.*, c.description
                    FROM vw_content_full_catalog v
                    INNER JOIN content c ON v.content_id = c.content_id
                    WHERE v.content_id = %s
                """, (sel_cid,))

                if not detail_df.empty:
                    item = detail_df.iloc[0]
                    st.markdown("---")
                    with st.container():
                        st.markdown(f"### 🎥 Đang mở Trình phát: **{item['title']}** ({item['release_year']}) — Nhãn `{item['rating_age']}`")
                        st.write(f"📝 **Tóm tắt:** {item['description']}")
                        st.write(f"🎭 **Thể loại:** {item['genres']} | 🌐 **Ngôn ngữ gốc:** {item['original_language']}")

                        selected_ep_id = None
                        max_seconds = 7200

                        # Phân nhánh EER: Nếu là TV_SERIES thì cho chọn Mùa (SEASON) và Tập (TV_EPISODE)
                        if item["content_type"] == "TV_SERIES":
                            st.info(f"📺 **Phim bộ nhiều tập (`TV_SERIES`)** • Tổng số mùa: **{int(item['series_total_seasons'])}** • Trạng thái: **{item['series_status']}**")
                            seasons_df = query_df(
                                "SELECT season_id, season_number, season_name, release_date FROM season WHERE content_id = %s ORDER BY season_number;",
                                (sel_cid,)
                            )
                            if not seasons_df.empty:
                                s_col, e_col = st.columns(2)
                                with s_col:
                                    sel_season_id = st.selectbox(
                                        "Chọn Mùa phát sóng (`SEASON`):",
                                        seasons_df["season_id"].tolist(),
                                        format_func=lambda sid: f"Mùa {seasons_df[seasons_df['season_id']==sid]['season_number'].values[0]}: {seasons_df[seasons_df['season_id']==sid]['season_name'].values[0]}"
                                    )
                                with e_col:
                                    eps_df = query_df(
                                        "SELECT episode_id, episode_number, episode_title, duration_minutes FROM tv_episode WHERE season_id = %s ORDER BY episode_number;",
                                        (sel_season_id,)
                                    )
                                    if not eps_df.empty:
                                        selected_ep_id = st.selectbox(
                                            "Chọn Tập phim (`TV_EPISODE`):",
                                            eps_df["episode_id"].tolist(),
                                            format_func=lambda eid: f"Tập {eps_df[eps_df['episode_id']==eid]['episode_number'].values[0]}: {eps_df[eps_df['episode_id']==eid]['episode_title'].values[0]} ({eps_df[eps_df['episode_id']==eid]['duration_minutes'].values[0]} phút)"
                                        )
                                        ep_dur = int(eps_df[eps_df["episode_id"] == selected_ep_id]["duration_minutes"].values[0])
                                        max_seconds = ep_dur * 60
                        else:
                            mov_dur = int(item["movie_duration_mins"]) if pd.notna(item["movie_duration_mins"]) else 120
                            max_seconds = mov_dur * 60
                            st.info(f"🎬 **Phim điện ảnh đơn lẻ (`MOVIE`)** • Thời lượng: **{mov_dur} phút** • Độ phân giải gốc: **{item['movie_resolution']}**")

                        p_col1, p_col2, p_col3 = st.columns([2, 1, 1])
                        with p_col1:
                            stopped_sec = st.slider("⏱️ Chọn vị trí dừng xem (giây) để lưu vào `WATCH_HISTORY`:", 0, max_seconds, min(1200, max_seconds))
                        with p_col2:
                            mark_done = st.checkbox("✅ Đánh dấu đã xem xong (`is_completed = TRUE`)", value=(stopped_sec >= max_seconds))
                        with p_col3:
                            if st.button("💾 Lưu tiến trình xem (Ghi vào CSDL)", use_container_width=True):
                                # Kiểm tra xem đã có bản ghi (profile_id, content_id) trong watch_history chưa
                                existing_wh = query_df(
                                    "SELECT history_id FROM watch_history WHERE profile_id = %s AND content_id = %s",
                                    (prof["profile_id"], int(sel_cid))
                                )
                                if existing_wh.empty:
                                    # Chạy INSERT trực tiếp (Nếu là Kids xem phim R/NC-17, Trigger trg_check_kids_rating_before_watch sẽ chặn ngay!)
                                    ok, msg = execute_sql("""
                                        INSERT INTO watch_history (profile_id, content_id, episode_id, last_watched_timestamp, stopped_position_seconds, is_completed)
                                        VALUES (%s, %s, %s, NOW(), %s, %s)
                                    """, (prof["profile_id"], int(sel_cid), selected_ep_id, stopped_sec, mark_done))
                                else:
                                    # Cập nhật trạng thái xem gần nhất (BR-06 / FR-05)
                                    ok, msg = execute_sql("""
                                        UPDATE watch_history
                                        SET episode_id = %s, last_watched_timestamp = NOW(),
                                            stopped_position_seconds = %s, is_completed = %s
                                        WHERE profile_id = %s AND content_id = %s
                                    """, (selected_ep_id, stopped_sec, mark_done, prof["profile_id"], int(sel_cid)))

                                if ok:
                                    st.success("✅ Đã lưu tiến trình xem vào bảng `watch_history`!")
                                else:
                                    st.error(f"🚨 TRIGGER BẢO VỆ TRẺ EM (`BR-09`) ĐÃ CHẶN THAO TÁC:\n\n`{msg}`")

                        if st.button("✖️ Đóng Trình phát"):
                            st.session_state.selected_content_id = None
                            st.rerun()
                    st.markdown("---")

            # Hiển thị lưới các thẻ phim (Movie / Series Cards)
            grid_cols = st.columns(2)
            for idx, item in catalog_df.iterrows():
                with grid_cols[idx % 2]:
                    cid = int(item["content_id"])
                    is_movie = (item["content_type"] == "MOVIE")
                    type_badge = "🎬 MOVIE (Phim lẻ)" if is_movie else "📺 TV SERIES (Phim bộ)"
                    extra_info = f"{int(item['movie_duration_mins'])} phút • {item['movie_resolution']}" if is_movie else f"{int(item['series_total_seasons'])} Mùa • {item['series_status']}"
                    in_wl = cid in wl_ids

                    st.markdown(f"""
                    <div class="movie-card">
                        <div>
                            <span class="badge-type">{type_badge}</span>
                            <span class="badge-age">MPAA: {item['rating_age']}</span>
                            <span class="badge-res">{extra_info}</span>
                        </div>
                        <h3 style="margin: 10px 0 4px 0;">{item['title']} ({item['release_year']})</h3>
                        <p style="color: #ccc; font-size: 13px; margin-bottom: 6px;">🎭 <b>Thể loại:</b> {item['genres']} | 🌐 <b>Ngôn ngữ:</b> {item['original_language']}</p>
                        <p style="color: #999; font-size: 13px;">{item['description']}</p>
                    </div>
                    """, unsafe_allow_html=True)

                    btn_c1, btn_c2 = st.columns(2)
                    with btn_c1:
                        if st.button(f"▶️ Phát / Chọn tập: {item['title']}", key=f"play_{cid}", use_container_width=True):
                            st.session_state.selected_content_id = cid
                            st.rerun()
                    with btn_c2:
                        if in_wl:
                            if st.button("✔️ Đã có trong Watchlist (Bấm để xóa)", key=f"wl_del_{cid}", use_container_width=True):
                                execute_sql("DELETE FROM watchlist WHERE profile_id = %s AND content_id = %s", (prof["profile_id"], cid))
                                st.rerun()
                        else:
                            if st.button("➕ Thêm vào Danh sách xem (Watchlist)", key=f"wl_add_{cid}", use_container_width=True):
                                execute_sql("INSERT INTO watchlist (profile_id, content_id, added_at) VALUES (%s, %s, NOW())", (prof["profile_id"], cid))
                                st.rerun()

        # -------------------------------------------------------------
        # TAB USER 2: TIẾP TỤC XEM (CONTINUE WATCHING) & LỊCH SỬ XEM
        # -------------------------------------------------------------
        with user_tab2:
            st.subheader(f"▶️ Danh sách đang xem dở (`is_completed = FALSE`) của {prof['profile_name']}")
            cont_df = query_df("""
                SELECT wh.history_id, c.content_id, c.title AS 'Tên phim', c.content_type AS 'Loại hình',
                       c.rating_age AS 'Nhãn tuổi',
                       COALESCE(CONCAT('Mùa ', s.season_number, ' - Tập ', ep.episode_number, ': ', ep.episode_title), 'Phim lẻ nguyên bản') AS 'Tập đang xem dở',
                       ROUND(wh.stopped_position_seconds / 60, 1) AS 'Dừng ở phút thứ',
                       wh.last_watched_timestamp AS 'Thời điểm xem cuối'
                FROM watch_history wh
                INNER JOIN content c ON wh.content_id = c.content_id
                LEFT JOIN tv_episode ep ON wh.episode_id = ep.episode_id
                LEFT JOIN season s ON ep.season_id = s.season_id
                WHERE wh.profile_id = %s AND wh.is_completed = FALSE
                ORDER BY wh.last_watched_timestamp DESC;
            """, (prof["profile_id"],))

            if cont_df.empty:
                st.info("Hiện không có bộ phim nào đang xem dở.")
            else:
                st.dataframe(cont_df, use_container_width=True, hide_index=True)

            st.subheader(f"✅ Lịch sử các bộ phim đã xem hoàn tất (`is_completed = TRUE`)")
            done_df = query_df("""
                SELECT c.title AS 'Tên phim', c.content_type AS 'Loại hình',
                       COALESCE(CONCAT('Mùa ', s.season_number, ' - Tập ', ep.episode_number, ': ', ep.episode_title), 'Phim lẻ') AS 'Nội dung hoàn tất',
                       wh.last_watched_timestamp AS 'Ngày hoàn thành'
                FROM watch_history wh
                INNER JOIN content c ON wh.content_id = c.content_id
                LEFT JOIN tv_episode ep ON wh.episode_id = ep.episode_id
                LEFT JOIN season s ON ep.season_id = s.season_id
                WHERE wh.profile_id = %s AND wh.is_completed = TRUE
                ORDER BY wh.last_watched_timestamp DESC;
            """, (prof["profile_id"],))
            st.dataframe(done_df, use_container_width=True, hide_index=True)

        # -------------------------------------------------------------
        # TAB USER 3: DANH SÁCH XEM SAU (WATCHLIST) & PHIM CHƯA XEM
        # -------------------------------------------------------------
        with user_tab3:
            st.subheader(f"❤️ Danh sách lưu xem sau (`WATCHLIST`) của {prof['profile_name']}")
            my_wl_df = query_df("""
                SELECT w.content_id, c.title AS 'Tên phim', c.content_type AS 'Loại hình',
                       c.rating_age AS 'Nhãn tuổi', w.added_at AS 'Thời điểm lưu',
                       CASE WHEN EXISTS (
                           SELECT 1 FROM watch_history wh
                           WHERE wh.profile_id = w.profile_id AND wh.content_id = w.content_id
                       ) THEN 'Đã bấm xem' ELSE 'Chưa từng xem (Gợi ý xem ngay!)' END AS 'Trạng thái xem'
                FROM watchlist w
                INNER JOIN content c ON w.content_id = c.content_id
                WHERE w.profile_id = %s
                ORDER BY w.added_at DESC;
            """, (prof["profile_id"],))
            st.dataframe(my_wl_df, use_container_width=True, hide_index=True)


# =====================================================================
# PHÂN HỆ 2: CỔNG QUẢN TRỊ VIÊN HỆ THỐNG (ADMIN / CONTENT MANAGER / DBA)
# =====================================================================
else:
    st.markdown("## 🔐 CỔNG QUẢN TRỊ HỆ THỐNG MINI-NETFLIX (ADMIN & DBA PORTAL)")
    st.caption("Mô phỏng đặc quyền của `role_system_admin` và `role_content_manager` (Mục 5.2 RBAC): Truy xuất dữ liệu nhạy cảm người dùng, quản trị kho phim EER, chạy 10 truy vấn phân tích và kiểm tra mọi bảng.")

    adm_tab1, adm_tab2, adm_tab3, adm_tab4 = st.tabs([
        "👥 Quản trị Tài khoản & Dữ liệu nhạy cảm (User & Billing)",
        "🎬 Quản trị Kho Phim EER (Add Movie / TV Series)",
        "📊 10 Truy vấn Phân tích & Doanh thu (Analytics)",
        "🗄️ Trình Khám phá 13 Bảng & Chạy SQL Tùy ý (DBA Explorer)"
    ])

    # -----------------------------------------------------------------
    # TAB ADMIN 1: PULL DỮ LIỆU NHẠY CẢM NGƯỜI DÙNG & CẬP NHẬT GÓI CƯỚC
    # -----------------------------------------------------------------
    with adm_tab1:
        st.subheader("1. Bảng Dữ liệu Nhạy cảm Tài khoản Khách hàng (`USER_ACCOUNT` + `SUBSCRIPTION_TIER`)")
        st.caption("Chỉ `role_system_admin` mới có quyền xem `password_hash`, `email`, trạng thái thuê bao và số lượng Profile đã tạo (`role_content_manager` bị chặn hoàn toàn bảng này).")

        sensitive_users_df = query_df("""
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
        """)
        st.dataframe(sensitive_users_df, use_container_width=True, hide_index=True)

        st.divider()
        st.subheader("2. Thao tác Quản trị: Khóa/Mở khóa Tài khoản hoặc Nâng cấp Gói cước")
        u_col1, u_col2, u_col3, u_col4 = st.columns(4)
        with u_col1:
            target_acc = st.selectbox("Chọn Tài khoản:", sensitive_users_df["account_id"].tolist(),
                                      format_func=lambda aid: f"ID {aid}: {sensitive_users_df[sensitive_users_df['account_id']==aid]['email'].values[0]}")
        with u_col2:
            new_status = st.selectbox("Trạng thái (`account_status`):", ["ACTIVE", "SUSPENDED", "CANCELED"])
        with u_col3:
            tiers_df = query_df("SELECT tier_id, tier_name FROM subscription_tier ORDER BY tier_id;")
            new_tier = st.selectbox("Gói cước (`tier_id`):", tiers_df["tier_id"].tolist(),
                                    format_func=lambda tid: f"{tid} - {tiers_df[tiers_df['tier_id']==tid]['tier_name'].values[0]}")
        with u_col4:
            st.write("")
            if st.button("💾 Cập nhật Tài khoản", use_container_width=True):
                ok, msg = execute_sql(
                    "UPDATE user_account SET account_status = %s, tier_id = %s WHERE account_id = %s",
                    (new_status, new_tier, target_acc)
                )
                if ok:
                    st.success("✅ Đã cập nhật thông tin tài khoản thành công!")
                    st.rerun()
                else:
                    st.error(msg)

    # -----------------------------------------------------------------
    # TAB ADMIN 2: THÊM MỚI NỘI DUNG PHIM (FR-03 & FR-07)
    # -----------------------------------------------------------------
    with adm_tab2:
        st.subheader("➕ Thêm Tác phẩm Mới vào Cấu trúc Kế thừa EER (`CONTENT` -> `MOVIE` / `TV_SERIES` + `CONTENT_GENRE`)")
        with st.form("add_content_form"):
            c_title = st.text_input("Tiêu đề phim (`title`):", placeholder="Ví dụ: Oppenheimer")
            c_desc = st.text_area("Mô tả cốt truyện (`description`):", placeholder="Nhập tóm tắt nội dung...")
            fc1, fc2, fc3, fc4 = st.columns(4)
            with fc1:
                c_year = st.number_input("Năm phát hành (`release_year`):", min_value=1888, max_value=2100, value=2025)
            with fc2:
                c_rating = st.selectbox("Nhãn độ tuổi MPAA (`rating_age`):", ["G", "PG", "PG-13", "R", "NC-17"])
            with fc3:
                c_type = st.selectbox("Phân lớp EER (`content_type`):", ["MOVIE", "TV_SERIES"])
            with fc4:
                l_df = query_df("SELECT language_code, language_name FROM language;")
                c_lang = st.selectbox("Ngôn ngữ gốc (`language_code`):", l_df["language_code"].tolist(),
                                      format_func=lambda lc: f"{lc} ({l_df[l_df['language_code']==lc]['language_name'].values[0]})")

            g_df = query_df("SELECT genre_id, genre_name FROM genre ORDER BY genre_id;")
            selected_gids = st.multiselect(
                "Gán Thể loại (`CONTENT_GENRE` - M:N):",
                g_df["genre_id"].tolist(),
                default=[1],
                format_func=lambda gid: g_df[g_df["genre_id"] == gid]["genre_name"].values[0]
            )

            st.markdown("**Thông số chuyên biệt cho Phân lớp con (Subclass Attributes):**")
            sc1, sc2, sc3, sc4 = st.columns(4)
            with sc1:
                m_dur = st.number_input("[Nếu là MOVIE] Thời lượng (phút):", value=120)
            with sc2:
                m_res = st.selectbox("[Nếu là MOVIE] Độ phân giải:", ["4K", "2K", "1080p"])
            with sc3:
                tv_seasons = st.number_input("[Nếu là TV_SERIES] Tổng số mùa:", min_value=1, value=1)
            with sc4:
                tv_status = st.selectbox("[Nếu là TV_SERIES] Trạng thái:", ["ONGOING", "COMPLETED", "CANCELLED"])

            submitted = st.form_submit_button("🚀 Thêm Nội dung vào CSDL (Transaction EER)")
            if submitted:
                if not c_title.strip():
                    st.warning("Vui lòng nhập tiêu đề phim!")
                else:
                    try:
                        conn = get_conn()
                        cur = conn.cursor()
                        # 1. Insert vào siêu lớp CONTENT
                        cur.execute("""
                            INSERT INTO content (title, description, release_year, rating_age, content_type, language_code)
                            VALUES (%s, %s, %s, %s, %s, %s)
                        """, (c_title.strip(), c_desc.strip(), c_year, c_rating, c_type, c_lang))
                        new_cid = cur.lastrowid

                        # 2. Insert vào phân lớp MOVIE hoặc TV_SERIES (Option 8A)
                        if c_type == "MOVIE":
                            cur.execute("INSERT INTO movie (content_id, duration_minutes, video_resolution) VALUES (%s, %s, %s)",
                                        (new_cid, m_dur, m_res))
                        else:
                            cur.execute("INSERT INTO tv_series (content_id, total_seasons, series_status) VALUES (%s, %s, %s)",
                                        (new_cid, tv_seasons, tv_status))

                        # 3. Insert vào bảng trung gian CONTENT_GENRE
                        for gid in selected_gids:
                            cur.execute("INSERT INTO content_genre (content_id, genre_id) VALUES (%s, %s)", (new_cid, gid))

                        conn.commit()
                        conn.close()
                        st.success(f"✅ Đã thêm '{c_title}' (content_id = {new_cid}) vào bảng `content`, `{c_type.lower()}` và `content_genre` thành công!")
                    except mysql.connector.Error as err:
                        st.error(f"🚨 Lỗi CSDL: {err.msg}")

    # -----------------------------------------------------------------
    # TAB ADMIN 3: CHẠY 10 CÂU TRUY VẤN PHỨC TẠP & BÁO CÁO DOANH THU
    # -----------------------------------------------------------------
    with adm_tab3:
        st.subheader("💰 Báo cáo Doanh thu Thuê bao (`vw_subscription_revenue_summary`)")
        st.dataframe(query_df("SELECT * FROM vw_subscription_revenue_summary;"), use_container_width=True, hide_index=True)

        st.divider()
        st.subheader("📈 Trình chạy trực tiếp 10 Truy vấn Nghiệp vụ Phức tạp (Mục 4.2A Báo cáo)")
        queries_dict = {
            "Truy vấn 1 (Multi-table JOIN): Danh mục Phim lẻ (MOVIE) độ phân giải 4K kèm ngôn ngữ & thể loại": """
                SELECT c.content_id, c.title AS movie_title, c.release_year, c.rating_age,
                       l.language_name AS original_language, m.duration_minutes, m.video_resolution,
                       GROUP_CONCAT(g.genre_name ORDER BY g.genre_name SEPARATOR ', ') AS genres
                FROM content c
                INNER JOIN movie m ON c.content_id = m.content_id
                INNER JOIN language l ON c.language_code = l.language_code
                INNER JOIN content_genre cg ON c.content_id = cg.content_id
                INNER JOIN genre g ON cg.genre_id = g.genre_id
                WHERE m.video_resolution = '4K'
                GROUP BY c.content_id, c.title, c.release_year, c.rating_age, l.language_name, m.duration_minutes, m.video_resolution
                ORDER BY c.release_year DESC;
            """,
            "Truy vấn 2 (Hierarchical 4-Table JOIN): Chuỗi phân cấp CONTENT -> TV_SERIES -> SEASON -> TV_EPISODE": """
                SELECT c.title AS series_title, tv.series_status, s.season_number, s.season_name,
                       ep.episode_number, ep.episode_title, ep.duration_minutes
                FROM content c
                INNER JOIN tv_series tv ON c.content_id = tv.content_id
                INNER JOIN season s ON tv.content_id = s.content_id
                INNER JOIN tv_episode ep ON s.season_id = ep.season_id
                ORDER BY c.title ASC, s.season_number ASC, ep.episode_number ASC;
            """,
            "Truy vấn 3 (LEFT JOIN & Continuous Playback): Danh sách Continue Watching đang xem dở toàn hệ thống": """
                SELECT p.profile_name, c.title AS content_title, c.content_type,
                       COALESCE(CONCAT('Mùa ', s.season_number, ' - Tập ', ep.episode_number, ': ', ep.episode_title), 'Phim lẻ nguyên bản') AS current_episode_info,
                       ROUND(wh.stopped_position_seconds / 60, 1) AS stopped_at_minute, wh.last_watched_timestamp
                FROM watch_history wh
                INNER JOIN profile p ON wh.profile_id = p.profile_id
                INNER JOIN content c ON wh.content_id = c.content_id
                LEFT JOIN tv_episode ep ON wh.episode_id = ep.episode_id
                LEFT JOIN season s ON ep.season_id = s.season_id
                WHERE wh.is_completed = FALSE
                ORDER BY wh.last_watched_timestamp DESC;
            """,
            "Truy vấn 4 (GROUP BY & Aggregation): Top 5 nội dung ăn khách nhất hệ thống": """
                SELECT c.content_id, c.title, c.content_type, c.rating_age,
                       COUNT(wh.history_id) AS total_views,
                       SUM(CASE WHEN wh.is_completed = TRUE THEN 1 ELSE 0 END) AS completed_views
                FROM content c
                INNER JOIN watch_history wh ON c.content_id = wh.content_id
                GROUP BY c.content_id, c.title, c.content_type, c.rating_age
                ORDER BY total_views DESC, completed_views DESC LIMIT 5;
            """,
            "Truy vấn 5 (GROUP BY & Revenue Analysis): Thống kê tài khoản ACTIVE, tổng Profile và Doanh thu": """
                SELECT st.tier_name, st.monthly_price,
                       COUNT(DISTINCT ua.account_id) AS active_accounts,
                       COUNT(p.profile_id) AS total_profiles_created,
                       COUNT(DISTINCT ua.account_id) * st.monthly_price AS monthly_revenue_vnd
                FROM subscription_tier st
                LEFT JOIN user_account ua ON st.tier_id = ua.tier_id AND ua.account_status = 'ACTIVE'
                LEFT JOIN profile p ON ua.account_id = p.account_id
                GROUP BY st.tier_id, st.tier_name, st.monthly_price
                ORDER BY monthly_revenue_vnd DESC;
            """,
            "Truy vấn 6 (GROUP BY & Completion Rate): Tổng số phút xem và tỷ lệ xem hoàn thành (%) của từng Profile": """
                SELECT ua.email AS account_email, p.profile_name, p.is_kids,
                       COUNT(wh.history_id) AS total_titles_watched,
                       ROUND(SUM(wh.stopped_position_seconds) / 60.0, 1) AS total_minutes_streamed,
                       ROUND(AVG(CASE WHEN wh.is_completed = TRUE THEN 100.0 ELSE 0.0 END), 1) AS completion_rate_percent
                FROM profile p
                INNER JOIN user_account ua ON p.account_id = ua.account_id
                INNER JOIN watch_history wh ON p.profile_id = wh.profile_id
                GROUP BY ua.email, p.profile_id, p.profile_name, p.is_kids
                ORDER BY total_minutes_streamed DESC;
            """,
            "Truy vấn 7 (Correlated Subquery - NOT EXISTS): Phim nằm trong Watchlist nhưng Profile chưa từng bấm xem": """
                SELECT p.profile_name, c.title AS unwatched_saved_title, c.content_type, w.added_at AS saved_to_watchlist_at
                FROM watchlist w
                INNER JOIN profile p ON w.profile_id = p.profile_id
                INNER JOIN content c ON w.content_id = c.content_id
                WHERE NOT EXISTS (
                    SELECT 1 FROM watch_history wh
                    WHERE wh.profile_id = w.profile_id AND wh.content_id = w.content_id
                )
                ORDER BY w.added_at ASC;
            """,
            "Truy vấn 8 (Scalar Subquery): Các Phim lẻ có thời lượng dài hơn thời lượng trung bình toàn hệ thống": """
                SELECT c.title, c.release_year, m.duration_minutes,
                       (SELECT ROUND(AVG(duration_minutes), 1) FROM movie) AS system_avg_duration
                FROM content c
                INNER JOIN movie m ON c.content_id = m.content_id
                WHERE m.duration_minutes > (SELECT AVG(duration_minutes) FROM movie)
                ORDER BY m.duration_minutes DESC;
            """,
            "Truy vấn 9 (GROUP BY & HAVING): Thống kê mức độ phổ biến của từng Thể loại (GENRE)": """
                SELECT g.genre_name, COUNT(DISTINCT cg.content_id) AS total_catalog_titles,
                       COUNT(wh.history_id) AS total_stream_views
                FROM genre g
                LEFT JOIN content_genre cg ON g.genre_id = cg.genre_id
                LEFT JOIN watch_history wh ON cg.content_id = wh.content_id
                GROUP BY g.genre_id, g.genre_name
                HAVING COUNT(wh.history_id) > 0
                ORDER BY total_stream_views DESC, total_catalog_titles DESC;
            """,
            "Truy vấn 10 (Kids Safe Catalog Filter - BR-09): Danh mục phim an toàn cho Trẻ em": """
                SELECT c.content_id, c.title, c.content_type, c.rating_age, l.language_name,
                       GROUP_CONCAT(g.genre_name SEPARATOR ', ') AS genres
                FROM content c
                INNER JOIN language l ON c.language_code = l.language_code
                INNER JOIN content_genre cg ON c.content_id = cg.content_id
                INNER JOIN genre g ON cg.genre_id = g.genre_id
                WHERE c.rating_age NOT IN ('R', 'NC-17')
                GROUP BY c.content_id, c.title, c.content_type, c.rating_age, l.language_name
                ORDER BY c.rating_age ASC, c.title ASC;
            """
        }

        chosen_q = st.selectbox("Chọn câu truy vấn trong báo cáo để chạy trực tiếp:", list(queries_dict.keys()))
        st.code(queries_dict[chosen_q].strip(), language="sql")
        st.dataframe(query_df(queries_dict[chosen_q]), use_container_width=True, hide_index=True)

    # -----------------------------------------------------------------
    # TAB ADMIN 4: PULL BẤT KỲ BẢNG NÀO & CHẠY SQL TRỰC TIẾP KHI VẤN ĐÁP
    # -----------------------------------------------------------------
    with adm_tab4:
        st.subheader("1. Trình Khám phá Toàn bộ 13 Bảng & 2 Views trong MySQL")
        all_tables = [
            "subscription_tier", "user_account", "profile", "language", "genre",
            "content", "content_genre", "movie", "tv_series", "season",
            "tv_episode", "watchlist", "watch_history",
            "vw_content_full_catalog", "vw_subscription_revenue_summary"
        ]
        chosen_tbl = st.selectbox("Chọn Bảng hoặc View muốn pull toàn bộ dữ liệu:", all_tables)
        st.dataframe(query_df(f"SELECT * FROM {chosen_tbl};"), use_container_width=True, hide_index=True)

        st.divider()
        st.subheader("2. Cửa sổ Thực thi SQL Tùy chỉnh (Dành cho Vấn đáp Trực tiếp & Kiểm tra EXPLAIN)")
        custom_sql = st.text_area(
            "Nhập câu lệnh SQL bất kỳ (SELECT, EXPLAIN, SHOW TRIGGERS, INSERT, DELETE...):",
            value="EXPLAIN SELECT content_id, title, release_year, rating_age FROM content WHERE title LIKE 'Inception%';",
            height=110
        )
        if st.button("⚡ Chạy câu lệnh SQL", use_container_width=True):
            sql_clean = custom_sql.strip()
            if sql_clean.upper().startswith(("SELECT", "EXPLAIN", "SHOW", "DESC")):
                try:
                    res_df = query_df(sql_clean)
                    st.success("✅ Truy vấn thực thi thành công!")
                    st.dataframe(res_df, use_container_width=True, hide_index=True)
                except Exception as err:
                    st.error(f"🚨 Lỗi SQL: {err}")
            else:
                ok, msg = execute_sql(sql_clean)
                if ok:
                    st.success(f"✅ Thực thi thành công: {msg}")
                else:
                    st.error(f"🚨 CSDL từ chối thao tác: {msg}")