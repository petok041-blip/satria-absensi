import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- Konfigurasi Halaman ---
st.set_page_config(page_title="Satria Absensi", page_icon="🛡️", layout="wide")

FILE_ABSENSI = 'data_absensi_web.csv'

# --- Inisialisasi Data ---
if not os.path.exists(FILE_ABSENSI):
    df_init = pd.DataFrame(columns=['ID', 'Nama', 'Tanggal', 'Waktu', 'Jenis', 'Keterangan'])
    df_init.to_csv(FILE_ABSENSI, index=False)

# --- Sidebar Navigasi ---
st.sidebar.title("🛡️ SATRIA ABSENSI")
menu = st.sidebar.radio("Menu Navigasi", ["🏠 Dashboard", "📝 Log Kehadiran", "⚙️ Manajemen Admin"])


# --- Fungsi Simpan Data ---
def save_data(id_user, nama, jenis, ket="Hadir"):
    df = pd.read_csv(FILE_ABSENSI)

    # Cek ID Duplikat
    if id_user in df['ID'].astype(str).values:
        st.error(f"❌ Gagal: ID '{id_user}' sudah terdaftar!")
        return False

    now = datetime.now()
    new_data = {
        'ID': id_user,
        'Nama': nama.upper(),
        'Tanggal': now.strftime("%Y-%m-%d"),
        'Waktu': now.strftime("%H:%M:%S"),
        'Jenis': jenis,
        'Keterangan': ket
    }

    df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
    df.to_csv(FILE_ABSENSI, index=False)
    st.success(f"✅ Berhasil: {nama.upper()} tercatat sebagai {jenis}")
    return True


# --- UI: Dashboard ---
if menu == "🏠 Dashboard":
    st.title("🏠 Dashboard Utama")
    col1, col2 = st.columns(2)

    with col1:
        st.metric("Waktu Sekarang", datetime.now().strftime("%H:%M:%S"))
    with col2:
        st.metric("Tanggal", datetime.now().strftime("%A, %d %B %Y"))

    st.info("Selamat datang di Sistem Satria Absensi Cloud. Gunakan menu di samping untuk mulai mencatat kehadiran.")

#--- UI: Log Kehadiran ---
elif menu == "📝 Log Kehadiran":
    st.title("📝 Form Kehadiran")

    with st.form("absensi_form", clear_on_submit=True):
        id_user = st.text_input("Nomor Identitas (ID)")
        nama = st.text_input("Nama Lengkap")

        # Tambahan: Kolom Keterangan (Opsional untuk Masuk/Keluar, Wajib untuk Izin/Sakit)
        keterangan_input = st.text_area("Keterangan Tambahan (Contoh: Sakit Flu, Cuti Tahunan, Keperluan Keluarga)",
                                        placeholder="Isi jika Anda memilih Sakit, Izin, atau Cuti...")

        col_btn1, col_btn2, col_btn3, col_btn4, col_btn5 = st.columns(5)

        with col_btn1:
            masuk = st.form_submit_button("✅ Masuk")
        with col_btn2:
            keluar = st.form_submit_button("🚪 Keluar")
        with col_btn3:
            sakit = st.form_submit_button("🤒 Sakit")
        with col_btn4:
            izin = st.form_submit_button("📄 Izin")
        with col_btn5:
            cuti = st.form_submit_button("🌴 Cuti")

        # Logika Tombol
        if masuk:
            if id_user and nama:
                save_data(id_user, nama, "MASUK", keterangan_input if keterangan_input else "Hadir")
            else:
                st.warning("ID dan Nama wajib diisi!")

        if keluar:
            if id_user and nama:
                save_data(id_user, nama, "KELUAR", "Selesai Kerja")
            else:
                st.warning("ID dan Nama wajib diisi!")

        if sakit:
            if id_user and nama and keterangan_input:
                save_data(id_user, nama, "SAKIT", keterangan_input)
            elif not keterangan_input:
                st.error("Mohon isi alasan sakit pada kolom keterangan!")
            else:
                st.warning("ID dan Nama wajib diisi!")

        if izin:
            if id_user and nama and keterangan_input:
                save_data(id_user, nama, "IZIN", keterangan_input)
            elif not keterangan_input:
                st.error("Mohon isi alasan izin pada kolom keterangan!")
            else:
                st.warning("ID dan Nama wajib diisi!")

        if cuti:
            if id_user and nama and keterangan_input:
                save_data(id_user, nama, "CUTI", keterangan_input)
            elif not keterangan_input:
                st.error("Mohon isi alasan cuti pada kolom keterangan!")
            else:
                st.warning("ID dan Nama wajib diisi!")

    # Bagian Khusus Sakit/Izin dengan Keterangan Tambahan
    if sakit or izin:
        st.info("Untuk status Sakit/Izin, mohon isi alasan di bawah jika diperlukan.")

# --- UI: Admin Panel ---
elif menu == "⚙️ Manajemen Admin":
    st.title("⚙️ Database Admin")
    password = st.text_input("Masukkan Password Admin", type="password")

    if password == "kantor":
        df = pd.read_csv(FILE_ABSENSI)
        st.dataframe(df, use_container_width=True)

        # Download Button
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Data (CSV)",
            data=csv,
            file_name='rekap_absensi_satria.csv',
            mime='text/csv',
        )
    elif password:
        st.error("Password Salah!")