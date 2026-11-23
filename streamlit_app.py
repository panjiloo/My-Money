import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo
import requests

# 1. Konfigurasi Halaman
st.set_page_config(
    page_title="Panji & Febby - Keuangan",
    page_icon="💰",
    layout="centered",
    initial_sidebar_state="collapsed"
)

WEB_APP_URL = "https://script.google.com/macros/s/AKfycbwqn9gHoy2ucq237Lr-0mevxh_7anpTPHym4r3IG1jChXvIY4RK-I9VfaEfYHbE00M2/exec"
DASHBOARD_PASSWORD = "febbycantik123"

KATEGORI_PEMASUKAN = ["Gaji", "Suami", "Istri", "Ortu", "Saudara", "Investasi"]
KATEGORI_PENGELUARAN = [
    "Makan & Jajan",
    "Kebutuhan Anak",
    "Pendidikan Anak",
    "Cicilan",
    "Listrik, Air & Iuran",
    "Keluarga (Adik/Ortu/Saudara)",
    "Transportasi & BBM",
    "Pulsa & Internet",
    "Kesehatan",
    "Belanja Rumah Tangga",
    "Sedekah & Sosial",
    "Hiburan & Jajan",
    "Tabungan",
    "Investasi",
    "Lainnya"
]
OPSI_NAMA = ["Panji", "Febby", "Bersama"]

# 2. Inisialisasi Session State
if "halaman" not in st.session_state:
    st.session_state.halaman = "Home"  # "Home", "Catatan", "Entry", "Dashboard"
if "buka_menu_opsi" not in st.session_state:
    st.session_state.buka_menu_opsi = False
if "dashboard_unlocked" not in st.session_state:
    st.session_state.dashboard_unlocked = False
if "buka_menu_edit" not in st.session_state:
    st.session_state.buka_menu_edit = False
if "tipe" not in st.session_state:
    st.session_state.tipe = "Pengeluaran"
if "kategori" not in st.session_state:
    st.session_state.kategori = "Kategori"
if "buka_pilih_kategori" not in st.session_state:
    st.session_state.buka_pilih_kategori = False
if "dibayar_oleh" not in st.session_state:
    st.session_state.dibayar_oleh = "Bersama"
if "form_key" not in st.session_state:
    st.session_state.form_key = 0
if "entry_key" not in st.session_state:
    st.session_state.entry_key = 0
if "periode_dash" not in st.session_state:
    st.session_state.periode_dash = "Bulanan"
if "edit_counter" not in st.session_state:
    st.session_state.edit_counter = 0

# 3. Fungsi Ambil & Bersihkan Data dari Google Sheets
@st.cache_data(ttl=15)
def ambil_data_sheets(url):
    try:
        resp = requests.get(url, timeout=15)
        if resp.status_code == 200:
            raw_json = resp.json()
            if not raw_json:
                return pd.DataFrame(columns=[
                    "_rowNumber", "Nama", "Hari tanggal bulan tahun", "Jenis Pengeluaran",
                    "jumlah uang pengeluaran", "Jenis Pemasukan",
                    "jumlah uang pemasukan", "Catatan", "RawDate", "ParsedDate"
                ])
            df = pd.DataFrame(raw_json)
            if "_rowNumber" not in df.columns:
                df["_rowNumber"] = range(2, len(df) + 2)
            for col in ["jumlah uang pengeluaran", "jumlah uang pemasukan"]:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
                else:
                    df[col] = 0.0
            for col in ["Nama", "Jenis Pengeluaran", "Jenis Pemasukan", "Catatan", "RawDate"]:
                if col not in df.columns:
                    df[col] = ""
                else:
                    df[col] = df[col].fillna("").astype(str)
            df["ParsedDate"] = pd.to_datetime(df["RawDate"], errors="coerce")
            return df
    except Exception:
        pass
    return pd.DataFrame(columns=[
        "_rowNumber", "Nama", "Hari tanggal bulan tahun", "Jenis Pengeluaran",
        "jumlah uang pengeluaran", "Jenis Pemasukan",
        "jumlah uang pemasukan", "Catatan", "RawDate", "ParsedDate"
    ])

def format_rp(angka):
    return f"Rp {int(round(angka)):,}".replace(",", ".")

def format_tgl_indo(tgl_date):
    nama_hari = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"][tgl_date.weekday()]
    bulan_str = [
        "Januari", "Februari", "Maret", "April", "Mei", "Juni",
        "Juli", "Agustus", "September", "Oktober", "November", "Desember"
    ][tgl_date.month - 1]
    return f"{nama_hari}, {tgl_date.day} {bulan_str} {tgl_date.year}"

# Tema dinamis: merah saat di halaman Catatan dengan tipe Pengeluaran, hijau untuk lainnya
is_tema_merah = (st.session_state.halaman == "Catatan" and st.session_state.tipe == "Pengeluaran")

if is_tema_merah:
    bg_app = "#F9ECE9"
    aksen_utama = "#C8432B"
    aksen_gelap = "#9E2A1C"
    bg_input_soft = "#FFF7F5"
    border_soft = "#F2D5CF"
else:
    bg_app = "#F4F2EA"
    aksen_utama = "#1B4332"
    aksen_gelap = "#133024"
    bg_input_soft = "#F8F7F4"
    border_soft = "#EAE7DD"

# 4. Custom CSS
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }}

    .stApp {{
        background-color: {bg_app} !important;
        transition: background-color 0.25s ease !important;
    }}

    header[data-testid="stHeader"], footer {{
        display: none !important;
    }}

    .block-container {{
        max-width: 440px !important;
        padding: 1.2rem 0 0 0 !important;
        margin: 0 auto !important;
    }}

    iframe[title="streamlit_components_v1.html_v1"] {{
        margin-bottom: -10px !important;
    }}

    div[data-testid="stVerticalBlockBorderWrapper"] {{
        background-color: #FFFFFF !important;
        border-radius: 28px 28px 0 0 !important;
        padding: 14px 20px 36px 20px !important;
        border: 1px solid {border_soft} !important;
        box-shadow: 0 -4px 20px rgba(0,0,0,0.06);
    }}

    .sheet-handle {{
        width: 38px;
        height: 4px;
        background-color: #D2CFC4;
        border-radius: 4px;
        margin: 0 auto 16px auto;
    }}

    .card-title {{
        font-size: 21px;
        font-weight: 700;
        color: {aksen_gelap if is_tema_merah else "#1F2421"};
        margin-bottom: 14px;
        letter-spacing: -0.4px;
    }}

    .sub-title {{
        font-size: 15px;
        font-weight: 700;
        color: #1F2421;
        margin-top: 18px;
        margin-bottom: 10px;
    }}

    .field-label {{
        font-size: 13.5px;
        font-weight: 600;
        color: {aksen_utama if is_tema_merah else "#6B6D66"};
        margin-top: 14px;
        margin-bottom: 6px;
    }}

    .summary-box {{
        background-color: #F8F7F4;
        border: 1px solid #EAE7DD;
        border-radius: 16px;
        padding: 12px 14px;
        margin-bottom: 10px;
    }}

    .opsi-panel {{
        background-color: #F8F7F4;
        border: 1px solid #EAE7DD;
        border-radius: 18px;
        padding: 14px;
        margin-top: 10px;
        margin-bottom: 14px;
    }}

    .summary-label {{
        font-size: 12px;
        font-weight: 600;
        color: #6B6D66;
    }}

    .summary-val-in {{
        font-size: 17px;
        font-weight: 700;
        color: #1B4332;
        margin-top: 2px;
    }}

    .summary-val-out {{
        font-size: 17px;
        font-weight: 700;
        color: #C8432B;
        margin-top: 2px;
    }}

    .summary-val-net {{
        font-size: 18px;
        font-weight: 700;
        color: #1F2421;
        margin-top: 2px;
    }}

    .cat-row {{
        background-color: #F8F7F4;
        border: 1px solid #EAE7DD;
        border-radius: 12px;
        padding: 10px 12px;
        margin-bottom: 8px;
    }}

    .cat-header {{
        display: flex;
        justify-content: space-between;
        font-size: 13px;
        font-weight: 700;
        color: #000000;
        margin-bottom: 6px;
    }}

    .bar-bg {{
        width: 100%;
        height: 8px;
        background-color: #EAE7DD;
        border-radius: 999px;
        overflow: hidden;
    }}

    .bar-fill-out {{
        height: 100%;
        background-color: #C8432B;
        border-radius: 999px;
    }}

    div[data-testid="stNumberInput"] input {{
        background-color: {bg_input_soft} !important;
        border: 1.8px solid {aksen_utama} !important;
        border-radius: 14px !important;
        font-size: 20px !important;
        font-weight: 700 !important;
        color: #000000 !important;
        padding: 10px 14px !important;
        height: 52px !important;
    }}
    div[data-testid="stNumberInput"] button {{
        display: none !important;
    }}

    div.stButton > button {{
        border-radius: 999px !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        padding: 6px 14px !important;
        min-height: 38px !important;
        transition: all 0.15s ease !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.03) !important;
    }}

    div.stButton > button p {{
        font-weight: inherit !important;
    }}

    div.stButton > button[kind="secondary"] {{
        background-color: {bg_input_soft} !important;
        color: #000000 !important;
        border: 1px solid {border_soft} !important;
    }}
    div.stButton > button[kind="secondary"]:hover {{
        border-color: {aksen_utama} !important;
        color: {aksen_utama} !important;
    }}

    div.stButton > button[kind="primary"] {{
        background-color: {aksen_utama} !important;
        color: #FFFFFF !important;
        border: 1px solid {aksen_utama} !important;
    }}
    div.stButton > button[kind="primary"]:hover {{
        background-color: {aksen_gelap} !important;
        border-color: {aksen_gelap} !important;
    }}

    div[data-testid="stDateInput"] > div > div,
    div[data-testid="stTextInput"] > div > div {{
        background-color: {bg_input_soft} !important;
        border: 1px solid {border_soft} !important;
        border-radius: 12px !important;
        height: 44px !important;
    }}

    div[data-testid="stDateInput"] input,
    div[data-testid="stTextInput"] input {{
        color: #000000 !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        background-color: transparent !important;
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
            <div class="greeting-name">Panji & Febby</div>
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

    # Bar Navigasi Utama (Home / Dashboard) — Catatan & Entry tersembunyi di menu Opsi pada Home
    nav1, nav2 = st.columns(2, gap="small")
    with nav1:
        if st.button(
            "🏠 Home",
            key="nav_home",
            use_container_width=True,
            type="primary" if st.session_state.halaman == "Home" else "secondary"
        ):
            st.session_state.halaman = "Home"
            st.rerun()
    with nav2:
        if st.button(
            "📊 Dashboard",
            key="nav_dash",
            use_container_width=True,
            type="primary" if st.session_state.halaman == "Dashboard" else "secondary"
        ):
            st.session_state.halaman = "Dashboard"
            st.session_state.buka_menu_opsi = False
            st.rerun()

    st.markdown(f"<hr style='margin: 12px 0 14px 0; border: 0; border-top: 1px solid {border_soft};'>", unsafe_allow_html=True)

    # =========================================================
    # HALAMAN 1: HOME (MENU CATATAN & ENTRY TERSEMBUNYI DI OPSI)
    # =========================================================
    if st.session_state.halaman == "Home":
        st.markdown('<div class="card-title">Home</div>', unsafe_allow_html=True)
        st.caption("Selamat datang di catatan keuangan keluarga Panji & Febby.")

        st.markdown(
            '<div class="summary-box"><b>📊 Dashboard Keuangan</b><br>'
            '<span class="summary-label">Pantau ringkasan pemasukan, pengeluaran, grafik, dan kelola data.</span></div>',
            unsafe_allow_html=True
        )
        if st.button("Buka Dashboard", key="home_go_dash", type="primary", use_container_width=True):
            st.session_state.halaman = "Dashboard"
            st.session_state.buka_menu_opsi = False
            st.rerun()

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

        # Tombol Opsi: menyembunyikan menu Catatan dan Entry sampai diklik
        label_opsi = "✖️ Tutup Opsi" if st.session_state.buka_menu_opsi else "⚙️ Opsi"
        if st.button(
            label_opsi,
            key="btn_toggle_opsi",
            type="primary" if st.session_state.buka_menu_opsi else "secondary",
            use_container_width=True
        ):
            st.session_state.buka_menu_opsi = not st.session_state.buka_menu_opsi
            st.rerun()

        if st.session_state.buka_menu_opsi:
            st.markdown('<div class="opsi-panel">', unsafe_allow_html=True)
            st.markdown("**Menu Tambahan**")
            st.caption("Pilih menu input data di bawah ini:")

            if st.button("✍️ Menu Catatan", key="opsi_go_catatan", type="secondary", use_container_width=True):
                st.session_state.halaman = "Catatan"
                st.session_state.buka_menu_opsi = False
                st.rerun()

            st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

            if st.button("📝 Menu Entry", key="opsi_go_entry", type="secondary", use_container_width=True):
                st.session_state.halaman = "Entry"
                st.session_state.buka_menu_opsi = False
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    # =========================================================
    # HALAMAN 2: CATATAN
    # =========================================================
    elif st.session_state.halaman == "Catatan":
        st.markdown('<div class="card-title">Catat transaksi</div>', unsafe_allow_html=True)

        col_in, col_out = st.columns(2, gap="small")
        with col_in:
            if st.button(
                "↓ Pemasukan",
                key="btn_in",
                use_container_width=True,
                type="primary" if st.session_state.tipe == "Pemasukan" else "secondary"
            ):
                st.session_state.tipe = "Pemasukan"
                st.session_state.kategori = "Kategori"
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
                st.session_state.kategori = "Kategori"
                st.session_state.buka_pilih_kategori = False
                st.rerun()

        st.markdown('<div class="field-label">Nominal (Rp)</div>', unsafe_allow_html=True)
        nominal = st.number_input(
            "Nominal",
            min_value=0,
            value=None,
            step=1000,
            placeholder="0",
            label_visibility="collapsed",
            key=f"input_nominal_{st.session_state.form_key}"
        )

        st.markdown('<div class="field-label">Kategori</div>', unsafe_allow_html=True)
        label_tombol_kategori = f"**{st.session_state.kategori}**"
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
                    [("🥗", "Makan & Jajan"), ("🧸", "Kebutuhan Anak")],
                    [("🎒", "Pendidikan Anak"), ("🏠", "Cicilan"), ("💡", "Listrik, Air & Iuran")],
                    [("👨‍👩‍👧", "Keluarga (Adik/Ortu/Saudara)"), ("⛽", "Transportasi & BBM")],
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

        label_subjek = "Diterima oleh" if st.session_state.tipe == "Pemasukan" else "Dibayar oleh"
        st.markdown(f'<div class="field-label">{label_subjek}</div>', unsafe_allow_html=True)

        cols_payer = st.columns(3, gap="small")
        for idx, pembayar in enumerate(OPSI_NAMA):
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

        st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
        val_nominal = nominal if nominal is not None else 0
        if st.button("Submit", type="primary", use_container_width=True):
            if val_nominal > 0 and st.session_state.kategori != "Kategori":
                format_tgl_lengkap = format_tgl_indo(tanggal)

                jns_pengeluaran = st.session_state.kategori if st.session_state.tipe == "Pengeluaran" else ""
                jml_pengeluaran = val_nominal if st.session_state.tipe == "Pengeluaran" else 0

                jns_pemasukan = st.session_state.kategori if st.session_state.tipe == "Pemasukan" else ""
                jml_pemasukan = val_nominal if st.session_state.tipe == "Pemasukan" else 0

                payload = {
                    "action": "create",
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
                    response = requests.post(WEB_APP_URL, json=payload, timeout=15)
                    if response.status_code == 200:
                        ambil_data_sheets.clear()
                        st.success(f"Berhasil tersimpan: {st.session_state.tipe} {format_rp(val_nominal)}!")
                        st.session_state.form_key += 1
                        st.session_state.kategori = "Kategori"
                        st.rerun()
                    else:
                        st.error("Gagal mengirim data ke Google Sheets.")
                except Exception as e:
                    st.error(f"Terjadi kesalahan koneksi: {e}")
            else:
                st.warning("Pastikan nominal sudah diisi dan kategori sudah dipilih.")

    # =========================================================
    # HALAMAN ENTRY (INPUT CEPAT KE GOOGLE SHEETS)
    # =========================================================
    elif st.session_state.halaman == "Entry":
        st.markdown('<div class="card-title">Menu Entry</div>', unsafe_allow_html=True)
        st.caption("Input transaksi cepat langsung ke Google Sheets.")

        hari_ini_wib = datetime.now(ZoneInfo("Asia/Jakarta")).date()
        e_tipe = st.selectbox(
            "Jenis Transaksi",
            options=["Pengeluaran", "Pemasukan"],
            key=f"entry_tipe_{st.session_state.entry_key}"
        )
        daftar_kat_e = KATEGORI_PENGELUARAN if e_tipe == "Pengeluaran" else KATEGORI_PEMASUKAN
        e_kat = st.selectbox(
            "Kategori",
            options=daftar_kat_e,
            key=f"entry_kat_{st.session_state.entry_key}"
        )
        e_nom = st.number_input(
            "Nominal (Rp)",
            min_value=0,
            value=None,
            step=1000,
            placeholder="0",
            key=f"entry_nom_{st.session_state.entry_key}"
        )
        e_nama = st.selectbox(
            "Nama",
            options=OPSI_NAMA,
            index=2,
            key=f"entry_nama_{st.session_state.entry_key}"
        )
        c_et, c_ec = st.columns(2, gap="small")
        with c_et:
            e_tgl = st.date_input(
                "Tanggal",
                value=hari_ini_wib,
                format="DD/MM/YYYY",
                key=f"entry_tgl_{st.session_state.entry_key}"
            )
        with c_ec:
            e_cat = st.text_input(
                "Catatan",
                placeholder="mis. galon / bensin",
                key=f"entry_cat_{st.session_state.entry_key}"
            )

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
        val_e_nom = e_nom if e_nom is not None else 0
        if st.button("Simpan Entry", type="primary", use_container_width=True, key="btn_simpan_entry"):
            if val_e_nom > 0:
                payload_entry = {
                    "action": "create",
                    "Nama": e_nama,
                    "Hari_tanggal_bulan_tahun": format_tgl_indo(e_tgl),
                    "Jenis_Pengeluaran": e_kat if e_tipe == "Pengeluaran" else "",
                    "Jumlah_Uang_Pengeluaran": val_e_nom if e_tipe == "Pengeluaran" else 0,
                    "Jenis_Pemasukan": e_kat if e_tipe == "Pemasukan" else "",
                    "Jumlah_Uang_Pemasukan": val_e_nom if e_tipe == "Pemasukan" else 0,
                    "Catatan": e_cat,
                    "RawDate": e_tgl.strftime("%Y-%m-%d")
                }
                try:
                    resp = requests.post(WEB_APP_URL, json=payload_entry, timeout=15)
                    if resp.status_code == 200:
                        ambil_data_sheets.clear()
                        st.session_state.entry_key += 1
                        st.success(f"Entry {e_tipe} {format_rp(val_e_nom)} berhasil disimpan!")
                        st.rerun()
                    else:
                        st.error("Gagal menyimpan entry ke Google Sheets.")
                except Exception as e:
                    st.error(f"Terjadi kesalahan koneksi: {e}")
            else:
                st.warning("Nominal harus lebih dari 0.")

    # =========================================================
    # HALAMAN 3: DASHBOARD
    # =========================================================
    elif st.session_state.halaman == "Dashboard":
        if not st.session_state.dashboard_unlocked:
            st.markdown('<div class="card-title">🔒 Kunci Dashboard</div>', unsafe_allow_html=True)
            st.caption("Masukkan kata sandi untuk membuka menu Dashboard.")

            with st.form("form_password_dashboard", clear_on_submit=False):
                input_pw = st.text_input("Kata Sandi", type="password", placeholder="Masukkan kata sandi...")
                submitted_pw = st.form_submit_button("Masuk Dashboard", type="primary", use_container_width=True)

            if submitted_pw:
                if input_pw == DASHBOARD_PASSWORD:
                    st.session_state.dashboard_unlocked = True
                    st.rerun()
                else:
                    st.error("Kata sandi salah. Silakan coba lagi.")
        else:
            col_jd, col_rf, col_lk = st.columns([2.4, 0.8, 0.8], gap="small")
            with col_jd:
                st.markdown('<div class="card-title" style="margin-bottom:4px;">Dashboard</div>', unsafe_allow_html=True)
            with col_rf:
                if st.button("🔄", key="refresh_dash", use_container_width=True):
                    ambil_data_sheets.clear()
                    st.rerun()
            with col_lk:
                if st.button("🔒", key="lock_dash", use_container_width=True):
                    st.session_state.dashboard_unlocked = False
                    st.session_state.buka_menu_edit = False
                    st.rerun()

            opsi_periode = ["Harian", "Mingguan", "Bulanan", "Kuartal"]
            cols_p = st.columns(4, gap="small")
            for idx, p in enumerate(opsi_periode):
                with cols_p[idx]:
                    if st.button(
                        p,
                        key=f"periode_{p}",
                        use_container_width=True,
                        type="primary" if st.session_state.periode_dash == p else "secondary"
                    ):
                        st.session_state.periode_dash = p
                        st.rerun()

            df_raw = ambil_data_sheets(WEB_APP_URL)

            sekarang_ts = pd.Timestamp.now(ZoneInfo("Asia/Jakarta")).tz_localize(None).normalize()
            periode_aktif = st.session_state.periode_dash

            if not df_raw.empty and "ParsedDate" in df_raw.columns:
                df_valid = df_raw.copy()
                parsed = pd.to_datetime(df_valid["ParsedDate"], errors="coerce")
                if getattr(parsed.dt, "tz", None) is not None:
                    parsed = parsed.dt.tz_localize(None)
                df_valid["ParsedDate"] = parsed.dt.normalize()
                df_valid = df_valid.dropna(subset=["ParsedDate"])

                if periode_aktif == "Harian":
                    tgl_awal = sekarang_ts
                    label_rentang = sekarang_ts.strftime("%d %b %Y")
                elif periode_aktif == "Mingguan":
                    tgl_awal = sekarang_ts - pd.Timedelta(days=6)
                    label_rentang = f"{tgl_awal.strftime('%d %b')} - {sekarang_ts.strftime('%d %b %Y')}"
                elif periode_aktif == "Bulanan":
                    tgl_awal = sekarang_ts.replace(day=1)
                    label_rentang = sekarang_ts.strftime("%B %Y")
                else:
                    tgl_awal = (sekarang_ts.replace(day=1) - pd.DateOffset(months=2)).tz_localize(None).normalize()
                    label_rentang = f"{tgl_awal.strftime('%b %Y')} - {sekarang_ts.strftime('%b %Y')}"

                tgl_awal = pd.Timestamp(tgl_awal).tz_localize(None).normalize()
                df_filtered = df_valid[(df_valid["ParsedDate"] >= tgl_awal) & (df_valid["ParsedDate"] <= sekarang_ts)].copy()
            else:
                df_filtered = pd.DataFrame(columns=[
                    "_rowNumber", "Nama", "Hari tanggal bulan tahun", "Jenis Pengeluaran",
                    "jumlah uang pengeluaran", "Jenis Pemasukan",
                    "jumlah uang pemasukan", "Catatan", "RawDate", "ParsedDate"
                ])
                label_rentang = "-"

            st.caption(f"Periode: **{periode_aktif}** ({label_rentang})")

            total_pemasukan = float(df_filtered["jumlah uang pemasukan"].sum()) if not df_filtered.empty else 0.0
            total_pengeluaran = float(df_filtered["jumlah uang pengeluaran"].sum()) if not df_filtered.empty else 0.0
            selisih_bersih = total_pemasukan - total_pengeluaran

            c_in, c_out = st.columns(2, gap="small")
            with c_in:
                st.markdown(
                    f'<div class="summary-box"><div class="summary-label">↓ Pemasukan</div><div class="summary-val-in">{format_rp(total_pemasukan)}</div></div>',
                    unsafe_allow_html=True
                )
            with c_out:
                st.markdown(
                    f'<div class="summary-box"><div class="summary-label">↑ Pengeluaran</div><div class="summary-val-out">{format_rp(total_pengeluaran)}</div></div>',
                    unsafe_allow_html=True
                )

            st.markdown(
                f'<div class="summary-box"><div class="summary-label">Saldo Bersih (Pemasukan - Pengeluaran)</div><div class="summary-val-net">{format_rp(selisih_bersih)}</div></div>',
                unsafe_allow_html=True
            )

            st.markdown('<div class="sub-title">1. Pengeluaran vs Pemasukan</div>', unsafe_allow_html=True)
            df_vs = pd.DataFrame({
                "Jenis": ["Pemasukan", "Pengeluaran"],
                "Nominal (Rp)": [total_pemasukan, total_pengeluaran]
            }).set_index("Jenis")
            st.bar_chart(df_vs, height=210, use_container_width=True)

            st.markdown('<div class="sub-title">2. Pengeluaran Paling Banyak</div>', unsafe_allow_html=True)

            df_exp = df_filtered[df_filtered["jumlah uang pengeluaran"] > 0].copy() if not df_filtered.empty else pd.DataFrame()
            if not df_exp.empty and total_pengeluaran > 0:
                df_exp["Kategori"] = df_exp["Jenis Pengeluaran"].replace("", "Lainnya").fillna("Lainnya")
                rekap_kat = (
                    df_exp.groupby("Kategori", as_index=False)["jumlah uang pengeluaran"]
                    .sum()
                    .sort_values("jumlah uang pengeluaran", ascending=False)
                )
                rekap_kat["Persentase (%)"] = (rekap_kat["jumlah uang pengeluaran"] / total_pengeluaran) * 100

                st.bar_chart(
                    rekap_kat.set_index("Kategori")[["jumlah uang pengeluaran"]],
                    height=210,
                    use_container_width=True
                )

                for _, row in rekap_kat.iterrows():
                    kat_nama = row["Kategori"]
                    kat_nominal = row["jumlah uang pengeluaran"]
                    kat_pct = row["Persentase (%)"]
                    lebar_bar = min(max(kat_pct, 2.0), 100.0)
                    st.markdown(
                        f"""
                        <div class="cat-row">
                            <div class="cat-header">
                                <span>{kat_nama}</span>
                                <span>{format_rp(kat_nominal)} ({kat_pct:.1f}%)</span>
                            </div>
                            <div class="bar-bg">
                                <div class="bar-fill-out" style="width: {lebar_bar:.1f}%;"></div>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            else:
                st.info(f"Belum ada data pengeluaran pada periode **{periode_aktif}**.")

            st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)
            label_btn_edit = "✖️ Tutup Menu Edit" if st.session_state.buka_menu_edit else "✏️ Edit Data Transaksi"
            if st.button(
                label_btn_edit,
                key="toggle_menu_edit",
                type="primary" if st.session_state.buka_menu_edit else "secondary",
                use_container_width=True
            ):
                st.session_state.buka_menu_edit = not st.session_state.buka_menu_edit
                st.rerun()

            if st.session_state.buka_menu_edit:
                st.markdown('<div class="sub-title">Form Edit Data Transaksi</div>', unsafe_allow_html=True)

                if not df_filtered.empty:
                    df_urut = df_filtered.sort_values(by=["ParsedDate", "_rowNumber"], ascending=[False, False]).reset_index(drop=True)

                    pilihan_label = []
                    label_to_row = {}
                    for _, r in df_urut.iterrows():
                        is_in = float(r["jumlah uang pemasukan"]) > 0
                        jenis_str = "Pemasukan" if is_in else "Pengeluaran"
                        kat_str = r["Jenis Pemasukan"] if is_in else r["Jenis Pengeluaran"]
                        nom_val = float(r["jumlah uang pemasukan"]) if is_in else float(r["jumlah uang pengeluaran"])
                        tgl_str = r["ParsedDate"].strftime("%d/%m/%Y") if pd.notna(r["ParsedDate"]) else r["RawDate"]
                        cat_str = f" - {r['Catatan']}" if r["Catatan"].strip() else ""
                        lbl = f"Baris {int(r['_rowNumber'])} | {tgl_str} | {r['Nama']} | {kat_str} ({jenis_str}) {format_rp(nom_val)}{cat_str}"
                        pilihan_label.append(lbl)
                        label_to_row[lbl] = r

                    selected_lbl = st.selectbox(
                        "Pilih transaksi yang ingin diperbaiki",
                        options=pilihan_label,
                        key=f"select_edit_trx_{st.session_state.edit_counter}"
                    )

                    trx = label_to_row[selected_lbl]
                    row_number_asli = int(trx["_rowNumber"])

                    awal_is_in = float(trx["jumlah uang pemasukan"]) > 0
                    awal_tipe = "Pemasukan" if awal_is_in else "Pengeluaran"
                    awal_nom = int(round(float(trx["jumlah uang pemasukan"]) if awal_is_in else float(trx["jumlah uang pengeluaran"])))
                    awal_kat = trx["Jenis Pemasukan"].strip() if awal_is_in else trx["Jenis Pengeluaran"].strip()
                    awal_nama = trx["Nama"].strip() if trx["Nama"].strip() in OPSI_NAMA else "Bersama"
                    awal_tgl = trx["ParsedDate"].date() if pd.notna(trx["ParsedDate"]) else datetime.now(ZoneInfo("Asia/Jakarta")).date()
                    awal_cat = trx["Catatan"]

                    edit_tipe = st.selectbox(
                        "Jenis Transaksi",
                        options=["Pengeluaran", "Pemasukan"],
                        index=0 if awal_tipe == "Pengeluaran" else 1,
                        key=f"edit_tipe_{row_number_asli}_{st.session_state.edit_counter}"
                    )

                    daftar_kat_edit = KATEGORI_PEMASUKAN if edit_tipe == "Pemasukan" else KATEGORI_PENGELUARAN
                    if awal_kat not in daftar_kat_edit:
                        daftar_kat_edit = [awal_kat] + daftar_kat_edit if awal_kat else daftar_kat_edit
                    kat_idx = daftar_kat_edit.index(awal_kat) if awal_kat in daftar_kat_edit else 0

                    edit_kat = st.selectbox(
                        "Kategori",
                        options=daftar_kat_edit,
                        index=kat_idx,
                        key=f"edit_kat_{row_number_asli}_{edit_tipe}_{st.session_state.edit_counter}"
                    )

                    edit_nom = st.number_input(
                        "Nominal Baru (Rp)",
                        min_value=1,
                        value=max(awal_nom, 1),
                        step=1000,
                        key=f"edit_nom_{row_number_asli}_{st.session_state.edit_counter}"
                    )

                    edit_nama = st.selectbox(
                        "Nama",
                        options=OPSI_NAMA,
                        index=OPSI_NAMA.index(awal_nama),
                        key=f"edit_nama_{row_number_asli}_{st.session_state.edit_counter}"
                    )

                    c_etgl, c_ecat = st.columns(2, gap="small")
                    with c_etgl:
                        edit_tgl = st.date_input(
                            "Tanggal Baru",
                            value=awal_tgl,
                            format="DD/MM/YYYY",
                            key=f"edit_tgl_{row_number_asli}_{st.session_state.edit_counter}"
                        )
                    with c_ecat:
                        edit_cat = st.text_input(
                            "Catatan Baru",
                            value=awal_cat,
                            key=f"edit_cat_{row_number_asli}_{st.session_state.edit_counter}"
                        )

                    if st.button("💾 Update ke Google Sheets", type="primary", use_container_width=True, key=f"btn_update_{row_number_asli}"):
                        jns_peng = edit_kat if edit_tipe == "Pengeluaran" else ""
                        jml_peng = int(edit_nom) if edit_tipe == "Pengeluaran" else 0
                        jns_pem = edit_kat if edit_tipe == "Pemasukan" else ""
                        jml_pem = int(edit_nom) if edit_tipe == "Pemasukan" else 0

                        payload_update = {
                            "action": "update",
                            "rowNumber": row_number_asli,
                            "Nama": edit_nama,
                            "Hari_tanggal_bulan_tahun": format_tgl_indo(edit_tgl),
                            "Jenis_Pengeluaran": jns_peng,
                            "Jumlah_Uang_Pengeluaran": jml_peng,
                            "Jenis_Pemasukan": jns_pem,
                            "Jumlah_Uang_Pemasukan": jml_pem,
                            "Catatan": edit_cat,
                            "RawDate": edit_tgl.strftime("%Y-%m-%d")
                        }

                        try:
                            resp = requests.post(WEB_APP_URL, json=payload_update, timeout=15)
                            if resp.status_code == 200:
                                ambil_data_sheets.clear()
                                st.session_state.edit_counter += 1
                                st.success(f"Baris {row_number_asli} berhasil diperbarui di Google Sheets!")
                                st.rerun()
                            else:
                                st.error("Gagal mengupdate data ke Google Sheets.")
                        except Exception as e:
                            st.error(f"Terjadi kesalahan koneksi saat update: {e}")
                else:
                    st.info(f"Tidak ada transaksi pada periode **{periode_aktif}** untuk diedit.")
