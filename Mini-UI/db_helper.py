import streamlit as st
import mysql.connector
import pandas as pd

# Hàm kết nối DB (chỉ chạy 1 lần nhờ cache)
@st.cache_resource
def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",       # Thay bằng host của bạn (vd: mysql-xxx.aivencloud.com)
            user="root",            # Thay bằng username
            password="123456",      # Thay bằng password
            database="csdl_g12"     # Thay bằng tên Database của nhóm bạn
        )
        return conn
    except mysql.connector.Error as e:
        st.error(f"Lỗi kết nối Database: {e}")
        return None

# Hàm lấy dữ liệu (Dùng cho SELECT)
def fetch_data(query, params=None):
    conn = get_db_connection()
    if conn:
        try:
            # Dùng pandas để lấy data cực nhanh
            df = pd.read_sql(query, conn, params=params)
            return df
        except Exception as e:
            st.error(f"Lỗi truy vấn: {e}")
            return pd.DataFrame()
    return pd.DataFrame()

# Hàm thực thi (Dùng cho INSERT, UPDATE, DELETE)
def execute_query(query, params=None):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
            conn.commit()
            return True, "Thành công"
        except mysql.connector.Error as e:
            # CỰC KỲ QUAN TRỌNG: Bắt lỗi từ Trigger (như lỗi giới hạn Profile) để hiện lên UI
            conn.rollback()
            return False, str(e)
        finally:
            cursor.close()
    return False, "Mất kết nối Database"
