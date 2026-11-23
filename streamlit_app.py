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
OPSI_NAMA = ["Panji", "Febby", "
