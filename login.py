# login.py
import streamlit as st
import mysql.connector
from utils import create_connection  # Impor fungsi create_connection

# Fungsi untuk memeriksa login
def check_login(username, password):
    conn = create_connection()  # Membuka koneksi menggunakan create_connection
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user

# Fungsi untuk menampilkan halaman login
def show_login():
    st.title("Login")
    st.write("Halaman login untuk admin.")
    
    # Input form login
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = check_login(username, password)
        if user:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.page = "Dashboard"  # Arahkan ke halaman dashboard setelah login berhasil
            st.success("Login berhasil!")
        else:
            st.error("Username atau password salah.")
