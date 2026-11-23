import base64
import io
import json
from pathlib import Path
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

BASE_DIR = Path(__file__).resolve().parent
KANDIDAT_GAMBAR = [
    BASE_DIR / "kimi.jpeg",
    BASE_DIR / "kimi.jpg",
    BASE_DIR / "assets" / "kimi.jpeg",
    BASE_DIR / "assets" / "kimi.jpg",
    BASE_DIR / "images" / "kimi.jpeg",
    BASE_DIR / "images" / "kimi.jpg",
]

KATEGORI_PEMASUKAN = ["Gaji", "Suami", "Istri", "Ortu", "Saudara", "Investasi"]
KATEGORI_PENGELUARAN = [
    "Makan & Jajan",
    "Listrik & Air",
    "Pulsa & Internet",
    "Transport & BBM",
    "Belanja Bulanan/ Rumah Tangga",
    "Tabungan",
    "Kesehatan",
    "Hiburan",
    "Sedekah & Sosial",
    "Iuran",
    "Investasi",
    "Keluarga",
    "Kebutuhan Anak",
    "Pendidikan Anak",
    "Cicilan",
    "Lainnya"
]
IKON_PENGELUARAN = {
    "Makan & Jajan": "🥗",
    "Listrik & Air": "💡",
    "Pulsa & Internet": "📶",
    "Transport & BBM": "⛽",
    "Belanja Bulanan/ Rumah Tangga": "🧺",
    "Tabungan": "🐷",
    "Kesehatan": "💊",
    "Hiburan": "🍦",
    "Sedekah & Sosial": "🤲",
    "Iuran": "🧾",
    "Investasi": "📈",
    "Keluarga": "👨‍👩‍👧",
    "Kebutuhan Anak": "🧸",
    "Pendidikan Anak": "🎒",
    "Cicilan": "🏠",
    "Lainnya": "📦"
}
OPSI_NAMA = ["Panji", "Febby", "Bersama"]
OPSI_FILTER_NAMA = ["Semua", "Panji", "Febby", "Bersama"]
OPSI_PERIODE = ["Hari", "Minggu", "Bulan", "Semester", "Tahun", "Semua"]

# 2. Inisialisasi Session State
if "halaman" not in st.session_state:
    st.session_state.halaman = "Home"  # "Home", "Entry", "Dashboard"
if "entry_mode_terkunci" not in st.session_state:
    st.session_state.entry_mode_terkunci = False
if "hide_home_nominal" not in st.session_state:
    st.session_state.hide_home_nominal = True
if "dashboard_unlocked" not in st.session_state:
    st.session_state.dashboard_unlocked = False
if "buka_menu_edit" not in st.session_state:
    st.session_state.buka_menu_edit = False
if "buka_menu_download" not in st.session_state:
    st.session_state.buka_menu_download = False
if "buka_menu_periode" not in st.session_state:
    st.session_state.buka_menu_periode = False
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
if "tanggal_kosong" not in st.session_state:
    st.session_state.tanggal_kosong = False
if "periode_dash" not in st.session_state:
    st.session_state.periode_dash = "Bulan"
if "tanggal_hari_dash" not in st.session_state:
    st.session_state.tanggal_hari_dash = datetime.now(ZoneInfo("Asia/Jakarta")).date()
if "filter_nama_dash" not in st.session_state:
    st.session_state.filter_nama_dash = "Semua"
if "edit_counter" not in st.session_state:
    st.session_state.edit_counter = 0

def _muat_banner_data_uri():
    for kandidat in KANDIDAT_GAMBAR:
        try:
            if kandidat.exists() and kandidat.is_file():
                mime = "image/png" if kandidat.suffix.lower() == ".png" else "image/jpeg"
                encoded = base64.b64encode(kandidat.read_bytes()).decode("ascii")
                return f"data:{mime};base64,{encoded}"
        except Exception:
            continue
    return ""

def _salam_waktu_wib():
    jam = datetime.now(ZoneInfo("Asia/Jakarta")).hour
    if 4 <= jam < 11:
        return "Selamat pagi,"
    if 11 <= jam < 15:
        return "Selamat siang,"
    if 15 <= jam < 18:
        return "Selamat sore,"
    return "Selamat malam,"

def _bersihkan_angka_rp(val):
    if val is None or val == "":
        return 0.0
    if isinstance(val, (int, float)):
        return float(val) if pd.notna(val) else 0.0
    s = str(val).strip()
    s = s.replace("Rp", "").replace("rp", "").replace(" ", "")
    if "." in s and "," in s:
        s = s.replace(".", "").replace(",", ".")
    elif "." in s:
        parts = s.split(".")
        if all(len(p) == 3 for p in parts[1:]):
            s = "".join(parts)
    elif "," in s:
        parts = s.split(",")
        if all(len(p) == 3 for p in parts[1:]):
            s = "".join(parts)
        else:
            s = s.replace(",", ".")
    num = pd.to_numeric(s, errors="coerce")
    return float(num) if pd.notna(num) else 0.0

def _format_ribuan_input(teks_input):
    if not teks_input:
        return "", 0
    digits = "".join(ch for ch in str(teks_input) if ch.isdigit())
    if not digits:
        return "", 0
    angka = int(digits)
    terformat = f"{angka:,}".replace(",", ".")
    return terformat, angka

def _cari_kolom(df, kandidat_nama):
    norm_map = {str(c).strip().lower().replace("_", " "): c for c in df.columns}
    for k in kandidat_nama:
        key_norm = k.strip().lower().replace("_", " ")
        if key_norm in norm_map:
            return norm_map[key_norm]
    return None

# 3. Fungsi Ambil & Bersihkan Data dari Google Sheets
@st.cache_data(ttl=5)
def ambil_data_sheets(url):
    kolom_standar = [
        "_rowNumber", "Nama", "Hari tanggal bulan tahun", "Jenis Pengeluaran",
        "jumlah uang pengeluaran", "Jenis Pemasukan",
        "jumlah uang pemasukan", "Catatan", "RawDate", "ParsedDate"
    ]
    try:
        resp = requests.get(url, timeout=20)
        if resp.status_code == 200:
            raw_json = resp.json()
            if isinstance(raw_json, dict):
                raw_json = raw_json.get("data", [])
            if not raw_json:
                return pd.DataFrame(columns=kolom_standar)

            df = pd.DataFrame(raw_json)
            if df.empty:
                return pd.DataFrame(columns=kolom_standar)

            col_row = _cari_kolom(df, ["_rowNumber", "rowNumber", "row"])
            if col_row:
                df["_rowNumber"] = pd.to_numeric(df[col_row], errors="coerce").fillna(0).astype(int)
            else:
                df["_rowNumber"] = range(2, len(df) + 2)

            col_peng_jml = _cari_kolom(df, [
                "jumlah uang pengeluaran", "Jumlah_Uang_Pengeluaran", "Jumlah Uang Pengeluaran", "Pengeluaran"
            ])
            col_pem_jml = _cari_kolom(df, [
                "jumlah uang pemasukan", "Jumlah_Uang_Pemasukan", "Jumlah Uang Pemasukan", "Pemasukan"
            ])

            df["jumlah uang pengeluaran"] = df[col_peng_jml].apply(_bersihkan_angka_rp) if col_peng_jml else 0.0
            df["jumlah uang pemasukan"] = df[col_pem_jml].apply(_bersihkan_angka_rp) if col_pem_jml else 0.0

            mapping_teks = {
                "Nama": ["Nama", "Dibayar oleh", "Diterima oleh"],
                "Hari tanggal bulan tahun": ["Hari tanggal bulan tahun", "Hari_tanggal_bulan_tahun", "Tanggal Indo"],
                "Jenis Pengeluaran": ["Jenis Pengeluaran", "Jenis_Pengeluaran", "Kategori Pengeluaran"],
                "Jenis Pemasukan": ["Jenis Pemasukan", "Jenis_Pemasukan", "Kategori Pemasukan"],
                "Catatan": ["Catatan", "Keterangan", "Notes"],
                "RawDate": ["RawDate", "Tanggal", "Date"]
            }

            for target_col, kandidat in mapping_teks.items():
                ditemukan = _cari_kolom(df, kandidat)
                if ditemukan:
                    df[target_col] = df[ditemukan].fillna("").astype(str).str.strip()
                else:
                    df[target_col] = ""

            parsed_raw = pd.to_datetime(df["RawDate"], errors="coerce")
            if parsed_raw.isna().any():
                col_tgl_alt = _cari_kolom(df, ["Tanggal", "Hari tanggal bulan tahun", "Hari_tanggal_bulan_tahun"])
                if col_tgl_alt:
                    parsed_alt = pd.to_datetime(df[col_tgl_alt], errors="coerce", dayfirst=True)
                    parsed_raw = parsed_raw.fillna(parsed_alt)

            if getattr(parsed_raw.dt, "tz", None) is not None:
                parsed_raw = parsed_raw.dt.tz_localize(None)
            df["ParsedDate"] = parsed_raw.dt.normalize()
            return df
    except Exception:
        pass
    return pd.DataFrame(columns=kolom_standar)

def format_rp(angka):
    return f"Rp {int(round(angka)):,}".replace(",", ".")

def format_tgl_indo(tgl_date):
    nama_hari = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"][tgl_date.weekday()]
    bulan_str = [
        "Januari", "Februari", "Maret", "April", "Mei", "Juni",
        "Juli", "Agustus", "September", "Oktober", "November", "Desember"
    ][tgl_date.month - 1]
    return f"{nama_hari}, {tgl_date.day} {bulan_str} {tgl_date.year}"

def render_donut_with_side_stats(labels, values, colors, chart_id="donutChart", height=250):
    clean_vals = [float(v) for v in values]
    total_val = sum(clean_vals)
    formatted_rp_list = [format_rp(v) for v in clean_vals]
    pct_list = [f"{(v / total_val * 100):.1f}%" if total_val > 0 else "0.0%" for v in clean_vals]

    payload_labels = json.dumps(labels)
    payload_values = json.dumps(clean_vals)
    payload_colors = json.dumps(colors)
    payload_rp = json.dumps(formatted_rp_list)
    payload_pct = json.dumps(pct_list)

    components.html(f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;600;700&display=swap" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: 'Plus Jakarta Sans', sans-serif; }}
            body {{ background: transparent; }}
            .card-donut-side {{
                width: 100%;
                background: #F8F7F4;
                border: 1px solid #EAE7DD;
                border-radius: 16px;
                padding: 12px;
                display: flex;
                flex-direction: row;
                align-items: center;
                justify-content: space-between;
                gap: 12px;
                min-height: {height - 14}px;
            }}
            .canvas-box {{
                width: 145px;
                height: 145px;
                flex: 0 0 145px;
                position: relative;
            }}
            .stats-side {{
                flex: 1;
                min-width: 0;
                display: flex;
                flex-direction: column;
                gap: 7px;
                max-height: {height - 38}px;
                overflow-y: auto;
                padding-right: 2px;
            }}
            .stat-item {{
                background: #FFFFFF;
                border: 1px solid #EAE7DD;
                border-radius: 10px;
                padding: 6px 8px;
            }}
            .stat-top {{
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 6px;
                font-size: 11.5px;
                font-weight: 700;
                color: #1F2421;
            }}
            .stat-left {{
                display: flex;
                align-items: center;
                gap: 6px;
                min-width: 0;
            }}
            .dot {{
                width: 9px;
                height: 9px;
                border-radius: 50%;
                flex-shrink: 0;
            }}
            .stat-name {{
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }}
            .stat-pct {{
                color: #1F2421;
                font-weight: 700;
                flex-shrink: 0;
            }}
            .stat-rp {{
                font-size: 11.5px;
                font-weight: 600;
                color: #4A524E;
                margin-top: 2px;
                padding-left: 15px;
            }}
        </style>
    </head>
    <body>
        <div class="card-donut-side">
            <div class="canvas-box">
                <canvas id="{chart_id}"></canvas>
            </div>
            <div class="stats-side" id="{chart_id}_stats"></div>
        </div>
        <script>
            const labels = {payload_labels};
            const values = {payload_values};
            const colors = {payload_colors};
            const rpList = {payload_rp};
            const pctList = {payload_pct};

            const statsContainer = document.getElementById('{chart_id}_stats');
            labels.forEach((lbl, idx) => {{
                const item = document.createElement('div');
                item.className = 'stat-item';
                item.innerHTML = `
                    <div class="stat-top">
                        <div class="stat-left">
                            <span class="dot" style="background-color: ${{colors[idx] || '#1B4332'}};"></span>
                            <span class="stat-name" title="${{lbl}}">${{lbl}}</span>
                        </div>
                        <span class="stat-pct">${{pctList[idx]}}</span>
                    </div>
                    <div class="stat-rp">${{rpList[idx]}}</div>
                `;
                statsContainer.appendChild(item);
            }});

            const ctx = document.getElementById('{chart_id}').getContext('2d');
            new Chart(ctx, {{
                type: 'doughnut',
                data: {{
                    labels: labels,
                    datasets: [{{
                        data: values,
                        backgroundColor: colors,
                        borderColor: '#FFFFFF',
                        borderWidth: 2,
                        hoverOffset: 4
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    cutout: '58%',
                    plugins: {{
                        legend: {{ display: false }},
                        tooltip: {{
                            callbacks: {{
                                label: function(context) {{
                                    const idx = context.dataIndex;
                                    return ' ' + labels[idx] + ': ' + rpList[idx] + ' (' + pctList[idx] + ')';
                                }}
                            }}
                        }}
                    }}
                }}
            }});
        </script>
    </body>
    </html>
    """, height=height)

def build_export_dataframe(df_src):
    if df_src.empty:
        return pd.DataFrame(columns=[
            "Tanggal", "Nama", "Jenis", "Kategori", "Pemasukan (Rp)", "Pengeluaran (Rp)", "Catatan"
        ])
    rows = []
    for _, r in df_src.iterrows():
        is_in = float(r["jumlah uang pemasukan"]) > 0
        jenis = "Pemasukan" if is_in else "Pengeluaran"
        kat = r["Jenis Pemasukan"] if is_in else r["Jenis Pengeluaran"]
        tgl_str = r["ParsedDate"].strftime("%Y-%m-%d") if pd.notna(r["ParsedDate"]) else r["RawDate"]
        rows.append({
            "Tanggal": tgl_str,
            "Nama": r["Nama"],
            "Jenis": jenis,
            "Kategori": kat,
            "Pemasukan (Rp)": int(round(float(r["jumlah uang pemasukan"]))),
            "Pengeluaran (Rp)": int(round(float(r["jumlah uang pengeluaran"]))),
            "Catatan": r["Catatan"]
        })
    return pd.DataFrame(rows)

def generate_excel_bytes(df_export):
    buf = io.BytesIO()
    try:
        with pd.ExcelWriter(buf, engine="openpyxl") as writer:
            df_export.to_excel(writer, index=False, sheet_name="Transaksi")
        return buf.getvalue(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "xlsx"
    except Exception:
        csv_fallback = df_export.to_csv(index=False).encode("utf-8-sig")
        return csv_fallback, "text/csv", "csv"

def generate_pdf_bytes(periode_aktif, label_rentang, nama_filter, total_pemasukan, total_pengeluaran, selisih_bersih, df_export):
    def escape_pdf_text(text):
        clean = str(text).encode("latin-1", "replace").decode("latin-1")
        return clean.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")

    lines = [
        "LAPORAN KEUANGAN - PANJI & FEBBY",
        f"Periode: {periode_aktif} ({label_rentang}) | Nama: {nama_filter}",
        f"Total Pemasukan : {format_rp(total_pemasukan)}",
        f"Total Pengeluaran: {format_rp(total_pengeluaran)}",
        f"Saldo Bersih     : {format_rp(selisih_bersih)}",
        "------------------------------------------------------------",
        "Daftar Transaksi:"
    ]
    if df_export.empty:
        lines.append("Tidak ada transaksi pada periode/filter ini.")
    else:
        for _, r in df_export.head(35).iterrows():
            nominal_rp = format_rp(r["Pemasukan (Rp)"] if r["Jenis"] == "Pemasukan" else r["Pengeluaran (Rp)"])
            cat_txt = f" ({r['Catatan']})" if str(r["Catatan"]).strip() else ""
            lines.append(f"{r['Tanggal']} | {r['Nama']} | {r['Jenis']} - {r['Kategori']}: {nominal_rp}{cat_txt}")

    content_ops = ["BT", "/F1 10 Tf", "40 790 Td", "14 TL"]
    for idx, line in enumerate(lines):
        esc = escape_pdf_text(line)
        if idx == 0:
            content_ops.append(f"({esc}) Tj")
        else:
            content_ops.append(f"T* ({esc}) Tj")
    content_ops.append("ET")
    stream_data = "\n".join(content_ops).encode("latin-1", "replace")

    objects = []
    objects.append(b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n")
    objects.append(b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n")
    objects.append(
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] "
        b"/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>\nendobj\n"
    )
    objects.append(b"4 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n")
    objects.append(
        f"5 0 obj\n<< /Length {len(stream_data)} >>\nstream\n".encode("latin-1")
        + stream_data
        + b"\nendstream\nendobj\n"
    )

    pdf_out = io.BytesIO()
    pdf_out.write(b"%PDF-1.4\n")
    offsets = [0]
    for obj in objects:
        offsets.append(pdf_out.tell())
        pdf_out.write(obj)

    xref_pos = pdf_out.tell()
    pdf_out.write(f"xref\n0 {len(offsets)}\n".encode("latin-1"))
    pdf_out.write(b"0000000000 65535 f \n")
    for off in offsets[1:]:
        pdf_out.write(f"{off:010d} 00000 n \n".encode("latin-1"))

    pdf_out.write(
        f"trailer\n<< /Size {len(offsets)} /Root 1 0 R >>\nstartxref\n{xref_pos}\n%%EOF".encode("latin-1")
    )
    return pdf_out.getvalue()

# Tema dinamis: merah saat di halaman Entry dengan tipe Pengeluaran, hijau untuk lainnya
is_tema_merah = (st.session_state.halaman == "Entry" and st.session_state.tipe == "Pengeluaran")

if is_tema_merah:
    bg_app = "#F9ECE9"
    aksen_utama = "#C8432B"
    aksen_gelap = "#9E2A1C"
    bg_input_soft = "#FFF7F5"
    border_soft = "#F2D5CF"
    placeholder_color = "#9E5A4E"
else:
    bg_app = "#F4F2EA"
    aksen_utama = "#1B4332"
    aksen_gelap = "#133024"
    bg_input_soft = "#F8F7F4"
    border_soft = "#EAE7DD"
    placeholder_color = "#7A7D75"

banner_data_uri = _muat_banner_data_uri()
salam_awal = _salam_waktu_wib()

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
        padding: 0.9rem 0 0 0 !important;
        margin: 0 auto !important;
    }}

    iframe[title="streamlit_components_v1.html_v1"] {{
        margin-bottom: -10px !important;
    }}

    .top-header-photo-wrap {{
        padding: 0 12px 10px 12px;
    }}

    .top-header-photo {{
        width: 100%;
        height: 156px;
        border-radius: 22px;
        overflow: hidden;
        box-shadow: 0 8px 20px rgba(15, 23, 42, 0.16);
        border: 1px solid rgba(255, 255, 255, 0.65);
        background: linear-gradient(135deg, #162447 0%, #1F4068 55%, #E43F5A 100%);
    }}

    .top-header-photo img {{
        width: 100%;
        height: 100%;
        object-fit: cover;
        object-position: center 45%;
        display: block;
    }}

    .greeting-strip {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 2px 2px 6px 2px;
        gap: 10px;
    }}

    .greeting-sub {{
        font-size: 13px;
        color: #6B6D66;
        margin-bottom: 1px;
        font-weight: 500;
    }}

    .greeting-name {{
        font-size: 20px;
        font-weight: 700;
        color: #1F2421;
        letter-spacing: -0.3px;
        line-height: 1.2;
    }}

    .sync-badge {{
        background-color: rgba(0, 0, 0, 0.05);
        color: #4A524E;
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 500;
        border: 1px solid rgba(0, 0, 0, 0.08);
        white-space: nowrap;
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

    .home-hero {{
        background: linear-gradient(135deg, #1B4332 0%, #2D6A4F 100%);
        color: #FFFFFF;
        border-radius: 20px;
        padding: 16px;
        margin-bottom: 8px;
        box-shadow: 0 8px 20px rgba(27, 67, 50, 0.16);
    }}

    .home-hero-top {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 12px;
        opacity: 0.9;
        font-weight: 600;
        margin-bottom: 6px;
    }}

    .home-saldo-label {{
        font-size: 12.5px;
        opacity: 0.88;
        font-weight: 500;
    }}

    .home-saldo-val {{
        font-size: 24px;
        font-weight: 700;
        letter-spacing: -0.5px;
        margin: 2px 0 12px 0;
    }}

    .home-mini-grid {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 8px;
    }}

    .home-mini-card {{
        background: rgba(255, 255, 255, 0.14);
        border: 1px solid rgba(255, 255, 255, 0.18);
        border-radius: 12px;
        padding: 8px 10px;
    }}

    .home-mini-label {{
        font-size: 11px;
        opacity: 0.88;
        font-weight: 500;
    }}

    .home-mini-val {{
        font-size: 13.5px;
        font-weight: 700;
        margin-top: 2px;
    }}

    .trx-item {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        background-color: #F8F7F4;
        border: 1px solid #EAE7DD;
        border-radius: 14px;
        padding: 10px 12px;
        margin-bottom: 8px;
        transition: transform 0.15s ease, border-color 0.15s ease;
    }}

    .trx-item:hover {{
        transform: translateY(-1px);
        border-color: #C9C4B6;
    }}

    .trx-title {{
        font-size: 13px;
        font-weight: 700;
        color: #1F2421;
    }}

    .trx-sub {{
        font-size: 11.5px;
        color: #6B6D66;
        margin-top: 2px;
    }}

    .trx-amt-in {{
        font-size: 13px;
        font-weight: 700;
        color: #1B4332;
        text-align: right;
    }}

    .trx-amt-out {{
        font-size: 13px;
        font-weight: 700;
        color: #C8432B;
        text-align: right;
    }}

    .summary-box {{
        background-color: #F8F7F4;
        border: 1px solid #EAE7DD;
        border-radius: 16px;
        padding: 12px 14px;
        margin-bottom: 10px;
    }}

    .download-panel, .periode-panel {{
        background-color: #F8F7F4;
        border: 1px solid #EAE7DD;
        border-radius: 16px;
        padding: 12px;
        margin-top: 8px;
        margin-bottom: 10px;
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
        -webkit-text-fill-color: #000000 !important;
        padding: 10px 14px !important;
        height: 52px !important;
    }}
    div[data-testid="stNumberInput"] input::placeholder {{
        color: {placeholder_color} !important;
        -webkit-text-fill-color: {placeholder_color} !important;
        opacity: 1 !important;
    }}
    div[data-testid="stNumberInput"] button {{
        display: none !important;
    }}

    div.stButton > button,
    div[data-testid="stDownloadButton"] > button {{
        border-radius: 999px !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        padding: 6px 14px !important;
        min-height: 38px !important;
        transition: all 0.15s ease !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.03) !important;
    }}

    div.stButton > button p,
    div[data-testid="stDownloadButton"] > button p {{
        font-weight: inherit !important;
    }}

    div.stButton > button[kind="secondary"],
    div[data-testid="stDownloadButton"] > button {{
        background-color: {bg_input_soft} !important;
        color: #000000 !important;
        border: 1px solid {border_soft} !important;
    }}
    div.stButton > button[kind="secondary"]:hover,
    div[data-testid="stDownloadButton"] > button:hover {{
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
        border: 1.2px solid {border_soft} !important;
        border-radius: 12px !important;
        height: 44px !important;
    }}

    div[data-testid="stDateInput"] > div > div:focus-within,
    div[data-testid="stTextInput"] > div > div:focus-within {{
        border-color: {aksen_utama} !important;
    }}

    div[data-testid="stDateInput"] input,
    div[data-testid="stDateInput"] span,
    div[data-testid="stDateInput"] div,
    div[data-testid="stTextInput"] input {{
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
        font-weight: 600 !important;
        font-size: 14px !important;
    }}

    div[data-testid="stDateInput"] input,
    div[data-testid="stTextInput"] input {{
        background-color: transparent !important;
    }}

    div[data-testid="stTextInput"] input::placeholder {{
        color: {placeholder_color} !important;
        -webkit-text-fill-color: {placeholder_color} !important;
        font-weight: 500 !important;
        opacity: 1 !important;
    }}

    .nominal-ribuan-box div[data-testid="stTextInput"] > div > div {{
        background-color: {bg_input_soft} !important;
        border: 1.8px solid {aksen_utama} !important;
        border-radius: 14px !important;
        height: 52px !important;
    }}
    .nominal-ribuan-box div[data-testid="stTextInput"] input {{
        font-size: 20px !important;
        font-weight: 700 !important;
    }}
</style>
""", unsafe_allow_html=True)

# 5. Header Atas dengan Foto ke-2 (kimi.jpeg)
if banner_data_uri:
    st.markdown(
        f"""
        <div class="top-header-photo-wrap">
            <div class="top-header-photo">
                <img src="{banner_data_uri}" alt="Header Banner">
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    st.markdown(
        """
        <div class="top-header-photo-wrap">
            <div class="top-header-photo" style="display:flex;align-items:center;justify-content:center;color:#FFFFFF;font-size:12.5px;font-weight:600;padding:12px;text-align:center;">
                Simpan file <b>kimi.jpeg</b> di folder yang sama dengan aplikasi untuk menampilkan foto header.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# 6. Kontainer Utama
with st.container(border=True):
    st.markdown('<div class="sheet-handle"></div>', unsafe_allow_html=True)

    if st.session_state.halaman == "Home":
        st.markdown(
            f"""
            <div class="greeting-strip">
                <div>
                    <div class="greeting-sub" id="ucapan_waktu">{salam_awal}</div>
                    <div class="greeting-name">Panji &amp; Febby</div>
                </div>
                <div class="sync-badge">☁️ Tersinkron</div>
            </div>
            <script>
            (function() {{
                function sinkronSalam() {{
                    const doc = window.parent.document;
                    const el = doc.getElementById("ucapan_waktu");
                    if (!el) return;
                    const jam = new Date().getHours();
                    let teks = "Selamat malam,";
                    if (jam >= 4 && jam < 11) teks = "Selamat pagi,";
                    else if (jam >= 11 && jam < 15) teks = "Selamat siang,";
                    else if (jam >= 15 && jam < 18) teks = "Selamat sore,";
                    el.innerText = teks;
                }}
                sinkronSalam();
                setInterval(sinkronSalam, 60000);
            }})();
            </script>
            """,
            unsafe_allow_html=True
        )
    else:
        if st.button("🏠 Kembali ke Home", key="nav_back_home", use_container_width=True, type="secondary"):
            st.session_state.halaman = "Home"
            st.session_state.entry_mode_terkunci = False
            st.rerun()

    st.markdown(f"<hr style='margin: 10px 0 14px 0; border: 0; border-top: 1px solid {border_soft};'>", unsafe_allow_html=True)

    # =========================================================
    # HALAMAN 1: HOME (INTERAKTIF & RINGKAS)
    # =========================================================
    if st.session_state.halaman == "Home":
        df_home_raw = ambil_data_sheets(WEB_APP_URL)
        sekarang_home = pd.Timestamp.now(ZoneInfo("Asia/Jakarta")).tz_localize(None).normalize()
        awal_bulan_home = sekarang_home.replace(day=1)

        if not df_home_raw.empty and "ParsedDate" in df_home_raw.columns:
            df_home_bulanan = df_home_raw[
                df_home_raw["ParsedDate"].notna() &
                (df_home_raw["ParsedDate"] >= awal_bulan_home) &
                (df_home_raw["ParsedDate"] <= sekarang_home)
            ]
        else:
            df_home_bulanan = pd.DataFrame()

        in_bulan_home = float(df_home_bulanan["jumlah uang pemasukan"].sum()) if not df_home_bulanan.empty else 0.0
        out_bulan_home = float(df_home_bulanan["jumlah uang pengeluaran"].sum()) if not df_home_bulanan.empty else 0.0
        saldo_bulan_home = in_bulan_home - out_bulan_home

        is_hidden = st.session_state.hide_home_nominal
        tampil_saldo = "****" if is_hidden else format_rp(saldo_bulan_home)
        tampil_in = "****" if is_hidden else format_rp(in_bulan_home)
        tampil_out = "****" if is_hidden else format_rp(out_bulan_home)

        st.markdown(
            f"""
            <div class="home-hero">
                <div class="home-hero-top">
                    <span>✨ Ringkasan {sekarang_home.strftime("%B %Y")}</span>
                    <span>Panji & Febby</span>
                </div>
                <div class="home-saldo-label">Saldo Bersih Bulan Ini</div>
                <div class="home-saldo-val">{tampil_saldo}</div>
                <div class="home-mini-grid">
                    <div class="home-mini-card">
                        <div class="home-mini-label">↓ Pemasukan</div>
                        <div class="home-mini-val">{tampil_in}</div>
                    </div>
                    <div class="home-mini-card">
                        <div class="home-mini-label">↑ Pengeluaran</div>
                        <div class="home-mini-val">{tampil_out}</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        label_mata = "👁️ Tampilkan Nominal" if is_hidden else "🙈 Sembunyikan Nominal"
        if st.button(label_mata, key="btn_toggle_mata_home", use_container_width=True, type="secondary"):
            st.session_state.hide_home_nominal = not st.session_state.hide_home_nominal
            st.rerun()

        st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)

        c_q1, c_q2 = st.columns(2, gap="small")
        with c_q1:
            if st.button("↑ Catat Pengeluaran", key="home_quick_out", type="primary", use_container_width=True):
                st.session_state.halaman = "Entry"
                st.session_state.tipe = "Pengeluaran"
                st.session_state.entry_mode_terkunci = True
                st.session_state.kategori = "Kategori"
                st.session_state.buka_pilih_kategori = True
                st.rerun()
        with c_q2:
            if st.button("↓ Catat Pemasukan", key="home_quick_in", type="secondary", use_container_width=True):
                st.session_state.halaman = "Entry"
                st.session_state.tipe = "Pemasukan"
                st.session_state.entry_mode_terkunci = True
                st.session_state.kategori = "Kategori"
                st.session_state.buka_pilih_kategori = True
                st.rerun()

        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

        if st.button("📊 Buka Dashboard Lengkap", key="home_go_dash", type="secondary", use_container_width=True):
            st.session_state.halaman = "Dashboard"
            st.rerun()

        st.markdown('<div class="sub-title">🕒 Transaksi Terakhir</div>', unsafe_allow_html=True)

        if not df_home_raw.empty:
            df_recent = df_home_raw.sort_values(
                by=["ParsedDate", "_rowNumber"],
                ascending=[False, False],
                na_position="last"
            ).head(3)

            for _, r in df_recent.iterrows():
                is_in = float(r["jumlah uang pemasukan"]) > 0
                kat_lbl = r["Jenis Pemasukan"] if is_in else (r["Jenis Pengeluaran"] or "Lainnya")
                nom_val = float(r["jumlah uang pemasukan"]) if is_in else float(r["jumlah uang pengeluaran"])
                tgl_lbl = r["ParsedDate"].strftime("%d %b") if pd.notna(r["ParsedDate"]) else r["RawDate"]
                cat_lbl = f" • {r['Catatan']}" if str(r["Catatan"]).strip() else ""
                kelas_amt = "trx-amt-in" if is_in else "trx-amt-out"
                tanda_amt = "+" if is_in else "-"

                st.markdown(
                    f"""
                    <div class="trx-item">
                        <div>
                            <div class="trx-title">{kat_lbl}</div>
                            <div class="trx-sub">{tgl_lbl} • {r["Nama"] or "Bersama"}{cat_lbl}</div>
                        </div>
                        <div class="{kelas_amt}">{tanda_amt} {format_rp(nom_val)}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.caption("Belum ada transaksi tercatat. Klik **Catat Pengeluaran** atau **Catat Pemasukan** di atas untuk mulai.")

    # =========================================================
    # HALAMAN 2: ENTRY
    # =========================================================
    elif st.session_state.halaman == "Entry":
        judul_entry = (
            "Catat Pengeluaran"
            if (st.session_state.entry_mode_terkunci and st.session_state.tipe == "Pengeluaran")
            else ("Catat Pemasukan" if st.session_state.entry_mode_terkunci else "Entry")
        )
        st.markdown(f'<div class="card-title">{judul_entry}</div>', unsafe_allow_html=True)

        if not st.session_state.entry_mode_terkunci:
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
        nominal_key = f"input_nominal_{st.session_state.form_key}"
        st.markdown('<div class="nominal-ribuan-box">', unsafe_allow_html=True)
        raw_nominal_input = st.text_input(
            "Nominal",
            placeholder="0",
            label_visibility="collapsed",
            key=nominal_key
        )
        st.markdown('</div>', unsafe_allow_html=True)

        nominal_terformat, val_nominal = _format_ribuan_input(raw_nominal_input)
        if nominal_terformat and nominal_terformat != raw_nominal_input:
            st.session_state[nominal_key] = nominal_terformat
            st.rerun()

        components.html(f"""
        <script>
        (function() {{
            const doc = window.parent.document;
            const inputs = doc.querySelectorAll('div[data-testid="stTextInput"] input');
            for (const inp of inputs) {{
                if (inp.placeholder === "0") {{
                    inp.setAttribute("inputmode", "numeric");
                    if (!inp.dataset.ribuanBound) {{
                        inp.dataset.ribuanBound = "1";
                        inp.addEventListener("input", function() {{
                            const digits = this.value.replace(/[^0-9]/g, "");
                            if (!digits) {{
                                this.value = "";
                                return;
                            }}
                            const formatted = Number(digits).toLocaleString("id-ID");
                            if (this.value !== formatted) {{
                                this.value = formatted;
                            }}
                        }});
                    }}
                }}
            }}
        }})();
        </script>
        """, height=0)

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
                    [(IKON_PENGELUARAN[k], k) for k in KATEGORI_PENGELUARAN[i:i + 2]]
                    for i in range(0, len(KATEGORI_PENGELUARAN), 2)
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
            tgl_key = f"input_tgl_{st.session_state.form_key}"
            tanggal_input = st.date_input(
                "Tanggal",
                value=None if st.session_state.tanggal_kosong else hari_ini_wib,
                format="DD/MM/YYYY",
                label_visibility="collapsed",
                key=tgl_key
            )
            if tanggal_input is not None:
                st.session_state.tanggal_kosong = False
            tanggal_efektif = tanggal_input if tanggal_input is not None else hari_ini_wib
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
        if st.button("Submit", type="primary", use_container_width=True):
            if val_nominal > 0 and st.session_state.kategori != "Kategori":
                format_tgl_lengkap = format_tgl_indo(tanggal_efektif)

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
                    "RawDate": tanggal_efektif.strftime("%Y-%m-%d")
                }

                try:
                    response = requests.post(WEB_APP_URL, json=payload, timeout=20)
                    if response.status_code == 200:
                        ambil_data_sheets.clear()
                        st.success(f"Berhasil tersimpan: {st.session_state.tipe} {format_rp(val_nominal)}!")
                        st.session_state.form_key += 1
                        st.session_state.kategori = "Kategori"
                        st.session_state.tanggal_kosong = True
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
        if not st.session_state.dashboard_unlocked:
            st.markdown('<div class="card-title">🔒 Kunci Dashboard</div>', unsafe_allow_html=True)
            st.caption("Masukkan kata sandi untuk membuka Dashboard.")

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
                    st.session_state.buka_menu_download = False
                    st.session_state.buka_menu_periode = False
                    st.rerun()

            if st.button(
                f"🗓️ Periode ({st.session_state.periode_dash})",
                key="toggle_menu_periode",
                type="primary" if st.session_state.buka_menu_periode else "secondary",
                use_container_width=True
            ):
                st.session_state.buka_menu_periode = not st.session_state.buka_menu_periode
                st.rerun()

            if st.session_state.buka_menu_periode:
                st.markdown('<div class="periode-panel">', unsafe_allow_html=True)
                cols_p1 = st.columns(3, gap="small")
                for idx, p in enumerate(OPSI_PERIODE[:3]):
                    with cols_p1[idx]:
                        if st.button(
                            p,
                            key=f"periode_{p}",
                            use_container_width=True,
                            type="primary" if st.session_state.periode_dash == p else "secondary"
                        ):
                            st.session_state.periode_dash = p
                            st.rerun()

                st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)

                cols_p2 = st.columns(3, gap="small")
                for idx, p in enumerate(OPSI_PERIODE[3:]):
                    with cols_p2[idx]:
                        if st.button(
                            p,
                            key=f"periode_{p}",
                            use_container_width=True,
                            type="primary" if st.session_state.periode_dash == p else "secondary"
                        ):
                            st.session_state.periode_dash = p
                            st.rerun()

                if st.session_state.periode_dash == "Hari":
                    st.markdown('<div class="field-label" style="margin-top: 10px;">📅 Pilih Tanggal</div>', unsafe_allow_html=True)
                    tgl_pilihan_hari = st.date_input(
                        "Pilih Tanggal",
                        value=st.session_state.tanggal_hari_dash,
                        format="DD/MM/YYYY",
                        label_visibility="collapsed",
                        key="kalender_periode_hari"
                    )
                    st.session_state.tanggal_hari_dash = tgl_pilihan_hari

                st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="field-label" style="margin-top: 10px;">Filter Nama</div>', unsafe_allow_html=True)
            cols_n = st.columns(4, gap="small")
            for idx_n, nm in enumerate(OPSI_FILTER_NAMA):
                with cols_n[idx_n]:
                    if st.button(
                        nm,
                        key=f"filter_nama_{nm}",
                        use_container_width=True,
                        type="primary" if st.session_state.filter_nama_dash == nm else "secondary"
                    ):
                        st.session_state.filter_nama_dash = nm
                        st.rerun()

            df_raw = ambil_data_sheets(WEB_APP_URL)

            sekarang_ts = pd.Timestamp.now(ZoneInfo("Asia/Jakarta")).tz_localize(None).normalize()
            periode_aktif = st.session_state.periode_dash
            nama_aktif = st.session_state.filter_nama_dash

            if not df_raw.empty and "ParsedDate" in df_raw.columns:
                df_valid = df_raw.copy()
                parsed = pd.to_datetime(df_valid["ParsedDate"], errors="coerce")
                if getattr(parsed.dt, "tz", None) is not None:
                    parsed = parsed.dt.tz_localize(None)
                df_valid["ParsedDate"] = parsed.dt.normalize()

                if periode_aktif == "Hari":
                    tgl_target = pd.Timestamp(st.session_state.tanggal_hari_dash).tz_localize(None).normalize()
                    label_rentang = tgl_target.strftime("%d %b %Y")
                    df_filtered = df_valid[
                        df_valid["ParsedDate"].notna() &
                        (df_valid["ParsedDate"] == tgl_target)
                    ].copy()
                elif periode_aktif == "Minggu":
                    tgl_awal = sekarang_ts - pd.Timedelta(days=6)
                    label_rentang = f"{tgl_awal.strftime('%d %b')} - {sekarang_ts.strftime('%d %b %Y')}"
                    df_filtered = df_valid[
                        df_valid["ParsedDate"].notna() &
                        (df_valid["ParsedDate"] >= tgl_awal) &
                        (df_valid["ParsedDate"] <= sekarang_ts)
                    ].copy()
                elif periode_aktif == "Bulan":
                    tgl_awal = sekarang_ts.replace(day=1)
                    label_rentang = sekarang_ts.strftime("%B %Y")
                    df_filtered = df_valid[
                        df_valid["ParsedDate"].notna() &
                        (df_valid["ParsedDate"] >= tgl_awal) &
                        (df_valid["ParsedDate"] <= sekarang_ts)
                    ].copy()
                elif periode_aktif == "Semester":
                    bulan_awal_sem = 1 if sekarang_ts.month <= 6 else 7
                    tgl_awal = sekarang_ts.replace(month=bulan_awal_sem, day=1)
                    label_rentang = f"{tgl_awal.strftime('%b %Y')} - {sekarang_ts.strftime('%b %Y')}"
                    df_filtered = df_valid[
                        df_valid["ParsedDate"].notna() &
                        (df_valid["ParsedDate"] >= tgl_awal) &
                        (df_valid["ParsedDate"] <= sekarang_ts)
                    ].copy()
                elif periode_aktif == "Tahun":
                    tgl_awal = sekarang_ts.replace(month=1, day=1)
                    label_rentang = sekarang_ts.strftime("Tahun %Y")
                    df_filtered = df_valid[
                        df_valid["ParsedDate"].notna() &
                        (df_valid["ParsedDate"] >= tgl_awal) &
                        (df_valid["ParsedDate"] <= sekarang_ts)
                    ].copy()
                else:
                    label_rentang = "Semua Data"
                    df_filtered = df_valid.copy()

                if nama_aktif != "Semua":
                    df_filtered = df_filtered[df_filtered["Nama"].str.strip().str.lower() == nama_aktif.lower()].copy()
            else:
                df_filtered = pd.DataFrame(columns=[
                    "_rowNumber", "Nama", "Hari tanggal bulan tahun", "Jenis Pengeluaran",
                    "jumlah uang pengeluaran", "Jenis Pemasukan",
                    "jumlah uang pemasukan", "Catatan", "RawDate", "ParsedDate"
                ])
                label_rentang = "-"

            st.caption(f"Periode: **{periode_aktif}** ({label_rentang}) • Nama: **{nama_aktif}** • Data: **{len(df_filtered)}** baris")

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
            render_donut_with_side_stats(
                labels=["Pemasukan", "Pengeluaran"],
                values=[total_pemasukan, total_pengeluaran],
                colors=["#1B4332", "#C8432B"],
                chart_id="chartVsInOut",
                height=210
            )

            st.markdown('<div class="sub-title">2. Major Expense</div>', unsafe_allow_html=True)

            df_exp = df_filtered[df_filtered["jumlah uang pengeluaran"] > 0].copy() if not df_filtered.empty else pd.DataFrame()
            if not df_exp.empty and total_pengeluaran > 0:
                df_exp["Kategori"] = df_exp["Jenis Pengeluaran"].replace("", "Lainnya").fillna("Lainnya")
                rekap_kat = (
                    df_exp.groupby("Kategori", as_index=False)["jumlah uang pengeluaran"]
                    .sum()
                    .sort_values("jumlah uang pengeluaran", ascending=False)
                )
                rekap_kat["Persentase (%)"] = (rekap_kat["jumlah uang pengeluaran"] / total_pengeluaran) * 100

                palette_donut = [
                    "#C8432B", "#E07A5F", "#F2CC8F", "#3D405B", "#81B29A",
                    "#2A9D8F", "#E9C46A", "#F4A261", "#E76F51", "#6D597A"
                ]
                donut_colors = [palette_donut[i % len(palette_donut)] for i in range(len(rekap_kat))]

                tinggi_box_major = min(max(210, len(rekap_kat) * 54 + 28), 340)
                render_donut_with_side_stats(
                    labels=rekap_kat["Kategori"].tolist(),
                    values=rekap_kat["jumlah uang pengeluaran"].tolist(),
                    colors=donut_colors,
                    chart_id="chartMajorExpense",
                    height=tinggi_box_major
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
                st.info(f"Belum ada data pengeluaran pada periode **{periode_aktif}** ({nama_aktif}).")

            # Menu Download
            st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)
            label_btn_dl = "✖️ Tutup Menu Download" if st.session_state.buka_menu_download else "📥 Download"
            if st.button(
                label_btn_dl,
                key="toggle_menu_download",
                type="primary" if st.session_state.buka_menu_download else "secondary",
                use_container_width=True
            ):
                st.session_state.buka_menu_download = not st.session_state.buka_menu_download
                st.rerun()

            if st.session_state.buka_menu_download:
                df_exp_file = build_export_dataframe(df_filtered)
                stamp_tgl = sekarang_ts.strftime("%Y%m%d")
                base_nama = f"keuangan_panji_febby_{nama_aktif.lower()}_{periode_aktif.lower()}_{stamp_tgl}"

                excel_bytes, excel_mime, excel_ext = generate_excel_bytes(df_exp_file)
                csv_bytes = df_exp_file.to_csv(index=False).encode("utf-8-sig")
                pdf_bytes = generate_pdf_bytes(
                    periode_aktif, label_rentang, nama_aktif,
                    total_pemasukan, total_pengeluaran, selisih_bersih,
                    df_exp_file
                )

                st.markdown('<div class="download-panel">', unsafe_allow_html=True)
                st.caption(f"Pilih format file untuk **{nama_aktif}** • **{periode_aktif}**:")

                st.download_button(
                    label=f"📗 Download Excel (.{excel_ext.upper()})",
                    data=excel_bytes,
                    file_name=f"{base_nama}.{excel_ext}",
                    mime=excel_mime,
                    use_container_width=True,
                    key="dl_excel"
                )

                st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)

                st.download_button(
                    label="📊 Download Spreadsheet (.CSV)",
                    data=csv_bytes,
                    file_name=f"{base_nama}_spreadsheet.csv",
                    mime="text/csv",
                    use_container_width=True,
                    key="dl_spreadsheet"
                )

                st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)

                st.download_button(
                    label="📄 Download PDF (.PDF)",
                    data=pdf_bytes,
                    file_name=f"{base_nama}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    key="dl_pdf"
                )

                st.markdown('</div>', unsafe_allow_html=True)

            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
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
                    df_urut = df_filtered.sort_values(by=["ParsedDate", "_rowNumber"], ascending=[False, False], na_position="last").reset_index(drop=True)

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
                            resp = requests.post(WEB_APP_URL, json=payload_update, timeout=20)
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
                    st.info(f"Tidak ada transaksi pada periode **{periode_aktif}** ({nama_aktif}) untuk diedit.")
