import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime
from zoneinfo import ZoneInfo

# 1. Konfigurasi Halaman
st.set_page_config(
    page_title="Catat Transaksi - Panji & Feby",
    page_icon="💰",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 2. Inisialisasi Session State
if "tipe" not in st.session_state:
    st.session_state.tipe = "Pengeluaran"
if "kategori" not in st.session_state:
    st.session_state.kategori = "Makan & Dapur"
if "dibayar_oleh" not in st.session_state:
    st.session_state.dibayar_oleh = "Bersama"

# 3. Custom CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }
    
    /* Background Utama Krem */
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

    /* Hilangkan celah berlebih pada iframe komponen header */
    iframe[title="streamlit_components_v1.html_v1"] {
        margin-bottom: -10px !important;
    }

    /* Kartu Utama (Container) */
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

    /* Input Nominal */
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

    /* Tombol Pilihan (Pills) */
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

    /* Input Tanggal & Catatan */
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

# 4. Warna Dinamis untuk Tab Pemasukan (Hijau) vs Pengeluaran (Merah Bata)
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

# 5. Header Atas dengan Deteksi Otomatis Jam Lokal Perangkat/HP
components.html("""
<!DOCTYPE html>
<html>
<head>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
    * {
        box-sizing: border-box;
        margin: 0;
        padding: 0;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    body {
        background-color: transparent;
    }
    .top-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        padding: 0 20px 10px 20px;
        color: #2C302E;
    }
    .greeting-sub {
        font-size: 13px;
        color: #6B6D66;
        margin-bottom: 2px;
        font-weight: 500;
    }
    .greeting-name {
        font-size: 20px;
        font-weight: 700;
        color: #1F2421;
        letter-spacing: -0.3px;
    }
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
            if (jam >= 4 && jam < 11) {
                teks = "Selamat pagi,";
            } else if (jam >= 11 && jam < 15) {
                teks = "Selamat siang,";
            } else if (jam >= 15 && jam < 18) {
                teks = "Selamat sore,";
            }
            document.getElementById("ucapan").innerText = teks;
        }
        updateGreeting();
        setInterval(updateGreeting, 60000); // Perbarui otomatis tiap 1 menit
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
            st.session_state.kategori = "Gaji"
            st.rerun()

    with col_out:
        if st.button(
            "↑ Pengeluaran",
            key="btn_out",
            use_container_width=True,
            type="primary" if st.session_state.tipe == "Pengeluaran" else "secondary"
        ):
            st.session_state.tipe = "Pengeluaran"
            st.session_state.kategori = "Makan & Dapur"
            st.rerun()

    # --- Input Nominal (Rp) ---
    st.markdown('<div class="field-label">Nominal (Rp)</div>', unsafe_allow_html=True)
    nominal = st.number_input(
        "Nominal",
        min_value=0,
        value=0,
        step=1000,
        label_visibility="collapsed"
    )

    # --- Pilihan Kategori Dinamis ---
    st.markdown('<div class="field-label">Kategori</div>', unsafe_allow_html=True)
    
    if st.session_state.tipe == "Pemasukan":
        baris_kategori = [
            [("💼", "Gaji"), ("👨", "Suami"), ("👩", "Istri")],
            [("👴", "Ortu"), ("🤝", "Saudara"), ("📈", "Investasi")]
        ]
    else:
        baris_kategori = [
            [("🥗", "Makan & Dapur"), ("🧸", "Kebutuhan Anak")],
            [("🎒", "Pendidikan Anak"), ("🏠", "Cicilan"), ("💡", "Listrik, Air & Iuran")],
            [("👨‍👩‍👧", "Keluarga (Adik/Ortu)"), ("⛽", "Transportasi & BBM")],
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
            label_visibility="collapsed"
        )
    with col_cat:
        st.markdown('<div class="field-label">Catatan</div>', unsafe_allow_html=True)
        placeholder_cat = "mis. honor rapat" if st.session_state.tipe == "Pemasukan" else "mis. belanja mingguan"
        catatan = st.text_input(
            "Catatan",
            placeholder=placeholder_cat,
            label_visibility="collapsed"
        )

    # --- Tombol Simpan Transaksi ---
    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    if st.button("Simpan Transaksi", type="primary", use_container_width=True):
        if nominal > 0:
            st.success(
                f"Tersimpan: **{st.session_state.tipe}** Rp {nominal:,} "
                f"({st.session_state.kategori}) - **{st.session_state.dibayar_oleh}**."
            )
        else:
            st.warning("Masukkan nominal transaksi terlebih dahulu.")
