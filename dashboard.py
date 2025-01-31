import streamlit as st
import pandas as pd
import mysql.connector
import plotly.express as px
from utils import create_connection  # Impor fungsi koneksi ke database

def show_dashboard():
    # **Header Dashboard**
    st.title("Dashboard Admin")
    st.markdown("Selamat datang di **Dashboard Admin**! Anda dapat mengelola data wilayah, melihat statistik bencana, dan hasil clustering di sini.")
    
    st.markdown("---")
    
    # **Kartu Statistik Utama**
    st.header("Statistik Utama 📊")
    try:
        # Koneksi ke database
        conn = create_connection()
        cursor = conn.cursor()
        
        # Query statistik data
        query_total_kejadian = "SELECT SUM(Jumlah_Kejadian) FROM wilayah_banjir"
        cursor.execute(query_total_kejadian)
        total_kejadian = cursor.fetchone()[0]
        total_kejadian = round(total_kejadian) if total_kejadian else 0  # Pembulatan
        
        query_total_korban = "SELECT SUM(Meninggal + Luka + Menderita_dan_Mengungsi) FROM wilayah_banjir"
        cursor.execute(query_total_korban)
        total_korban = cursor.fetchone()[0]
        total_korban = total_korban if total_korban else 0
        
        query_total_rumah = "SELECT SUM(Rumah_Terendam) FROM wilayah_banjir"
        cursor.execute(query_total_rumah)
        total_rumah = cursor.fetchone()[0]
        total_rumah = total_rumah if total_rumah else 0
        
        # Tampilkan kartu statistik
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Kejadian", f"{total_kejadian:,}")
        col2.metric("Total Korban", f"{total_korban:,}")
        col3.metric("Rumah Terdampak", f"{total_rumah:,}")
    except Exception as e:
        st.error(f"Error saat memuat statistik: {e}")
    finally:
        cursor.close()
        conn.close()
    
    st.markdown("---")
    
    # **Visualisasi Data**
    st.header("Visualisasi Data Wilayah 🌍")
    try:
        # Koneksi ke database dan ambil data wilayah
        conn = create_connection()
        cursor = conn.cursor()
        query = "SELECT Tahun, Provinsi, Jumlah_Kejadian, Meninggal, Luka, Menderita_dan_Mengungsi, Rumah_Terendam FROM wilayah_banjir"
        cursor.execute(query)
        data = cursor.fetchall()
        df = pd.DataFrame(data, columns=["Tahun", "Provinsi", "Jumlah Kejadian", "Meninggal", "Luka", "Mengungsi", "Rumah Terendam"])
        
        # Pilihan visualisasi
        viz_option = st.selectbox(
            "Pilih visualisasi data:",
            ["Jumlah Kejadian per Provinsi", "Korban (Meninggal, Luka, Mengungsi) per Provinsi"]
        )
        
        if viz_option == "Jumlah Kejadian per Provinsi":
            fig = px.bar(
                df,
                x="Provinsi",
                y="Jumlah Kejadian",
                color="Tahun",
                title="Jumlah Kejadian per Provinsi",
                labels={"Jumlah Kejadian": "Jumlah Kejadian (Bencana)"}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        elif viz_option == "Korban (Meninggal, Luka, Mengungsi) per Provinsi":
            korban_df = df.melt(
                id_vars=["Provinsi", "Tahun"],
                value_vars=["Meninggal", "Luka", "Mengungsi"],
                var_name="Kategori Korban",
                value_name="Jumlah"
            )
            fig = px.bar(
                korban_df,
                x="Provinsi",
                y="Jumlah",
                color="Kategori Korban",
                barmode="group",
                title="Korban (Meninggal, Luka, Mengungsi) per Provinsi",
                labels={"Jumlah": "Jumlah Korban"}
            )
            st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Error saat memuat visualisasi data: {e}")
    finally:
        cursor.close()
        conn.close()

    st.markdown("---")
    
    # **Info Lanjutan**
    st.header("Info dan Saran 💡")
    st.info("""
    - Pastikan data wilayah selalu diperbarui secara berkala.
    - Gunakan visualisasi untuk memahami pola data bencana dengan lebih baik.
    - Jangan ragu untuk kembali ke halaman data wilayah untuk menambah atau memperbarui data!
    """)

# Menjalankan dashboard
if __name__ == "__main__":
    show_dashboard()
