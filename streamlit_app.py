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

# 2. Inisialisasi Session State
if "halaman" not in st.session_state:
    st.session_state.halaman = "Home"  # "Home", "Catatan", "Dashboard"
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
if "periode_dash" not in st.session_state:
    st.session_state.periode_dash = "Bulanan"

# 3. Fungsi Ambil & Bersihkan Data dari Google Sheets
@st.cache_data(ttl=15)
def ambil_data_sheets(url):
    try:
        resp = requests.get(url, timeout=15)
        if resp.status_code == 200:
            raw_json = resp.json()
            if not raw_json:
                return pd.DataFrame(columns=[
                    "Nama", "Hari tanggal bulan tahun", "Jenis Pengeluaran",
                    "jumlah uang pengeluaran", "Jenis Pemasukan",
                    "jumlah uang pemasukan", "Catatan", "RawDate"
                ])
            df = pd.DataFrame(raw_json)
            for col in ["jumlah uang pengeluaran", "jumlah uang pemasukan"]:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
                else:
                    df[col] = 0.0
            if "RawDate" in df.columns:
                df["ParsedDate"] = pd.to_datetime(df["RawDate"], errors="coerce")
            else:
                df["ParsedDate"] = pd.NaT
            return df
    except Exception:
        pass
    return pd.DataFrame(columns=[
        "Nama", "Hari tanggal bulan tahun", "Jenis Pengeluaran",
        "jumlah uang pengeluaran", "Jenis Pemasukan",
        "jumlah uang pemasukan", "Catatan", "RawDate", "ParsedDate"
    ])

def format_rp(angka):
    return f"Rp {int(round(angka)):,}".replace(",", ".")

# 4. Custom CSS
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

    .sub-title {
        font-size: 15px;
        font-weight: 700;
        color: #1F2421;
        margin-top: 18px;
        margin-bottom: 10px;
    }

    .field-label {
        font-size: 13.5px;
        font-weight: 600;
        color: #6B6D66;
        margin-top: 14px;
        margin-bottom: 6px;
    }

    .summary-box {
        background-color: #F8F7F4;
        border: 1px solid #EAE7DD;
        border-radius: 16px;
        padding: 12px 14px;
        margin-bottom: 10px;
    }

    .summary-label {
        font-size: 12px;
        font-weight: 600;
        color: #6B6D66;
    }

    .summary-val-in {
        font-size: 17px;
        font-weight: 700;
        color: #1B4332;
        margin-top: 2px;
    }

    .summary-val-out {
        font-size: 17px;
        font-weight: 700;
        color: #C8432B;
        margin-top: 2px;
    }

    .summary-val-net {
        font-size: 18px;
        font-weight: 700;
        color: #1F2421;
        margin-top: 2px;
    }

    .cat-row {
        background-color: #F8F7F4;
        border: 1px solid #EAE7DD;
        border-radius: 12px;
        padding: 10px 12px;
        margin-bottom: 8px;
    }

    .cat-header {
        display: flex;
        justify-content: space-between;
        font-size: 13px;
        font-weight: 700;
        color: #000000;
        margin-bottom: 6px;
    }

    .bar-bg {
        width: 100%;
        height: 8px;
        background-color: #EAE7DD;
        border-radius: 999px;
        overflow: hidden;
    }

    .bar-fill-out {
        height: 100%;
        background-color: #C8432B;
        border-radius: 999px;
    }

    div[data-testid="stNumberInput"] input {
        background-color: #F8F7F4 !important;
        border: 1.8px solid #355E4B !important;
        border-radius: 14px !important;
        font-size: 26px !important;
        font-weight: 700 !important;
        color: #000000 !important;
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

    div.stButton > button p {
        font-weight: inherit !important;
    }

    div.stButton > button[kind="secondary"] {
        background-color: #F8F7F4 !important;
        color: #000000 !important;
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
        color: #000000 !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        background-color: transparent !important;
    }
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

    # Bar Navigasi Utama (Home / Catatan / Dashboard)
    nav1, nav2, nav3 = st.columns(3, gap="small")
    with nav1:
        if st.button("🏠 Home", key="nav_home", use_container_width=True,
                     type="primary" if st.session_state.halaman == "Home" else "secondary"):
            st.session_state.halaman = "Home"
            st.rerun()
    with nav2:
        if st.button("✍️ Catatan", key="nav_catatan", use_container_width=True,
                     type="primary" if st.session_state.halaman == "Catatan" else "secondary"):
            st.session_state.halaman = "Catatan"
            st.rerun()
    with nav3:
        if st.button("📊 Dashboard", key="nav_dash", use_container_width=True,
                     type="primary" if st.session_state.halaman == "Dashboard" else "secondary"):
            st.session_state.halaman = "Dashboard"
            st.rerun()

    st.markdown("<hr style='margin: 12px 0 14px 0; border: 0; border-top: 1px solid #EAE7DD;'>", unsafe_allow_html=True)

    # =========================================================
    # HALAMAN 1: HOME
    # =========================================================
    if st.session_state.halaman == "Home":
        st.markdown('<div class="card-title">Menu Utama</div>', unsafe_allow_html=True)
        st.caption("Pilih menu untuk mencatat transaksi atau melihat ringkasan keuangan.")

        st.markdown('<div class="summary-box"><b>✍️ Menu Catatan</b><br><span class="summary-label">Input pengeluaran & pemasukan harian secara cepat ke Google Sheets.</span></div>', unsafe_allow_html=True)
        if st.button("Buka Menu Catatan", key="go_catatan", type="primary", use_container_width=True):
            st.session_state.halaman = "Catatan"
            st.rerun()

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

        st.markdown('<div class="summary-box"><b>📊 Menu Dashboard</b><br><span class="summary-label">Summary keuangan, filter harian/mingguan/bulanan/kuartal, serta diagram perbandingan & kategori pengeluaran terbesar.</span></div>', unsafe_allow_html=True)
        if st.button("Buka Menu Dashboard", key="go_dash", type="secondary", use_container_width=True):
            st.session_state.halaman = "Dashboard"
            st.rerun()

    # =========================================================
    # HALAMAN 2: CATATAN (INPUT PENGELUARAN & PEMASUKAN)
    # =========================================================
    elif st.session_state.halaman == "Catatan":
        warna_tab_aktif = "#C8432B" if st.session_state.tipe == "Pengeluaran" else "#1B4332"
        st.markdown(f"""
        <style>
            div[data-testid="stHorizontalBlock"]:nth-of-type(2) div.stButton > button[kind="primary"] {{
                background-color: {warna_tab_aktif} !important;
                border-color: {warna_tab_aktif} !important;
                border-radius: 11px !important;
            }}
        </style>
        """, unsafe_allow_html=True)

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

        # Input Nominal (tanpa 0 bawaan agar langsung siap ketik)
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

        # Tombol Kategori (font hitam & bold)
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

        # Dibayar / Diterima oleh
        label_subjek = "Diterima oleh" if st.session_state.tipe == "Pemasukan" else "Dibayar oleh"
        st.markdown(f'<div class="field-label">{label_subjek}</div>', unsafe_allow_html=True)

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

        # Tanggal & Catatan
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

        # Tombol Submit
        st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
        val_nominal = nominal if nominal is not None else 0
        if st.button("Submit", type="primary", use_container_width=True):
            if val_nominal > 0 and st.session_state.kategori != "Kategori":
                nama_hari = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"][tanggal.weekday()]
                bulan_str = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"][tanggal.month - 1]
                format_tgl_lengkap = f"{nama_hari}, {tanggal.day} {bulan_str} {tanggal.year}"

                jns_pengeluaran = st.session_state.kategori if st.session_state.tipe == "Pengeluaran" else ""
                jml_pengeluaran = val_nominal if st.session_state.tipe == "Pengeluaran" else 0

                jns_pemasukan = st.session_state.kategori if st.session_state.tipe == "Pemasukan" else ""
                jml_pemasukan = val_nominal if st.session_state.tipe == "Pemasukan" else 0

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
    # HALAMAN 3: DASHBOARD
    # =========================================================
    elif st.session_state.halaman == "Dashboard":
        col_jd, col_rf = st.columns([3, 1])
        with col_jd:
            st.markdown('<div class="card-title" style="margin-bottom:4px;">Dashboard</div>', unsafe_allow_html=True)
        with col_rf:
            if st.button("🔄", key="refresh_dash", use_container_width=True):
                ambil_data_sheets.clear()
                st.rerun()

        # Filter Periode: Harian, Mingguan, Bulanan, Kuartal
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

        # Samakan semua tanggal menjadi tz-naive (tanpa timezone) & dinormalisasi ke awal hari
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
            else:  # Kuartal (3 bulan terakhir termasuk bulan ini)
                tgl_awal = (sekarang_ts.replace(day=1) - pd.DateOffset(months=2)).tz_localize(None).normalize()
                label_rentang = f"{tgl_awal.strftime('%b %Y')} - {sekarang_ts.strftime('%b %Y')}"

            tgl_awal = pd.Timestamp(tgl_awal).tz_localize(None).normalize()
            df_filtered = df_valid[(df_valid["ParsedDate"] >= tgl_awal) & (df_valid["ParsedDate"] <= sekarang_ts)]
        else:
            df_filtered = pd.DataFrame(columns=[
                "Nama", "Hari tanggal bulan tahun", "Jenis Pengeluaran",
                "jumlah uang pengeluaran", "Jenis Pemasukan",
                "jumlah uang pemasukan", "Catatan", "RawDate"
            ])
            label_rentang = "-"

        st.caption(f"Periode: **{periode_aktif}** ({label_rentang})")

        total_pemasukan = float(df_filtered["jumlah uang pemasukan"].sum()) if not df_filtered.empty else 0.0
        total_pengeluaran = float(df_filtered["jumlah uang pengeluaran"].sum()) if not df_filtered.empty else 0.0
        selisih_bersih = total_pemasukan - total_pengeluaran

        # Summary Cards
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

        # 1. Diagram Pengeluaran vs Pemasukan
        st.markdown('<div class="sub-title">1. Pengeluaran vs Pemasukan</div>', unsafe_allow_html=True)
        df_vs = pd.DataFrame({
            "Jenis": ["Pemasukan", "Pengeluaran"],
            "Nominal (Rp)": [total_pemasukan, total_pengeluaran]
        }).set_index("Jenis")
        st.bar_chart(df_vs, height=210, use_container_width=True)

        # 2. Pengeluaran Paling Banyak (Angka + Persentase + Diagram)
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
