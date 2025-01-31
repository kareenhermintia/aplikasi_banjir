import streamlit as st
import pandas as pd
import mysql.connector
from utils import create_connection  # Pastikan fungsi create_connection tersedia di file utils.py

# Fungsi untuk memuat data dari database
def load_data_from_database():
    conn = create_connection()  # Membuka koneksi
    query = "SELECT * FROM wilayah_banjir"
    data = pd.read_sql(query, conn)
    conn.close()  # Menutup koneksi setelah pengambilan data
    data['Tahun'] = data['Tahun'].astype(str)  # Pastikan kolom Tahun ditampilkan sebagai string
    return data

def show_mitigasi():
    """Halaman Langkah Mitigasi dan Data Wilayah."""
    st.title("Data Wilayah Banjir dan Langkah Mitigasi🌍🚨")

    # **Bagian Data Wilayah**
    st.header("Data Wilayah Banjir 🌍")
    try:
        # Koneksi ke database dan ambil data
        conn = create_connection()
        cursor = conn.cursor()

        # Query untuk mengambil kolom yang diperlukan
        query = """
        SELECT Tahun, Provinsi, KabKota, Jumlah_Kejadian, Meninggal, 
               Luka, Menderita_dan_Mengungsi, Rumah_Terendam 
        FROM wilayah_banjir
        """
        cursor.execute(query)
        data = cursor.fetchall()

        # Tampilkan data dalam tabel menggunakan DataFrame
        df = pd.DataFrame(data, columns=["Tahun", "Provinsi", "KabKota", "Jumlah_Kejadian", "Meninggal", "Luka", "Menderita_dan_Mengungsi", "Rumah_Terendam"])

        # Konversi kolom Tahun ke string agar tidak menampilkan koma
        df["Tahun"] = df["Tahun"].astype(str)

        # **Checkbox untuk menampilkan filter tahun**
        filter_tahun = st.checkbox("Filter Berdasarkan Tahun")

        if filter_tahun:
            # Menampilkan pilihan tahun jika checkbox dicentang
            tahun_terpilih = st.selectbox("Pilih Tahun", options=["Semua Tahun"] + list(df["Tahun"].unique()), index=0)

            if tahun_terpilih == "Semua Tahun":
                filtered_data = df
            else:
                # Filter data berdasarkan tahun yang dipilih
                filtered_data = df[df["Tahun"] == tahun_terpilih]
        else:
            # Menampilkan semua data jika checkbox tidak dicentang
            filtered_data = df

        # Tampilkan data yang telah difilter
        st.dataframe(filtered_data, use_container_width=True)

    except Exception as e:
        st.error(f"Error saat memuat data wilayah: {e}")
    finally:
        cursor.close()
        conn.close()

    # **Bagian Langkah Mitigasi**
    st.header("Langkah-Langkah Mitigasi Bencana 🚨")

    # Membuat layout grid untuk menampilkan langkah mitigasi
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 🧭 **Identifikasi Wilayah Rawan**")
        st.markdown("""    
        - Pahami wilayah risiko tinggi.
        - Analisis data wilayah terdampak banjir.
        - Fokuskan mitigasi pada daerah kritis.
        """)

    with col2:
        st.markdown("### 📢 **Edukasi dan Simulasi**")
        st.markdown("""    
        - Sosialisasikan langkah evakuasi.
        - Latihan evakuasi untuk kesiapsiagaan.
        - Pastikan masyarakat paham jalur evakuasi.
        """)

    with col3:
        st.markdown("### 🛠️ **Perbaikan Infrastruktur**")
        st.markdown("""    
        - Perkuat tanggul dan saluran air.
        - Pasang sistem peringatan dini.
        - Tingkatkan fasilitas publik darurat.
        """)

    # Membuat baris tambahan untuk langkah lainnya
    col4, col5 = st.columns(2)
    
    with col4:
        st.markdown("### 🌐 **Sistem Informasi Bencana**")
        st.markdown("""    
        - Pastikan informasi bencana tersampaikan real-time.
        - Gunakan aplikasi dan media sosial untuk update.
        - Sediakan nomor darurat yang mudah diakses.
        """)

    with col5:
        st.markdown("### 🤝 **Kolaborasi Stakeholder**")
        st.markdown("""    
        - Kerja sama antara pemerintah, swasta, dan masyarakat.
        - Libatkan organisasi lokal untuk distribusi bantuan.
        - Evaluasi dan perbaiki strategi mitigasi.
        """)

    # Tambahkan tautan ke informasi BNPB
    st.subheader("🔗 Informasi Mitigasi dari Website BNPB")
    st.markdown("""    
    Untuk informasi lebih lanjut terkait mitigasi bencana, kunjungi website resmi BNPB:
    - **[BNPB - Informasi Bencana](https://www.bnpb.go.id/)**: Sumber utama untuk data bencana dan mitigasi.
    - **[Peta Bencana BNPB](https://petabencana.id/)**: Platform berbasis peta untuk memahami risiko wilayah.
    - **[Panduan Mitigasi BNPB](https://www.bnpb.go.id/mitigasi)**: Panduan mitigasi yang lebih terperinci.
    """)

    st.info("Pastikan Anda memanfaatkan semua sumber daya yang tersedia dari BNPB untuk kesiapsiagaan bencana.")
