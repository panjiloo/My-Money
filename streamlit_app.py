import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo
import io
import requests

# 1. Konfigurasi Halaman
st.set_page_config(
    page_title="Catat Transaksi - Panji & Feby",
    page_icon="💰",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# URL Web App Google Apps Script Anda
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbwqn9gHoy2ucq237Lr-0mevxh_7anpTPHym4r3IG1jChXvIY4RK-I9VfaEfYHbE00M2/exec"

# 2. Inisialisasi Session State
if "tipe" not in st.session_state:
    st.session_state.tipe = "Pengeluaran"
if "kategori" not in st.session_state:
    st.session_state.kategori = "Pilih Kategori..."
if "buka_pilih_kategori" not in st.session_state:
    st.session_state.buka_pilih_kategori = False
if "dibayar_oleh" not in st.session_state:
    st.session_state.dibayar_oleh = "Bersama"
if "form_key" not in st.session_state:
    st.session_state.form_key = 0

# 3. Custom CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }
    
    .stApp {
        background-color: #F4F2EA !important;
    }

    header[data-testid="stHeader"], footer {
        display: none !important;
    }

    .block-container {
        max-width: 440px !important;
        padding: 1.2rem 0 0 0 !important;
        margin: 0 auto !important;
    }

    iframe[title="streamlit_components_v1.html_v1"] {
        margin-bottom: -10px !important;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #FFFFFF !important;
        border-radius: 28px 28px 0 0 !important;
        padding: 14px 20px 36px 20px !important;
        border: none !important;
        box-shadow: 0 -4px 20px rgba(0,0,0,0.06);
    }

    .sheet-handle {
        width: 38px;
        height: 4px;
        background-color: #D2CFC4;
        border-radius: 4px;
        margin: 0 auto 16px auto;
    }

    .card-title {
        font-size: 21px;
        font-weight: 700;
        color: #1F2421;
        margin-bottom: 14px;
        letter-spacing: -0.4px;
    }

    .field-label {
        font-size: 13.5px;
        font-weight: 600;
        color: #6B6D66;
        margin-top: 14px;
        margin-bottom: 6px;
    }

    div[data-testid="stNumberInput"] input {
        background-color: #F8F7F4 !important;
        border: 1.8px solid #355E4B !important;
        border-radius: 14px !important;
        font-size: 26px !important;
        font-weight: 700 !important;
        color: #5A5D58 !important;
        padding: 12px 16px !important;
        height: 58px !important;
    }
    div[data-testid="stNumberInput"] button {
        display: none !important;
    }

    div.stButton > button {
        border-radius: 999px !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        padding: 6px 14px !important;
        min-height: 38px !important;
        transition: all 0.15s ease !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.03) !important;
    }

    div.stButton > button[kind="secondary"] {
        background-color: #F8F7F4 !important;
        color: #2C302E !important;
        border: 1px solid #EAE7DD !important;
    }
    div.stButton > button[kind="secondary"]:hover {
        border-color: #1B4332 !important;
        color: #1B4332 !important;
    }

    div.stButton > button[kind="primary"] {
        background-color: #1B4332 !important;
        color: #FFFFFF !important;
        border: 1px solid #1B4332 !important;
    }

    div[data-testid="stDateInput"] > div > div,
    div[data-testid="stTextInput"] > div > div {
        background-color: #F8F7F4 !important;
        border: 1px solid #EAE7DD !important;
        border-radius: 12px !important;
        height: 46px !important;
    }
    div[data-testid="stDateInput"] input,
    div[data-testid="stTextInput"] input {
        color: #2C302E !important;
        font-weight: 500 !important;
        font-size: 14px !important;
        background-color: transparent !important;
    }
</style>
""", unsafe_allow_html=True)

# 4. Warna Dinamis Tab Pemasukan vs Pengeluaran
warna_tab_aktif = "#C8432B" if st.session_state.tipe == "Pengeluaran" else "#1B4332"
st.markdown(f"""
<style>
    div[data-testid="stHorizontalBlock"]:nth-of-type(1) div.stButton > button[kind="primary"] {{
        background-color: {warna_tab_aktif} !important;
        border-color: {warna_tab_aktif} !important;
        border-radius: 11px !important;
    }}
    div[data-testid="stHorizontalBlock"]:nth-of-type(1) div.stButton > button[kind="secondary"] {{
        background-color: #EAE7DD !important;
        border: none !important;
        border-radius: 11px !important;
        box-shadow: none !important;
        color: #6B6D66 !important;
    }}
</style>
""", unsafe_allow_html=True)

# 5. Header Atas dengan Jam Lokal HP
components.html("""
<!DOCTYPE html>
<html>
<head>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Plus Jakarta Sans', sans-serif; }
    body { background-color: transparent; }
    .top-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        padding: 0 20px 10px 20px;
        color: #2C302E;
    }
    .greeting-sub { font-size: 13px; color: #6B6D66; margin-bottom: 2px; font-weight: 500; }
    .greeting-name { font-size: 20px; font-weight: 700; color: #1F2421; letter-spacing: -0.3px; }
    .sync-badge {
        background-color: rgba(0, 0, 0, 0.05);
        color: #4A524E;
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 500;
        margin-top: 6px;
        border: 1px solid rgba(0, 0, 0, 0.08);
    }
</style>
</head>
<body>
    <div class="top-header">
        <div>
            <div class="greeting-sub" id="ucapan">Selamat malam,</div>
            <div class="greeting-name">Panji & Feby</div>
        </div>
        <div class="sync-badge">☁️ Tersinkron</div>
    </div>
    <script>
        function updateGreeting() {
            const jam = new Date().getHours();
            let teks = "Selamat malam,";
            if (jam >= 4 && jam < 11) teks = "Selamat pagi,";
            else if (jam >= 11 && jam < 15) teks = "Selamat siang,";
            else if (jam >= 15 && jam < 18) teks = "Selamat sore,";
            document.getElementById("ucapan").innerText = teks;
        }
        updateGreeting();
        setInterval(updateGreeting, 60000);
    </script>
</body>
</html>
""", height=68)

# 6. Kontainer Utama
with st.container(border=True):
    st.markdown('<div class="sheet-handle"></div>', unsafe_allow_html=True)
    st.markdown('<div class="card-title">Catat transaksi</div>', unsafe_allow_html=True)

    # --- Toggle Pemasukan / Pengeluaran ---
    col_in, col_out = st.columns(2, gap="small")
    with col_in:
        if st.button(
            "↓ Pemasukan",
            key="btn_in",
            use_container_width=True,
            type="primary" if st.session_state.tipe == "Pemasukan" else "secondary"
        ):
            st.session_state.tipe = "Pemasukan"
            st.session_state.kategori = "Pilih Kategori..."
            st.session_state.buka_pilih_kategori = False
            st.rerun()

    with col_out:
        if st.button(
            "↑ Pengeluaran",
            key="btn_out",
            use_container_width=True,
            type="primary" if st.session_state.tipe == "Pengeluaran" else "secondary"
        ):
            st.session_state.tipe = "Pengeluaran"
            st.session_state.kategori = "Pilih Kategori..."
            st.session_state.buka_pilih_kategori = False
            st.rerun()

    # --- Input Nominal (Rp) ---
    st.markdown('<div class="field-label">Nominal (Rp)</div>', unsafe_allow_html=True)
    nominal = st.number_input(
        "Nominal",
        min_value=0,
        value=0,
        step=1000,
        label_visibility="collapsed",
        key=f"input_nominal_{st.session_state.form_key}"
    )

    # --- Tombol Kategori (Dropdown Akordeon) ---
    st.markdown('<div class="field-label">Kategori</div>', unsafe_allow_html=True)
    
    label_tombol_kategori = f"📂 {st.session_state.kategori}"
    if st.button(label_tombol_kategori, key="btn_buka_kategori", use_container_width=True):
        st.session_state.buka_pilih_kategori = not st.session_state.buka_pilih_kategori
        st.rerun()

    if st.session_state.buka_pilih_kategori:
        if st.session_state.tipe == "Pemasukan":
            baris_kategori = [
                [("💼", "Gaji"), ("👨", "Suami"), ("👩", "Istri")],
                [("👴", "Ortu"), ("🤝", "Saudara"), ("📈", "Investasi")]
            ]
        else:
            baris_kategori = [
                [("🥗", "Makan & Dapur"), ("🧸", "Kebutuhan Anak")],
                [("🎒", "Pendidikan Anak"), ("🏠", "Cicilan"), ("💡", "Listrik, Air & Iuran")],
                [("👨‍👩‍👧", "Keluarga (Adik/Uti)"), ("⛽", "Transportasi & BBM")],
                [("📶", "Pulsa & Internet"), ("💊", "Kesehatan")],
                [("🧺", "Belanja Rumah Tangga"), ("🤲", "Sedekah & Sosial")],
                [("🍦", "Hiburan & Jajan"), ("🐷", "Tabungan"), ("📈", "Investasi")],
                [("📦", "Lainnya")]
            ]

        for idx_row, row in enumerate(baris_kategori):
            cols = st.columns(len(row), gap="small")
            for idx_col, (ikon, nama_kat) in enumerate(row):
                with cols[idx_col]:
                    is_selected = (st.session_state.kategori == nama_kat)
                    if st.button(
                        f"{ikon} {nama_kat}",
                        key=f"kat_{st.session_state.tipe}_{idx_row}_{idx_col}",
                        use_container_width=True,
                        type="primary" if is_selected else "secondary"
                    ):
                        st.session_state.kategori = nama_kat
                        st.session_state.buka_pilih_kategori = False
                        st.rerun()

    # --- Dibayar / Diterima oleh ---
    label_subjek = "Diterima oleh" if st.session_state.tipe == "Pemasukan" else "Dibayar oleh"
    st.markdown(f'<div class="field-label">{label_subjek}</div>', unsafe_allow_html=True)
    
    opsi_pembayar = ["Panji", "Feby", "Bersama"]
    cols_payer = st.columns(3, gap="small")
    for idx, pembayar in enumerate(opsi_pembayar):
        with cols_payer[idx]:
            is_selected = (st.session_state.dibayar_oleh == pembayar)
            if st.button(
                pembayar,
                key=f"payer_{pembayar}",
                use_container_width=True,
                type="primary" if is_selected else "secondary"
            ):
                st.session_state.dibayar_oleh = pembayar
                st.rerun()

    # --- Tanggal & Catatan ---
    col_tgl, col_cat = st.columns(2, gap="small")
    with col_tgl:
        st.markdown('<div class="field-label">Tanggal</div>', unsafe_allow_html=True)
        hari_ini_wib = datetime.now(ZoneInfo("Asia/Jakarta")).date()
        tanggal = st.date_input(
            "Tanggal",
            value=hari_ini_wib,
            format="DD/MM/YYYY",
            label_visibility="collapsed",
            key=f"input_tgl_{st.session_state.form_key}"
        )
    with col_cat:
        st.markdown('<div class="field-label">Catatan</div>', unsafe_allow_html=True)
        placeholder_cat = "mis. honor rapat" if st.session_state.tipe == "Pemasukan" else "mis. belanja mingguan"
        catatan = st.text_input(
            "Catatan",
            placeholder=placeholder_cat,
            label_visibility="collapsed",
            key=f"input_catatan_{st.session_state.form_key}"
        )

    # --- Tombol Simpan Transaksi (Kirim ke Google Sheets via Web App) ---
    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    if st.button("Simpan Transaksi", type="primary", use_container_width=True):
        if nominal > 0 and st.session_state.kategori != "Pilih Kategori...":
            nama_hari = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"][tanggal.weekday()]
            bulan_str = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"][tanggal.month - 1]
            format_tgl_lengkap = f"{nama_hari}, {tanggal.day} {bulan_str} {tanggal.year}"

            jns_pengeluaran = st.session_state.kategori if st.session_state.tipe == "Pengeluaran" else ""
            jml_pengeluaran = nominal if st.session_state.tipe == "Pengeluaran" else 0
            
            jns_pemasukan = st.session_state.kategori if st.session_state.tipe == "Pemasukan" else ""
            jml_pemasukan = nominal if st.session_state.tipe == "Pemasukan" else 0

            payload = {
                "Nama": st.session_state.dibayar_oleh,
                "Hari_tanggal_bulan_tahun": format_tgl_lengkap,
                "Jenis_Pengeluaran": jns_pengeluaran,
                "Jumlah_Uang_Pengeluaran": jml_pengeluaran,
                "Jenis_Pemasukan": jns_pemasukan,
                "Jumlah_Uang_Pemasukan": jml_pemasukan,
                "Catatan": catatan,
                "RawDate": tanggal.strftime("%Y-%m-%d")
            }

            try:
                response = requests.post(WEB_APP_URL, json=payload)
                if response.status_code == 200:
                    st.success(f"Berhasil tersimpan ke Google Sheets: {st.session_state.tipe} Rp {nominal:,}!")
                    # Kosongkan form input
                    st.session_state.form_key += 1
                    st.session_state.kategori = "Pilih Kategori..."
                    st.rerun()
                else:
                    st.error("Gagal mengirim data ke Google Sheets.")
            except Exception as e:
                st.error(f"Terjadi kesalahan koneksi: {e}")
        else:
            st.warning("Pastikan nominal sudah diisi dan kategori sudah dipilih.")

    # --- Bagian Download Laporan Excel ---
    st.markdown("<hr style='margin: 24px 0 16px 0; border: 0; border-top: 1px solid #EAE7DD;'>", unsafe_allow_html=True)
    st.markdown('<div class="card-title" style="font-size: 17px;">Download Laporan Excel</div>', unsafe_allow_html=True)

    # Membaca data langsung dari Google Sheets untuk keperluan download laporan
    @st.cache_data(ttl=5)
    def load_data_from_sheet(sheet_url):
        try:
            csv_url = sheet_url.replace('/edit?usp=sharing', '/export?format=csv&gid=0').replace('/edit', '/export?format=csv&gid=0')
            df = pd.read_csv(csv_url)
            return df
        except Exception:
            return pd.DataFrame()

    df_database = load_data_from_sheet(WEB_APP_URL.replace("/exec", "/edit")) # atau gunakan URL share Google Sheets Anda

    # Alternatif pembacaan CSV langsung dari link Google Sheets publik/share
    link_csv_sheets = st.text_input("Link CSV Google Sheets (Opsional untuk unduh laporan):", value="", placeholder="https://docs.google.com/spreadsheets/d/.../export?format=csv")
    
    if link_csv_sheets:
        try:
            df_all = pd.read_csv(link_csv_sheets)
            df_all["RawDate"] = pd.to_datetime(df_all["RawDate"], errors="coerce")
            df_all = df_all.dropna(subset=["RawDate"])

            tipe_laporan = st.selectbox("Pilih Periode Laporan", ["Harian", "Mingguan", "Bulanan (Siklus Gajian Panji - tgl 26)", "Bulanan (Siklus Gajian Feby - tgl 28)", "Semua Data"])
            
            df_filtered = df_all.copy()
            sekarang = pd.Timestamp.now(ZoneInfo("Asia/Jakarta")).normalize().tz_localize(None)

            if tipe_laporan == "Harian":
                df_filtered = df_all[df_all["RawDate"] == sekarang]
            elif tipe_laporan == "Mingguan":
                satu_minggu_lalu = sekarang - pd.Timedelta(days=7)
                df_filtered = df_all[(df_all["RawDate"] >= satu_minggu_lalu) & (df_all["RawDate"] <= sekarang)]
            elif "Bulanan" in tipe_laporan:
                tgl_gaji = 26 if "Panji" in tipe_laporan else 28
                tahun_skrg = sekarang.year
                bulan_skrg = sekarang.month
                
                try:
                    mulai_bln_ini = pd.Timestamp(year=tahun_skrg, month=bulan_skrg, day=tgl_gaji)
                except ValueError:
                    mulai_bln_ini = pd.Timestamp(year=tahun_skrg, month=bulan_skrg, day=1) + pd.offsets.MonthEnd(0)

                if sekarang >= mulai_bln_ini:
                    tgl_mulai = mulai_bln_ini
                    tgl_selesai = (tgl_mulai + pd.DateOffset(months=1)) - pd.Timedelta(days=1)
                else:
                    tgl_selesai = mulai_bln_ini - pd.Timedelta(days=1)
                    tgl_mulai = (tgl_selesai - pd.DateOffset(months=1)) + pd.Timedelta(days=1)

                df_filtered = df_all[(df_all["RawDate"] >= tgl_mulai) & (df_all["RawDate"] <= tgl_selesai)]

            if not df_filtered.empty:
                df_export = df_filtered[[
                    "Nama", 
                    "Hari tanggal bulan tahun", 
                    "Jenis Pengeluaran", 
                    "jumlah uang pengeluaran", 
                    "Jenis Pemasukan", 
                    "jumlah uang pemasukan"
                ]].rename(columns={
                    "jumlah uang pengeluaran": "jumlah uang",
                    "jumlah uang pemasukan": "jumlah uang"
                })
                
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df_export.to_excel(writer, index=False, sheet_name='Laporan Keuangan')
                excel_data = output.getvalue()

                st.download_button(
                    label=f"📥 Download Excel ({tipe_laporan})",
                    data=excel_data,
                    file_name=f"Laporan_Keuangan_{tipe_laporan.lower().replace(' ', '_').replace('(', '').replace(')', '')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            else:
                st.info(f"Tidak ada data transaksi untuk periode **{tipe_laporan}**.")
        except Exception:
            st.caption("Masukkan link export CSV Google Sheets dengan benar untuk mengaktifkan unduhan laporan.")
    else:
            st.caption("Masukkan link CSV Spreadsheet di atas untuk mulai mendownload laporan berdasarkan data Google Sheets.")
