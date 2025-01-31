import streamlit as st
from login import show_login
from dashboard import show_dashboard
from data_wilayah import show_data_wilayah
from cluster import show_cluster
from mitigasi import show_mitigasi
# from coba import coba  # Memastikan coba diimpor dengan benar

def main():
    # Set konfigurasi aplikasi
    st.set_page_config(page_title="Aplikasi Banjir", page_icon="🌊", layout="wide")

    # Status login
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.page = "Login"
        st.session_state.mode = "User"  # Default mode sebagai User

    # Header untuk memilih mode aplikasi
    st.title("Aplikasi Banjir 🌊")
    st.markdown("---")
    mode = st.selectbox("Pilih Mode Aplikasi", ["User Umum", "Admin"], index=0, key="mode_selector")
    st.session_state.mode = "Admin" if mode == "Admin" else "User"

    # Halaman login untuk Admin
    if not st.session_state.logged_in and st.session_state.mode == "Admin":
        show_login()
    else:
        if st.session_state.mode == "User":
            # Sidebar navigasi untuk user umum
            st.sidebar.title("Navigasi User")
            st.sidebar.markdown("---")
            menu_items = {
                "Mitigasi Bencana": "🚨 Mitigasi Bencana",
                "Hasil Clustering dan Visualisasi": "📊 Cluster dan Visualisasi",
                # "Halaman Coba": "🔧 Coba",  # Menambahkan menu item untuk coba
            }

            # Pilihan menu untuk user umum
            for page, label in menu_items.items():
                if st.sidebar.button(label):
                    st.session_state.page = page

            # Routing untuk user umum
            if st.session_state.page == "Mitigasi Bencana":
                show_mitigasi()
            elif st.session_state.page == "Hasil Clustering dan Visualisasi":
                show_cluster()
            # elif st.session_state.page == "Halaman Coba":  # Routing untuk coba
            #      coba()
        else:
            # Sidebar navigasi untuk admin
            st.sidebar.title("Navigasi Admin")
            st.sidebar.markdown("---")
            menu_items = {
                "Dashboard": "🏠 Dashboard",
                "Data Wilayah": "🌍 Data Wilayah",
                "Cluster dan Visualisasi Cluster": "📊 Cluster dan Visualisasi",
                "Logout": "🔒 Logout",
            }

            for page, label in menu_items.items():
                if st.sidebar.button(label):
                    if page == "Logout":
                        st.session_state.logged_in = False
                        st.session_state.page = "Login"
                    else:
                        st.session_state.page = page

            # Routing untuk admin
            if st.session_state.page == "Dashboard":
                show_dashboard()
            elif st.session_state.page == "Data Wilayah":
                show_data_wilayah()
            elif st.session_state.page == "Cluster dan Visualisasi Cluster":
                show_cluster()

if __name__ == "__main__":
    main()
