import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
from io import BytesIO
from mpl_toolkits.mplot3d import Axes3D
from utils import create_connection  # Impor fungsi koneksi ke database

# Fungsi untuk memuat data dari database
def load_data_from_database():
    conn = create_connection()  # Membuka koneksi
    query = "SELECT * FROM wilayah_banjir"
    data = pd.read_sql(query, conn)
    conn.close()  # Menutup koneksi setelah pengambilan data
    data['Tahun'] = data['Tahun'].astype(str)  # Pastikan kolom Tahun ditampilkan sebagai string
    return data

def show_cluster():
    st.title("Clustering Wilayah Berdasarkan Dampak Banjir")

    # Mengambil data dari database
    data = load_data_from_database()
    st.write("Dataset wilayah:")
    st.dataframe(data)  # Menampilkan seluruh data dalam bentuk tabel interaktif


    # Langkah 3: Data Understanding
    st.subheader("Info Dataset")
    st.write(data.info())
    st.subheader("Statistik Deskriptif")
    st.write(data.describe())

    # Langkah 4: Data Preparation
    features = data[['Jumlah_Kejadian', 'Menderita_dan_Mengungsi', 'Rumah_Terendam']]
    data['Menderita_dan_Mengungsi_log'] = np.log1p(data['Menderita_dan_Mengungsi'])
    features_transformed = data[['Jumlah_Kejadian', 'Menderita_dan_Mengungsi_log', 'Rumah_Terendam']]

    # Normalisasi data
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(features_transformed)

    # Langkah 5: Menentukan jumlah cluster optimal dengan metode Elbow
    st.subheader("Metode Elbow untuk Menentukan Jumlah Cluster")
    
    sse = []
    k_values = range(1, 11)
    for k in k_values:
         kmeans = KMeans(n_clusters=k, random_state=42)
         kmeans.fit(scaled_features)
         sse.append(kmeans.inertia_)

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(k_values, sse, marker='o')
    ax.set_title('Metode Elbow untuk Menentukan Jumlah Cluster')
    ax.set_xlabel('Jumlah Cluster')
    ax.set_ylabel('SSE')
    ax.grid(True)
    st.pyplot(fig)

    st.write("Metode Elbow digunakan untuk menentukan jumlah cluster optimal dengan melihat titik siku pada grafik SSE (Sum of Squared Errors). Jumlah cluster optimal adalah saat terjadi penurunan signifikan sebelum stabil. Dari grafik berikut, kita memilih jumlah cluster optimal sebanyak 3 karena setelah titik ini, penurunan SSE mulai melambat.")

    # Berdasarkan plot elbow, pilih jumlah cluster optimal (misalnya 3)
    optimal_k = 3

    # Langkah 6: Modeling - K-Means Clustering
    kmeans = KMeans(n_clusters=optimal_k, random_state=42)
    kmeans.fit(scaled_features)
    data['Cluster'] = kmeans.labels_

    # Ubah indeks cluster dari 0,1,2 menjadi 1,2,3
    data['Cluster'] = data['Cluster'] + 1

    # Memberikan nama pada cluster
    cluster_names = {
        1: 'Wilayah dengan dampak korban dan kerusakan ringan',
        2: 'Wilayah dengan dampak korban dan kerusakan sedang',
        3: 'Wilayah dengan dampak korban dan kerusakan berat'
    }
    data['Cluster_Name'] = data['Cluster'].map(cluster_names)

    st.subheader("Hasil Clustering")
    st.dataframe(data[['Provinsi','KabKota','Jumlah_Kejadian', 'Menderita_dan_Mengungsi', 'Rumah_Terendam', 'Cluster', 'Cluster_Name']])

    output_file = 'hasil_clustering_banjir.xlsx'

    # Menyimpan ke dalam BytesIO object dengan openpyxl
    towrite = BytesIO()
    with pd.ExcelWriter(towrite, engine='openpyxl') as writer:
        data.to_excel(writer, index=False, sheet_name='Cluster')

    towrite.seek(0)  # Kembali ke awal stream
    st.write(f"Hasil clustering disimpan dalam file: {output_file}")

    # Tombol download
    st.download_button("Download hasil clustering", towrite, file_name=output_file, mime="application/vnd.ms-excel")

    # Langkah 7: Evaluasi - Perhitungan Silhouette Score untuk 10 percobaan
    st.subheader("Evaluasi Model - Silhouette Score")
    sil_scores = []  # List untuk menyimpan hasil Silhouette Score dari setiap percobaan
    for i in range(10):
        kmeans_test = KMeans(n_clusters=optimal_k, random_state=i)
        kmeans_test.fit(scaled_features)
        score = silhouette_score(scaled_features, kmeans_test.labels_)
        sil_scores.append(score)
        st.write(f"Percobaan {i+1} - Silhouette Score: {score:.4f}")  # Menampilkan Silhouette Score setiap percobaan

    # Menghitung rata-rata Silhouette Score
    average_sil_score = np.mean(sil_scores)
    st.write(f"Rata-rata Silhouette Score dari 10 percobaan: {average_sil_score:.4f}")

    # Langkah 8: Visualisasi hasil clustering
    # # Scatter plot untuk visualisasi cluster (2D)
    # st.subheader("Visualisasi Cluster (2D)")
    # fig, ax = plt.subplots(figsize=(8, 6))
    # scatter = ax.scatter(scaled_features[:, 2], scaled_features[:, 1],
    #                      c=data['Cluster'], cmap='viridis', label='Cluster')
    # centroids = kmeans.cluster_centers_
    # ax.scatter(centroids[:, 2], centroids[:, 1], s=200, c='red', marker='X', label='Centroid')
    # ax.set_xlabel('Rumah Terendam (scaled)')
    # ax.set_ylabel('Menderita dan Mengungsi (scaled) log')
    # ax.set_title('Clustering Wilayah Berdasarkan Dampak Banjir (2D)')
    # fig.colorbar(scatter, label='Cluster')
    # ax.legend()
    # st.pyplot(fig)

    # Scatter plot untuk visualisasi cluster (3D)
   # Tab untuk visualisasi
    tab1, tab2, tab3 = st.tabs(["Visualisasi 3D", "Barchart Per Wilayah", "Pie Chart Per Cluster"])

    # Tab 1: Visualisasi 3D
    with tab1:
        st.subheader("Visualisasi Cluster (3D)")
        st.write("""
            Di tab ini, kita memvisualisasikan hasil clustering dalam bentuk grafik tiga dimensi (3D), 
            yang memungkinkan kita untuk melihat bagaimana wilayah-wilayah dikelompokkan berdasarkan tiga faktor utama: 
            Jumlah Kejadian, Menderita dan Mengungsi, serta Rumah Terendam. 
            Setiap titik di dalam grafik ini mewakili satu wilayah, dengan warna yang menunjukkan cluster yang berbeda. 
            Visualisasi ini membantu kita memahami sebaran geografis wilayah-wilayah yang mengalami dampak banjir dengan intensitas yang berbeda-beda.
        """)
        st.write("""
            **Keterangan warna:**
            - 🟣 **Ungu** → Cluster 1 (**Dampak Ringan**)
            - 🟢 **Hijau Kebiruan** → Cluster 2 (**Dampak Sedang**)
            - 🟡 **Kuning** → Cluster 3 (**Dampak Berat**)
            - ❌ **Merah X** → **Centroid (Titik Pusat Cluster)**
            """)
        fig1 = plt.figure(figsize=(6, 4))
        ax1 = fig1.add_subplot(111, projection='3d')
        scatter3d = ax1.scatter(scaled_features[:, 0], scaled_features[:, 1], scaled_features[:, 2],
                                c=data['Cluster'], cmap='viridis', label='Cluster')
        centroids = kmeans.cluster_centers_
        ax1.scatter(centroids[:, 0], centroids[:, 1], centroids[:, 2], s=200, c='red', marker='X', label='Centroid')
        ax1.set_xlabel('Jumlah Kejadian', fontsize=8)
        ax1.set_ylabel('Menderita dan Mengungsi', fontsize=8)
        ax1.set_zlabel('Rumah Terendam', fontsize=8)
        ax1.set_title('Clustering Wilayah Berdasarkan Dampak Banjir (3D)')
        ax1.legend()
        st.pyplot(fig1)

        # Definisikan data per cluster
        cluster1_data = data[data['Cluster'] == 1]
        cluster2_data = data[data['Cluster'] == 2]
        cluster3_data = data[data['Cluster'] == 3]


    # Tab 2: Barchart per wilayah berdasarkan cluster
    with tab2:
        st.subheader("Barchart Dampak Wilayah Berdasarkan Cluster")
        st.write("""
            Pada tab ini, kita menunjukkan bar chart untuk masing-masing cluster yang menggambarkan jumlah kejadian banjir di setiap provinsi. 
            Setiap cluster merepresentasikan wilayah dengan tingkat dampak yang berbeda, mulai dari ringan hingga berat. 
            Dengan melihat bar chart ini, pengguna dapat membandingkan secara langsung jumlah kejadian banjir di wilayah yang termasuk dalam setiap kategori dampak banjir,
            serta melihat perbedaan kejadian antarprovinsi dalam setiap cluster.
        """)
        fig2, (ax2_1, ax2_2, ax2_3) = plt.subplots(1, 3, figsize=(18, 6))

        # Cluster 1
        ax2_1.bar(cluster1_data['Provinsi'], cluster1_data['Jumlah_Kejadian'], color='lightblue')
        ax2_1.set_title('Cluster 1: Wilayah Dengan Dampak Ringan')
        ax2_1.set_xlabel('Provinsi')
        ax2_1.set_ylabel('Jumlah Kejadian')
        ax2_1.tick_params(axis='x', rotation=90)

        # Cluster 2
        ax2_2.bar(cluster2_data['Provinsi'], cluster2_data['Jumlah_Kejadian'], color='lightgreen')
        ax2_2.set_title('Cluster 2: Wilayah Dengan Dampak Sedang')
        ax2_2.set_xlabel('Provinsi')
        ax2_2.set_ylabel('Jumlah Kejadian')
        ax2_2.tick_params(axis='x', rotation=90)

        # Cluster 3
        ax2_3.bar(cluster3_data['Provinsi'], cluster3_data['Jumlah_Kejadian'], color='lightcoral')
        ax2_3.set_title('Cluster 3: Wilayah Dengan Dampak Berat')
        ax2_3.set_xlabel('Provinsi')
        ax2_3.set_ylabel('Jumlah Kejadian')
        ax2_3.tick_params(axis='x', rotation=90)

        st.pyplot(fig2)

    # Tab 3: Pie chart per cluster
    with tab3:
        st.subheader("Pie Chart Per Cluster")
        st.write("""
            Tab ini menunjukkan pie chart yang menggambarkan persentase distribusi wilayah berdasarkan cluster dampak banjir yang telah terbentuk. 
            Setiap bagian dari pie chart mewakili proporsi wilayah yang termasuk dalam kategori dampak banjir ringan, sedang, atau berat. 
            Visualisasi ini memberikan gambaran umum tentang bagaimana wilayah-wilayah tersebut terbagi dalam tiga cluster, 
            sehingga kita bisa dengan cepat melihat sebaran dampak banjir di seluruh dataset.
        """)
        cluster_sizes = data['Cluster_Name'].value_counts()
        fig3, ax3 = plt.subplots(figsize=(7, 7))
        ax3.pie(cluster_sizes, labels=cluster_sizes.index, autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired.colors)
        ax3.set_title('Distribusi Wilayah Berdasarkan Dampak Banjir', fontsize=14)
        st.pyplot(fig3)


    # # Langkah 9: Simpan hasil ke dalam BytesIO
    # output_file = 'hasil_clustering_banjir.xlsx'

    # # Menyimpan ke dalam BytesIO object dengan openpyxl
    # towrite = BytesIO()
    # with pd.ExcelWriter(towrite, engine='openpyxl') as writer:
    #     data.to_excel(writer, index=False, sheet_name='Cluster')

    # towrite.seek(0)  # Kembali ke awal stream
    # st.write(f"Hasil clustering disimpan dalam file: {output_file}")

    # # Tombol download
    # st.download_button("Download hasil clustering", towrite, file_name=output_file, mime="application/vnd.ms-excel")

if __name__ == "__main__":
    show_cluster()
