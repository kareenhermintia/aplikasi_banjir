import streamlit as st
import pandas as pd
import mysql.connector
from utils import create_connection  # Pastikan fungsi create_connection tersedia di file utils.py


# Fungsi untuk mengambil data dari database MySQL
def load_data_from_database():
    conn = create_connection()
    query = "SELECT * FROM wilayah_banjir"
    data = pd.read_sql(query, conn)
    conn.close()
    data['Tahun'] = data['Tahun'].astype(str)  # Pastikan kolom Tahun tidak menampilkan koma
    return data


# Fungsi untuk menyimpan data yang telah diedit ke database
def save_to_database(data):
    conn = create_connection()
    cursor = conn.cursor()

    for index, row in data.iterrows():
        cursor.execute("""
            UPDATE wilayah_banjir 
            SET 
                Tahun = %s, 
                Provinsi = %s, 
                KabKota = %s, 
                Jumlah_Kejadian = %s, 
                Meninggal = %s, 
                Luka = %s, 
                Menderita_dan_Mengungsi = %s, 
                Rumah_Terendam = %s
            WHERE id = %s
        """, (
            row['Tahun'], row['Provinsi'], row['KabKota'], row['Jumlah_Kejadian'], row['Meninggal'], 
            row['Luka'], row['Menderita_dan_Mengungsi'], row['Rumah_Terendam'], row['id']
        ))

    conn.commit()
    cursor.close()
    conn.close()


# Fungsi untuk menambahkan data baru ke database
def add_new_data(new_data):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO wilayah_banjir (Tahun, Provinsi, KabKota, Jumlah_Kejadian, Meninggal, Luka, 
                                    Menderita_dan_Mengungsi, Rumah_Terendam)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        new_data['Tahun'], new_data['Provinsi'], new_data['KabKota'], new_data['Jumlah_Kejadian'], 
        new_data['Meninggal'], new_data['Luka'], new_data['Menderita_dan_Mengungsi'], new_data['Rumah_Terendam']
    ))
    conn.commit()
    cursor.close()
    conn.close()


# Fungsi untuk menambahkan banyak data dari DataFrame ke database
def add_bulk_data(df):
    conn = create_connection()
    cursor = conn.cursor()
    for _, row in df.iterrows():
        cursor.execute("""
            INSERT INTO wilayah_banjir (Tahun, Provinsi, KabKota, Jumlah_Kejadian, Meninggal, Luka, 
                                        Menderita_dan_Mengungsi, Rumah_Terendam)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            row['Tahun'], row['Provinsi'], row['KabKota'], row['Jumlah_Kejadian'], 
            row['Meninggal'], row['Luka'], row['Menderita_dan_Mengungsi'], row['Rumah_Terendam']
        ))
    conn.commit()
    cursor.close()
    conn.close()


# Fungsi untuk menghapus data dari database
def delete_data(selected_id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM wilayah_banjir WHERE id = %s", (selected_id,))
    conn.commit()
    cursor.close()
    conn.close()


# Fungsi untuk menghapus seluruh data berdasarkan tahun
def delete_data_by_year(year):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM wilayah_banjir WHERE Tahun = %s", (year,))
    conn.commit()
    cursor.close()
    conn.close()


# Fungsi utama untuk menampilkan data dan mengelola operasi CRUD
def show_data_wilayah():
    st.title("Data Wilayah Banjir Pulau Jawa")

    # Ambil data dari database
    if "data" not in st.session_state or st.session_state.refresh:
        st.session_state.data = load_data_from_database()
        st.session_state.refresh = False
    data = st.session_state.data

    st.write("Dataframe wilayah banjir pulau jawa")
    st.dataframe(data, width=1000, height=500)

    # Pilih operasi
    operation = st.radio("Pilih Operasi:", ["Tambah Data", "Edit Data", "Hapus Data", "Upload Data"], horizontal=True)

    if operation == "Tambah Data":
        st.subheader("Tambah Data Baru")
        new_data = {}
        new_data['Tahun'] = st.number_input("Tahun:", min_value=2000, max_value=2050, value=2021)
        new_data['Provinsi'] = st.text_input("Provinsi:", placeholder="Contoh: Jawa Timur")
        new_data['KabKota'] = st.text_input("Kabupaten/Kota:", placeholder="Contoh: Surabaya")
        new_data['Jumlah_Kejadian'] = st.number_input("Jumlah Kejadian:", min_value=0, value=0)
        new_data['Meninggal'] = st.number_input("Meninggal:", min_value=0, value=0)
        new_data['Luka'] = st.number_input("Luka:", min_value=0, value=0)
        new_data['Menderita_dan_Mengungsi'] = st.number_input("Menderita dan Mengungsi:", min_value=0, value=0)
        new_data['Rumah_Terendam'] = st.number_input("Rumah Terendam:", min_value=0, value=0)
        if st.button("Tambahkan Data"):
            if new_data['Provinsi'] and new_data['KabKota']:
                add_new_data(new_data)
                st.success("Data baru berhasil ditambahkan ke database.")
                st.session_state.refresh = True
            else:
                st.error("Kolom Provinsi dan Kabupaten/Kota wajib diisi.")

    elif operation == "Upload Data":
        st.subheader("Upload Data Baru")
        uploaded_file = st.file_uploader("Unggah file CSV atau Excel:", type=["csv", "xlsx"])

        if uploaded_file is not None:
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith(".xlsx"):
                df = pd.read_excel(uploaded_file)

            st.write("Data yang diunggah:")
            df['Tahun'] = df['Tahun'].astype(str)
            st.dataframe(df)

            if st.button("Tambahkan Data ke Database"):
                add_bulk_data(df)
                st.success("Data berhasil diunggah dan disimpan ke database.")
                st.session_state.refresh = True

    elif operation == "Edit Data":
        st.subheader("Edit Data")
        selected_id = st.selectbox("Pilih ID untuk Diedit:", data['id'].tolist())
        row_to_edit = data[data['id'] == selected_id].iloc[0]
        edited_data = {}
        edited_data['Tahun'] = st.number_input("Tahun:", value=int(row_to_edit['Tahun']), min_value=2000, max_value=2050)
        edited_data['Provinsi'] = st.text_input("Provinsi:", value=row_to_edit['Provinsi'])
        edited_data['KabKota'] = st.text_input("Kabupaten/Kota:", value=row_to_edit['KabKota'])
        edited_data['Jumlah_Kejadian'] = st.number_input("Jumlah Kejadian:", value=int(row_to_edit['Jumlah_Kejadian']), min_value=0)
        edited_data['Meninggal'] = st.number_input("Meninggal:", value=int(row_to_edit['Meninggal']), min_value=0)
        edited_data['Luka'] = st.number_input("Luka:", value=int(row_to_edit['Luka']), min_value=0)
        edited_data['Menderita_dan_Mengungsi'] = st.number_input("Menderita:", value=int(row_to_edit['Menderita_dan_Mengungsi']), min_value=0)
        edited_data['Rumah_Terendam'] = st.number_input("Rumah Terendam:", value=int(row_to_edit['Rumah_Terendam']), min_value=0)
        if st.button("Simpan Perubahan"):
            for key in edited_data:
                data.loc[data['id'] == selected_id, key] = edited_data[key]
            save_to_database(data)
            st.success("Perubahan berhasil disimpan.")
            st.session_state.refresh = True

    elif operation == "Hapus Data":
        st.subheader("Hapus Data")

        # Filter berdasarkan Provinsi dan Tahun
        filter_provinsi = st.text_input("Filter berdasarkan Provinsi:", placeholder="Contoh: Jawa Timur")
        filter_tahun = st.number_input("Filter berdasarkan Tahun:", min_value=2000, max_value=2050, value=2021, step=1)

        # Menyaring data sesuai dengan input Provinsi dan Tahun
        filtered_data = data[
            (data['Provinsi'].str.contains(filter_provinsi, case=False, na=False)) &
            (data['Tahun'].astype(int) == filter_tahun)
        ]

        st.write("Hasil Filter:")
        st.dataframe(filtered_data, width=1200, height=400)

        # Pilih ID untuk dihapus
        selected_ids = st.multiselect(
            "Pilih ID untuk dihapus:",
            options=filtered_data['id'].tolist(),
            format_func=lambda x: f"ID {x}"
        )

        # Menghapus data berdasarkan ID yang dipilih
        if st.button("Hapus Data Terpilih"):
            if selected_ids:
                for selected_id in selected_ids:
                    delete_data(selected_id)
                st.success(f"Data dengan ID {', '.join(map(str, selected_ids))} berhasil dihapus.")
                st.session_state.refresh = True
            else:
                st.warning("Pilih setidaknya satu data untuk dihapus.")

        # Menambahkan tombol untuk menghapus seluruh data pada tahun tertentu
        # Konfirmasi sebelum menghapus
        confirm_delete = st.checkbox(f"Saya yakin ingin menghapus seluruh data untuk tahun {filter_tahun}")

        if confirm_delete and st.button("Hapus Semua Data Sekarang"):
            delete_data_by_year(filter_tahun)
            st.success(f"Seluruh data untuk tahun {filter_tahun} berhasil dihapus.")
            st.session_state.refresh = True

# Fungsi utama untuk menjalankan aplikasi
def main():
    if "refresh" not in st.session_state:
        st.session_state.refresh = False
    show_data_wilayah()


if __name__ == "__main__":
    main()
