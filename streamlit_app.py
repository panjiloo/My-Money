import streamlit as st
from datetime import datetime, date

# 1. Konfigurasi Halaman
st.set_page_config(
    page_title="Catat Transaksi - Toni & Keke",
    page_icon="💰",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 2. Inisialisasi Session State untuk menyimpan pilihan interaktif
if "tipe" not in st.session_state:
    st.session_state.tipe = "Pengeluaran"
if "kategori" not in st.session_state:
    st.session_state.kategori = "Makan & Dapur"
if "dibayar_oleh" not in st.session_state:
    st.session_state.dibayar_oleh = "Bersama"

# 3. Custom CSS untuk meniru desain UI secara presisi
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

    /* Reset & Latar Belakang Utama (Hijau Gelap di bagian atas) */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }
    
    .stApp {
        background-color: #162E22 !important;
    }

    /* Sembunyikan header & footer bawaan Streamlit */
    header[data-testid="stHeader"], footer {
        display: none !important;
    }

    /* Atur lebar kontainer agar menyerupai layar mobile */
    .block-container {
        max-width: 440px !important;
        padding: 1.2rem 0 0 0 !important;
        margin: 0 auto !important;
    }

    /* Header Atas: Selamat malam, Panji & Febby */
    .top-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        padding: 0 20px 18px 20px;
        color: #E2ECE7;
    }
    .greeting-sub {
        font-size: 13px;
        color: #8BA396;
        margin-bottom: 2px;
        font-weight: 500;
    }
    .greeting-name {
        font-size: 20px;
        font-weight: 700;
        color: #C7D8CE;
        letter-spacing: -0.3px;
    }
    .sync-badge {
        background-color: rgba(255, 255, 255, 0.08);
        color: #A3B8AD;
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 500;
        margin-top: 6px;
        border: 1px solid rgba(255, 255, 255, 0.06);
    }

    /* Kartu Utama (Bottom Sheet Krem) */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #F4F2EA !important;
        border-radius: 28px 28px 0 0 !important;
        padding: 14px 20px 36px 20px !important;
        border: none !important;
        box-shadow: 0 -4px 20px rgba(0,0,0,0.2);
    }

    /* Garis Handle di atas kartu */
    .sheet-handle {
        width: 38px;
        height: 4px;
        background-color: #D2CFC4;
        border-radius: 4px;
        margin: 0 auto 16px auto;
    }

    /* Judul: Catat transaksi */
    .card-title {
        font-size: 21px;
        font-weight: 700;
        color: #1F2421;
        margin-bottom: 14px;
        letter-spacing: -0.4px;
    }

    /* Label Section (Nominal, Kategori, Dibayar oleh, Tanggal, Catatan) */
    .field-label {
        font-size: 13.5px;
        font-weight: 600;
        color: #6B6D66;
        margin-top: 14px;
        margin-bottom: 6px;
    }

    /* Styling Input Nominal */
    div[data-testid="stNumberInput"] input {
        background-color: #FFFFFF !important;
        border: 1.8px solid #355E4B !important;
        border-radius: 14px !important;
        font-size: 26px !important;
        font-weight: 700 !important;
        color: #5A5D58 !important;
        padding: 12px 16px !important;
        height: 58px !important;
    }
    div[data-testid="stNumberInput"] button {
        display: none !important; /* Sembunyikan tombol + dan - bawaan */
    }

    /* Styling Umum untuk Tombol Pilihan (Pills & Tabs) */
    div.stButton > button {
        border-radius: 999px !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        padding: 6px 14px !important;
        min-height: 38px !important;
        transition: all 0.15s ease !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.03) !important;
    }

    /* Tombol Tidak Aktif (Secondary) */
    div.stButton > button[kind="secondary"] {
        background-color: #FFFFFF !important;
        color: #2C302E !important;
        border: 1px solid #EAE7DD !important;
    }
    div.stButton > button[kind="secondary"]:hover {
        border-color: #1B4332 !important;
        color: #1B4332 !important;
    }

    /* Tombol Aktif (Primary) - Default Hijau Tua (untuk Kategori) */
    div.stButton > button[kind="primary"] {
        background-color: #1B4332 !important;
        color: #FFFFFF !important;
        border: 1px solid #1B4332 !important;
    }

    /* Penyesuaian khusus baris Segmented Control Pemasukan / Pengeluaran */
    .tipe-container {
        background-color: #EAE7DD;
        padding: 4px;
        border-radius: 14px;
        margin-bottom: 6px;
    }
    /* Jika Pengeluaran aktif, ubah warna tombol aktif di baris pertama menjadi Merah Bata */
    div[data-testid="stHorizontalBlock"]:nth-of-type(1) div.stButton > button[kind="primary"] {
        background-color: #C8432B !important;
        border-color: #C8432B !important;
        border-radius: 11px !important;
    }
    div[data-testid="stHorizontalBlock"]:nth-of-type(1) div.stButton > button[kind="secondary"] {
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        color: #6B6D66 !important;
    }

    /* Styling Input Tanggal & Catatan di bagian bawah */
    div[data-testid="stDateInput"] > div > div,
    div[data-testid="stTextInput"] > div > div {
        background-color: #E7E4DA !important;
        border: none !important;
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

# 4. Header Atas (Background Hijau Tua)
st.markdown("""
<div class="top-header">
    <div>
        <div class="greeting-sub">Selamat malam,</div>
        <div class="greeting-name">Toni & Keke</div>
    </div>
    <div class="sync-badge">☁️ Tersinkron</div>
</div>
""", unsafe_allow_html=True)

# 5. Kontainer Utama (Kartu Krem Membulat)
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
            st.rerun()
    with col_out:
        if st.button(
            "↑ Pengeluaran",
            key="btn_out",
            use_container_width=True,
            type="primary" if st.session_state.tipe == "Pengeluaran" else "secondary"
        ):
            st.session_state.tipe = "Pengeluaran"
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

    # --- Pilihan Kategori (Pills) ---
    st.markdown('<div class="field-label">Kategori</div>', unsafe_allow_html=True)
    
    # Susunan baris kategori mengikuti tata letak gambar
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
                    key=f"kat_{idx_row}_{idx_col}",
                    use_container_width=True,
                    type="primary" if is_selected else "secondary"
                ):
                    st.session_state.kategori = nama_kat
                    st.rerun()

    # --- Dibayar oleh ---
    st.markdown('<div class="field-label">Dibayar oleh</div>', unsafe_allow_html=True)
    opsi_pembayar = ["Panji", "Febby", "Bersama"]
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
        tanggal = st.date_input(
            "Tanggal",
            value=date(2026, 10, 30),
            format="DD/MM/YYYY",
            label_visibility="collapsed"
        )
    with col_cat:
        st.markdown('<div class="field-label">Catatan</div>', unsafe_allow_html=True)
        catatan = st.text_input(
            "Catatan",
            placeholder="mis. honor rapat",
            label_visibility="collapsed"
        )

    # --- Tombol Simpan Transaksi ---
    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    if st.button("Simpan Transaksi", type="primary", use_container_width=True):
        if nominal > 0:
            st.success(
                f"Tersimpan: **{st.session_state.tipe}** Rp {nominal:,} "
                f"({st.session_state.kategori}) oleh **{st.session_state.dibayar_oleh}**."
            )
        else:
            st.warning("Masukkan nominal transaksi terlebih dahulu.")
