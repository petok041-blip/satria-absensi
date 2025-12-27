import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Satria Absensi", page_icon="🛡️", layout="wide")

FILE_ABSENSI = 'data_absensi_web.csv'

# --- 2. INISIALISASI DATA ---
if not os.path.exists(FILE_ABSENSI):
    df_init = pd.DataFrame(columns=['ID', 'Nama', 'Tanggal', 'Waktu', 'Jenis', 'Keterangan'])
    df_init.to_csv(FILE_ABSENSI, index=False)


# --- 3. FUNGSI SIMPAN DATA ---
def save_data(id_user, nama, jenis, ket="Hadir"):
    df = pd.read_csv(FILE_ABSENSI)
    today = datetime.now().strftime("%Y-%m-%d")

    # Cek apakah ID sudah absen untuk JENIS yang sama di HARI yang sama
    is_duplicate = df[(df['ID'].astype(str) == str(id_user)) &
                      (df['Tanggal'] == today) &
                      (df['Jenis'] == jenis)]

    if not is_duplicate.empty:
        st.error(f"❌ Gagal: ID '{id_user}' sudah melakukan absensi {jenis} hari ini!")
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


# --- 4. SIDEBAR NAVIGASI ---
st.sidebar.title("🛡️ SATRIA ABSENSI")
menu = st.sidebar.radio("Menu Navigasi",
                        ["🏠 Dashboard", "📝 Log Kehadiran", "🔍 Riwayat Saya", "⚙️ Manajemen Admin"])

# --- 5. UI: DASHBOARD ---
if menu == "🏠 Dashboard":
    st.title("🏠 Dashboard Utama")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Waktu Sekarang", datetime.now().strftime("%H:%M:%S"))
    with col2:
        st.metric("Tanggal", datetime.now().strftime("%A, %d %B %Y"))
    st.info("Selamat datang di Sistem Satria Absensi Cloud.")

# --- 6. UI: LOG KEHADIRAN (FORM DENGAN FITUR ENTER) ---
elif menu == "📝 Log Kehadiran":
    st.title("📝 Form Kehadiran")
    st.caption("Tips: Tekan ENTER setelah mengisi ID dan Nama untuk langsung absen MASUK.")

    # Menggunakan form agar tombol Enter berfungsi otomatis
    with st.form("absensi_form", clear_on_submit=True):
        id_user = st.text_input("Nomor Identitas (ID)", placeholder="Masukkan ID...")
        nama = st.text_input("Nama Lengkap", placeholder="Masukkan Nama...")
        keterangan_input = st.text_input("Keterangan Tambahan (Opsional)",
                                         placeholder="Contoh: Hadir, Sakit Flu, dsb.")

        # Tombol utama (Tombol pertama dalam form biasanya menjadi target tombol Enter)
        masuk = st.form_submit_button("✅ Masuk (Klik Enter)")

        # Tombol tambahan lainnya
        col_btn2, col_btn3, col_btn4, col_btn5 = st.columns(4)
        with col_btn2:
            keluar = st.form_submit_button("🚪 Keluar")
        with col_btn3:
            sakit = st.form_submit_button("🤒 Sakit")
        with col_btn4:
            izin = st.form_submit_button("📄 Izin")
        with col_btn5:
            cuti = st.form_submit_button("🌴 Cuti")

        # Logika Eksekusi
        if masuk:
            if id_user and nama:
                save_data(id_user, nama, "MASUK", keterangan_input if keterangan_input else "Hadir")
            else:
                st.warning("ID dan Nama wajib diisi!")
        elif keluar:
            if id_user and nama:
                save_data(id_user, nama, "KELUAR", "Selesai Kerja")
            else:
                st.warning("ID dan Nama wajib diisi!")
        elif sakit or izin or cuti:
            jenis_status = "SAKIT" if sakit else ("IZIN" if izin else "CUTI")
            if id_user and nama and keterangan_input:
                save_data(id_user, nama, jenis_status, keterangan_input)
            elif not keterangan_input:
                st.error(f"Mohon isi alasan {jenis_status.lower()} pada kolom keterangan!")
            else:
                st.warning("ID dan Nama wajib diisi!")

# --- 7. UI: RIWAYAT SAYA ---
elif menu == "🔍 Riwayat Saya":
    st.title("🔍 Riwayat Absensi Saya")
    # Form kecil untuk riwayat agar Enter juga berfungsi di sini
    with st.form("search_form"):
        search_id = st.text_input("Masukkan Nomor ID Anda", placeholder="Contoh: 123")
        submit_search = st.form_submit_button("Cari Data")

    if submit_search and search_id:
        if os.path.exists(FILE_ABSENSI):
            df = pd.read_csv(FILE_ABSENSI)
            user_data = df[df['ID'].astype(str) == str(search_id)]
            if not user_data.empty:
                user_data = user_data.sort_values(by=['Tanggal', 'Waktu'], ascending=False)
                st.write(f"Menampilkan riwayat untuk: **{user_data['Nama'].iloc[0]}**")
                st.dataframe(user_data, use_container_width=True)
            else:
                st.warning("Data tidak ditemukan.")

# --- 8. UI: ADMIN PANEL ---
elif menu == "⚙️ Manajemen Admin":
    st.title("⚙️ Database Admin")
    with st.form("admin_login"):
        password = st.text_input("Masukkan Password Admin", type="password")
        login_btn = st.form_submit_button("Buka Data")

    if login_btn and password == "kantor":
        df = pd.read_csv(FILE_ABSENSI)
        st.dataframe(df, use_container_width=True)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Data (CSV)", data=csv, file_name='rekap.csv', mime='text/csv')
    elif login_btn:
        st.error("Password Salah!")