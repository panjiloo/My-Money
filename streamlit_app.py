import base64
from datetime import datetime
import io
import json
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
import requests
import streamlit as st
import streamlit.components.v1 as components

# 1. Konfigurasi Halaman
st.set_page_config(
    page_title="Panji & Febby - Keuangan",
    page_icon="💰",
    layout="centered",
    initial_sidebar_state="collapsed",
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
    "Lainnya",
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
    "Lainnya": "📦",
}
OPSI_NAMA = ["Panji", "Febby", "Bersama"]
OPSI_FILTER_NAMA = ["Semua", "Panji", "Febby", "Bersama"]
OPSI_PERIODE = ["Hari", "Minggu", "Bulan", "Semester", "Tahun", "Semua"]

# 2. Inisialisasi Session State
if "halaman" not in st.session_state:
    st.session_state.halaman = "Home"
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
    st.session_state.tanggal_kosong = True
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
        if s.rfind(",") > s.rfind("."):
            s = s.replace(".", "").replace(",", ".")
        else:
            s = s.replace(",", "")
    elif "." in s:
        parts = s.split(".")
        if len(parts) > 1 and all(len(p) == 3 and p.isdigit() for p in parts[1:]):
            s = "".join(parts)
    elif "," in s:
        parts = s.split(",")
        if len(parts) > 1 and all(len(p) == 3 and p.isdigit() for p in parts[1:]):
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
        "_rowNumber",
        "Nama",
        "Hari tanggal bulan tahun",
        "Jenis Pengeluaran",
        "jumlah uang pengeluaran",
        "Jenis Pemasukan",
        "jumlah uang pemasukan",
        "Catatan",
        "RawDate",
        "ParsedDate",
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

            col_peng_jml = _cari_kolom(
                df,
                ["jumlah uang pengeluaran", "Jumlah_Uang_Pengeluaran", "Jumlah Uang Pengeluaran", "Pengeluaran"],
            )
            col_pem_jml = _cari_kolom(
                df,
                ["jumlah uang pemasukan", "Jumlah_Uang_Pemasukan", "Jumlah Uang Pemasukan", "Pemasukan"],
            )

            df["jumlah uang pengeluaran"] = df[col_peng_jml].apply(_bersihkan_angka_rp) if col_peng_jml else 0.0
            df["jumlah uang pemasukan"] = df[col_pem_jml].apply(_bersihkan_angka_rp) if col_pem_jml else 0.0

            mapping_teks = {
                "Nama": ["Nama", "Dibayar oleh", "Diterima oleh"],
                "Hari tanggal bulan tahun": ["Hari tanggal bulan tahun", "Hari_tanggal_bulan_tahun", "Tanggal Indo"],
                "Jenis Pengeluaran": ["Jenis Pengeluaran", "Jenis_Pengeluaran", "Kategori Pengeluaran"],
                "Jenis Pemasukan": ["Jenis Pemasukan", "Jenis_Pemasukan", "Kategori Pemasukan"],
                "Catatan": ["Catatan", "Keterangan", "Notes"],
                "RawDate": ["RawDate", "Tanggal", "Date"],
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


def kirim_transaksi_ke_sheets(payload_dict):
    resp = requests.post(WEB_APP_URL, json=payload_dict, timeout=20)
    resp.raise_for_status()
    try:
        data = resp.json()
        if isinstance(data, dict) and data.get("status") == "error":
            raise RuntimeError(data.get("message", "Gagal menyimpan ke Google Sheets"))
    except ValueError:
        pass


def format_rp(angka):
    return f"Rp {int(round(angka)):,}".replace(",", ".")


def format_tgl_indo(tgl_date):
    nama_hari = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"][tgl_date.weekday()]
    bulan_str = [
        "Januari",
        "Februari",
        "Maret",
        "April",
        "Mei",
        "Juni",
        "Juli",
        "Agustus",
        "September",
        "Oktober",
        "November",
        "Desember",
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

    components.html(
        f"""
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
    """,
        height=height,
    )


def build_export_dataframe(df_src):
    if df_src.empty:
        return pd.DataFrame(
            columns=["Tanggal", "Nama", "Jenis", "Kategori", "Pemasukan (Rp)", "Pengeluaran (Rp)", "Catatan"]
        )
    rows = []
    for _, r in df_src.iterrows():
        is_in = float(r["jumlah uang pemasukan"]) > 0
        jenis = "Pemasukan" if is_in else "Pengeluaran"
        kat = r["Jenis Pemasukan"] if is_in else r["Jenis Pengeluaran"]
        tgl_str = r["ParsedDate"].strftime("%Y-%m-%d") if pd.notna(r["ParsedDate"]) else r["RawDate"]
        rows.append(
            {
                "Tanggal": tgl_str,
                "Nama": r["Nama"],
                "Jenis": jenis,
                "Kategori": kat,
                "Pemasukan (Rp)": int(round(float(r["jumlah uang pemasukan"]))),
                "Pengeluaran (Rp)": int(round(float(r["jumlah uang pengeluaran"]))),
                "Catatan": r["Catatan"],
            }
        )
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


def generate_pdf_bytes(
    periode_aktif, label_rentang, nama_filter, total_pemasukan, total_pengeluaran, selisih_bersih, df_export
):
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
        "Daftar Transaksi:",
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

    objects = [
        b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n",
        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n",
        (
            b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] "
            b"/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>\nendobj\n"
        ),
        b"4 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n",
        (
            f"5 0 obj\n<< /Length {len(stream_data)} >>\nstream\n".encode("latin-1")
            + stream_data
            + b"\nendstream\nendobj\n"
        ),
    ]

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


def filter_df_periode(df_src, periode, tgl_acuan, nama_filter):
    if df_src.empty:
        return df_src.copy(), "Semua Data"

    out = df_src.copy()
    if nama_filter != "Semua":
        out = out[out["Nama"].str.lower() == nama_filter.lower()]

    valid_dates = out["ParsedDate"].dropna()
    if periode == "Semua" or valid_dates.empty:
        return out, "Semua Periode"

    dt_ref = pd.Timestamp(tgl_acuan).normalize()
    if periode == "Hari":
        out = out[out["ParsedDate"] == dt_ref]
        return out, format_tgl_indo(tgl_acuan)
    if periode == "Minggu":
        start_week = dt_ref - pd.Timedelta(days=int(dt_ref.dayofweek))
        end_week = start_week + pd.Timedelta(days=6)
        out = out[(out["ParsedDate"] >= start_week) & (out["ParsedDate"] <= end_week)]
        return out, f"{start_week.strftime('%d %b %Y')} - {end_week.strftime('%d %b %Y')}"
    if periode == "Bulan":
        out = out[
            (out["ParsedDate"].dt.year == dt_ref.year) & (out["ParsedDate"].dt.month == dt_ref.month)
        ]
        return out, dt_ref.strftime("%B %Y")
    if periode == "Semester":
        sem = 1 if dt_ref.month <= 6 else 2
        months = range(1, 7) if sem == 1 else range(7, 13)
        out = out[(out["ParsedDate"].dt.year == dt_ref.year) & (out["ParsedDate"].dt.month.isin(months))]
        return out, f"Semester {sem} - {dt_ref.year}"
    if periode == "Tahun":
        out = out[out["ParsedDate"].dt.year == dt_ref.year]
        return out, f"Tahun {dt_ref.year}"

    return out, "Semua Periode"


# Tema dinamis: merah saat di halaman Entry dengan tipe Pengeluaran, hijau untuk lainnya
is_tema_merah = st.session_state.halaman == "Entry" and st.session_state.tipe == "Pengeluaran"

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

if st.session_state.halaman == "Entry" and st.session_state.tanggal_kosong:
    css_date_empty = """
    div[data-testid="stDateInput"] > div > div {
        background-color: var(--bg-input-soft) !important;
        border: 1.2px solid var(--border-soft) !important;
        border-radius: 12px !important;
        height: 44px !important;
    }
    div[data-testid="stDateInput"] input,
    div[data-testid="stDateInput"] span,
    div[data-testid="stDateInput"] div {
        color: transparent !important;
        -webkit-text-fill-color: transparent !important;
        background-color: transparent !important;
    }
    div[data-testid="stDateInput"] button,
    div[data-testid="stDateInput"] svg {
        opacity: 0 !important;
    }
    """
else:
    css_date_empty = """
    div[data-testid="stDateInput"] > div > div {
        background-color: var(--bg-input-soft) !important;
        border: 1.2px solid var(--border-soft) !important;
        border-radius: 12px !important;
        height: 44px !important;
    }
    div[data-testid="stDateInput"] input,
    div[data-testid="stDateInput"] span,
    div[data-testid="stDateInput"] div {
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
        font-weight: 600 !important;
        font-size: 14px !important;
    }
    """

# 4. Custom CSS
st.markdown(
    f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

    :root {{
        --bg-input-soft: {bg_input_soft};
        --border-soft: {border_soft};
    }}

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
        background: linear-gradient(135deg, #1B4332 0%, #2D6A4F 100%);
        color: #FFFFFF;
        border-radius: 18px;
        padding: 13px 16px;
        margin-bottom: 6px;
        box-shadow: 0 8px 20px rgba(27, 67, 50, 0.16);
        gap: 10px;
    }}

    .greeting-sub {{
        font-size: 12.5px;
        color: rgba(255, 255, 255, 0.88);
        margin-bottom: 2px;
        font-weight: 500;
    }}

    .greeting-name {{
        font-size: 20px;
        font-weight: 700;
        color: #FFFFFF;
        letter-spacing: -0.3px;
        line-height: 1.2;
    }}

    .sync-badge {{
        background-color: rgba(255, 255, 255, 0.16);
        color: #FFFFFF;
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        border: 1px solid rgba(255, 255, 255, 0.22);
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

    div[data-testid="stTextInput"] input,
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
    div[data-testid="stTextInput"] input::placeholder,
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

    div[data-testid="stElementContainer"]:has(.kategori-in) + div[data-testid="stElementContainer"] div.stButton > button {{
        background-color: #1B4332 !important;
        color: #FFFFFF !important;
        border: 1px solid #1B4332 !important;
    }}
    div[data-testid="stElementContainer"]:has(.kategori-out) + div[data-testid="stElementContainer"] div.stButton > button {{
        background-color: #C8432B !important;
        color: #FFFFFF !important;
        border: 1px solid #C8432B !important;
    }}
    div[data-testid="stElementContainer"]:has(.kategori-opsi-in) + div[data-testid="stElementContainer"] div.stButton > button[kind="secondary"] {{
        background-color: #EAF4EE !important;
        color: #1B4332 !important;
        border: 1px solid #B7D8C4 !important;
    }}
    div[data-testid="stElementContainer"]:has(.kategori-opsi-out) + div[data-testid="stElementContainer"] div.stButton > button[kind="secondary"] {{
        background-color: #FDECE9 !important;
        color: #C8432B !important;
        border: 1px solid #F2C7BF !important;
    }}

    {css_date_empty}
</style>
""",
    unsafe_allow_html=True,
)

# 5. Banner & Header
if banner_data_uri:
    st.markdown(
        f"""
        <div class="top-header-photo-wrap">
            <div class="top-header-photo">
                <img src="{banner_data_uri}" alt="Banner Keuangan" />
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

df_all = ambil_data_sheets(WEB_APP_URL)

with st.container(border=True):
    st.markdown('<div class="sheet-handle"></div>', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="greeting-strip">
            <div>
                <div class="greeting-sub">{salam_awal}</div>
                <div class="greeting-name">Panji &amp; Febby</div>
            </div>
            <div class="sync-badge">{len(df_all)} data</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    nav_cols = st.columns(3)
    with nav_cols[0]:
        if st.button("Home", use_container_width=True, type="primary" if st.session_state.halaman == "Home" else "secondary"):
            st.session_state.halaman = "Home"
            st.rerun()
    with nav_cols[1]:
        if st.button("Input", use_container_width=True, type="primary" if st.session_state.halaman == "Entry" else "secondary"):
            st.session_state.halaman = "Entry"
            st.rerun()
    with nav_cols[2]:
        if st.button("Dashboard", use_container_width=True, type="primary" if st.session_state.halaman == "Dashboard" else "secondary"):
            st.session_state.halaman = "Dashboard"
            st.rerun()

    # Halaman HOME
    if st.session_state.halaman == "Home":
        st.markdown('<div class="card-title">Ringkasan Keuangan</div>', unsafe_allow_html=True)
        total_in = float(df_all["jumlah uang pemasukan"].sum()) if not df_all.empty else 0.0
        total_out = float(df_all["jumlah uang pengeluaran"].sum()) if not df_all.empty else 0.0
        saldo_net = total_in - total_out

        teks_saldo = "Rp •••••••" if st.session_state.hide_home_nominal else format_rp(saldo_net)
        teks_in = "Rp ••••••" if st.session_state.hide_home_nominal else format_rp(total_in)
        teks_out = "Rp ••••••" if st.session_state.hide_home_nominal else format_rp(total_out)

        st.markdown(
            f"""
            <div class="home-hero">
                <div class="home-hero-top">
                    <span>SALDO BERSIH</span>
                    <span>WIB</span>
                </div>
                <div class="home-saldo-val">{teks_saldo}</div>
                <div class="home-mini-grid">
                    <div class="home-mini-card">
                        <div class="home-mini-label">Pemasukan</div>
                        <div class="home-mini-val">{teks_in}</div>
                    </div>
                    <div class="home-mini-card">
                        <div class="home-mini-label">Pengeluaran</div>
                        <div class="home-mini-val">{teks_out}</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("Tampilkan / Sembunyikan Nominal", use_container_width=True, type="secondary"):
            st.session_state.hide_home_nominal = not st.session_state.hide_home_nominal
            st.rerun()

        st.markdown('<div class="sub-title">Transaksi Terakhir</div>', unsafe_allow_html=True)
        if df_all.empty:
            st.info("Belum ada transaksi tercatat.")
        else:
            for _, row in df_all.tail(8).iloc[::-1].iterrows():
                is_in = float(row["jumlah uang pemasukan"]) > 0
                nominal = float(row["jumlah uang pemasukan"]) if is_in else float(row["jumlah uang pengeluaran"])
                kat = row["Jenis Pemasukan"] if is_in else row["Jenis Pengeluaran"]
                tgl_label = row["Hari tanggal bulan tahun"] or (
                    row["ParsedDate"].strftime("%d %b %Y") if pd.notna(row["ParsedDate"]) else "-"
                )
                catatan_txt = f" • {row['Catatan']}" if row["Catatan"] else ""
                cls_amt = "trx-amt-in" if is_in else "trx-amt-out"
                tanda = "+" if is_in else "-"
                st.markdown(
                    f"""
                    <div class="trx-item">
                        <div>
                            <div class="trx-title">{kat or 'Transaksi'}</div>
                            <div class="trx-sub">{row['Nama'] or '-'} • {tgl_label}{catatan_txt}</div>
                        </div>
                        <div class="{cls_amt}">{tanda} {format_rp(nominal)}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    # Halaman ENTRY (Input Nominal Jutaan Aman)
    elif st.session_state.halaman == "Entry":
        st.markdown('<div class="card-title">Catat Transaksi</div>', unsafe_allow_html=True)

        tipe_cols = st.columns(2)
        with tipe_cols[0]:
            if st.button("Pengeluaran", use_container_width=True, type="primary" if st.session_state.tipe == "Pengeluaran" else "secondary"):
                st.session_state.tipe = "Pengeluaran"
                st.session_state.kategori = "Kategori"
                st.rerun()
        with tipe_cols[1]:
            if st.button("Pemasukan", use_container_width=True, type="primary" if st.session_state.tipe == "Pemasukan" else "secondary"):
                st.session_state.tipe = "Pemasukan"
                st.session_state.kategori = "Kategori"
                st.rerun()

        st.markdown('<div class="field-label">Nominal (Rp)</div>', unsafe_allow_html=True)
        raw_nominal = st.text_input(
            "Nominal",
            key=f"nominal_input_{st.session_state.form_key}",
            placeholder="Contoh: 5585000 atau 5.585.000",
            label_visibility="collapsed",
        )
        nominal_terformat, nominal_angka = _format_ribuan_input(raw_nominal)
        if nominal_angka > 0:
            st.caption(f"Nominal terbaca: **Rp {nominal_terformat}**")

        st.markdown('<div class="field-label">Kategori</div>', unsafe_allow_html=True)
        marker_kat = "kategori-out" if st.session_state.tipe == "Pengeluaran" else "kategori-in"
        st.markdown(f'<span class="{marker_kat}"></span>', unsafe_allow_html=True)
        label_btn_kat = st.session_state.kategori if st.session_state.kategori != "Kategori" else "Pilih Kategori"
        if st.button(label_btn_kat, use_container_width=True, type="primary"):
            st.session_state.buka_pilih_kategori = not st.session_state.buka_pilih_kategori
            st.rerun()

        if st.session_state.buka_pilih_kategori:
            daftar_kat = KATEGORI_PENGELUARAN if st.session_state.tipe == "Pengeluaran" else KATEGORI_PEMASUKAN
            marker_opsi = "kategori-opsi-out" if st.session_state.tipe == "Pengeluaran" else "kategori-opsi-in"
            st.markdown(f'<span class="{marker_opsi}"></span>', unsafe_allow_html=True)
            for idx_k in range(0, len(daftar_kat), 2):
                row_kat = st.columns(2)
                for sub_i, kat_item in enumerate(daftar_kat[idx_k : idx_k + 2]):
                    with row_kat[sub_i]:
                        ikon = IKON_PENGELUARAN.get(kat_item, "📌") if st.session_state.tipe == "Pengeluaran" else "💵"
                        if st.button(f"{ikon} {kat_item}", key=f"kat_{kat_item}_{st.session_state.form_key}", use_container_width=True, type="secondary"):
                            st.session_state.kategori = kat_item
                            st.session_state.buka_pilih_kategori = False
                            st.rerun()

        st.markdown('<div class="field-label">Nama</div>', unsafe_allow_html=True)
        nama_cols = st.columns(3)
        for idx_n, nama_item in enumerate(OPSI_NAMA):
            with nama_cols[idx_n]:
                if st.button(nama_item, key=f"nama_{nama_item}", use_container_width=True, type="primary" if st.session_state.dibayar_oleh == nama_item else "secondary"):
                    st.session_state.dibayar_oleh = nama_item
                    st.rerun()

        st.markdown('<div class="field-label">Tanggal</div>', unsafe_allow_html=True)
        tgl_val = st.date_input(
            "Tanggal Transaksi",
            value=datetime.now(ZoneInfo("Asia/Jakarta")).date(),
            key=f"tgl_input_{st.session_state.form_key}",
            label_visibility="collapsed",
        )
        if tgl_val:
            st.session_state.tanggal_kosong = False

        st.markdown('<div class="field-label">Catatan (Opsional)</div>', unsafe_allow_html=True)
        catatan_val = st.text_input(
            "Catatan",
            key=f"catatan_input_{st.session_state.form_key}",
            placeholder="Keterangan tambahan...",
            label_visibility="collapsed",
        )

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Simpan Transaksi", use_container_width=True, type="primary"):
            if nominal_angka <= 0:
                st.error("Masukkan nominal lebih besar dari 0.")
            elif st.session_state.kategori == "Kategori":
                st.error("Pilih kategori terlebih dahulu.")
            else:
                is_peng = st.session_state.tipe == "Pengeluaran"
                payload = {
                    "Nama": st.session_state.dibayar_oleh,
                    "Tanggal": tgl_val.strftime("%Y-%m-%d"),
                    "Hari tanggal bulan tahun": format_tgl_indo(tgl_val),
                    "Jenis Pengeluaran": st.session_state.kategori if is_peng else "",
                    "jumlah uang pengeluaran": int(nominal_angka) if is_peng else 0,
                    "Jenis Pemasukan": "" if is_peng else st.session_state.kategori,
                    "jumlah uang pemasukan": 0 if is_peng else int(nominal_angka),
                    "Catatan": (catatan_val or "").strip(),
                }
                try:
                    kirim_transaksi_ke_sheets(payload)
                    st.cache_data.clear()
                    st.session_state.form_key += 1
                    st.session_state.kategori = "Kategori"
                    st.success(f"Tersimpan: {format_rp(nominal_angka)}")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Gagal menyimpan: {exc}")

    # Halaman DASHBOARD
    elif st.session_state.halaman == "Dashboard":
        st.markdown('<div class="card-title">Dashboard Keuangan</div>', unsafe_allow_html=True)
        if not st.session_state.dashboard_unlocked:
            pwd_in = st.text_input("Password Dashboard", type="password", placeholder="Masukkan password...", label_visibility="collapsed")
            if st.button("Buka Dashboard", use_container_width=True, type="primary"):
                if pwd_in == DASHBOARD_PASSWORD:
                    st.session_state.dashboard_unlocked = True
                    st.rerun()
                else:
                    st.error("Password salah.")
        else:
            if st.button(f"Periode: {st.session_state.periode_dash}", use_container_width=True, type="secondary"):
                st.session_state.buka_menu_periode = not st.session_state.buka_menu_periode
                st.rerun()

            if st.session_state.buka_menu_periode:
                st.markdown('<div class="periode-panel">', unsafe_allow_html=True)
                p_cols = st.columns(3)
                for idx_p, p_opt in enumerate(OPSI_PERIODE):
                    with p_cols[idx_p % 3]:
                        if st.button(p_opt, key=f"per_{p_opt}", use_container_width=True, type="primary" if st.session_state.periode_dash == p_opt else "secondary"):
                            st.session_state.periode_dash = p_opt
                            st.session_state.buka_menu_periode = False
                            st.rerun()
                st.session_state.tanggal_hari_dash = st.date_input("Tanggal Acuan", value=st.session_state.tanggal_hari_dash)
                st.markdown("</div>", unsafe_allow_html=True)

            n_cols = st.columns(4)
            for idx_fn, fn_opt in enumerate(OPSI_FILTER_NAMA):
                with n_cols[idx_fn]:
                    if st.button(fn_opt, key=f"fn_{fn_opt}", use_container_width=True, type="primary" if st.session_state.filter_nama_dash == fn_opt else "secondary"):
                        st.session_state.filter_nama_dash = fn_opt
                        st.rerun()

            df_filt, label_rentang = filter_df_periode(
                df_all,
                st.session_state.periode_dash,
                st.session_state.tanggal_hari_dash,
                st.session_state.filter_nama_dash,
            )
            st.caption(f"Rentang: **{label_rentang}** • Nama: **{st.session_state.filter_nama_dash}**")

            tot_in = float(df_filt["jumlah uang pemasukan"].sum()) if not df_filt.empty else 0.0
            tot_out = float(df_filt["jumlah uang pengeluaran"].sum()) if not df_filt.empty else 0.0
            net_val = tot_in - tot_out

            st.markdown(
                f"""
                <div class="summary-box">
                    <div class="summary-label">Total Pemasukan</div>
                    <div class="summary-val-in">{format_rp(tot_in)}</div>
                    <div class="summary-label" style="margin-top:8px;">Total Pengeluaran</div>
                    <div class="summary-val-out">{format_rp(tot_out)}</div>
                    <div class="summary-label" style="margin-top:8px;">Saldo Bersih</div>
                    <div class="summary-val-net">{format_rp(net_val)}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if not df_filt.empty and tot_out > 0:
                df_out_cat = (
                    df_filt[df_filt["jumlah uang pengeluaran"] > 0]
                    .groupby("Jenis Pengeluaran")["jumlah uang pengeluaran"]
                    .sum()
                    .sort_values(ascending=False)
                )
                palette_out = ["#C8432B", "#E07A5F", "#F2CC8F", "#3D405B", "#81B29A", "#B56576"]
                colors_out = [palette_out[i % len(palette_out)] for i in range(len(df_out_cat))]
                render_donut_with_side_stats(
                    [k or "Lainnya" for k in df_out_cat.index.tolist()],
                    df_out_cat.values.tolist(),
                    colors_out,
                    chart_id="donutPengeluaran",
                    height=245,
                )

            if st.button("Download Laporan", use_container_width=True, type="secondary"):
                st.session_state.buka_menu_download = not st.session_state.buka_menu_download
                st.rerun()

            if st.session_state.buka_menu_download:
                st.markdown('<div class="download-panel">', unsafe_allow_html=True)
                df_exp = build_export_dataframe(df_filt)
                xlsx_bytes, mime_xlsx, ext_xlsx = generate_excel_bytes(df_exp)
                pdf_bytes = generate_pdf_bytes(
                    st.session_state.periode_dash,
                    label_rentang,
                    st.session_state.filter_nama_dash,
                    tot_in,
                    tot_out,
                    net_val,
                    df_exp,
                )
                d_cols = st.columns(2)
                with d_cols[0]:
                    st.download_button(
                        f"Unduh .{ext_xlsx.upper()}",
                        data=xlsx_bytes,
                        file_name=f"keuangan_{st.session_state.periode_dash.lower()}.{ext_xlsx}",
                        mime=mime_xlsx,
                        use_container_width=True,
                    )
                with d_cols[1]:
                    st.download_button(
                        "Unduh .PDF",
                        data=pdf_bytes,
                        file_name=f"keuangan_{st.session_state.periode_dash.lower()}.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                    )
                st.markdown("</div>", unsafe_allow_html=True)
