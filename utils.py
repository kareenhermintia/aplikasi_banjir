# utils.py
import mysql.connector
import streamlit as st

# Fungsi untuk membuat koneksi ke database MySQL
def create_connection():
    return mysql.connector.connect(
        host=st.secrets["DB_HOST"],
        database=st.secrets["DB_DATABASE"],
        user=st.secrets["DB_USER"],
        password=st.secrets["DB_PASSWORD"]  # Ganti dengan nama database yang Anda buat
    )
