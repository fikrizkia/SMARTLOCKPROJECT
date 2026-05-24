import streamlit as st
import pandas as pd
import gspread
import plotly.express as px
import os
import requests
from dotenv import load_dotenv
import sys
import paho.mqtt.client as mqtt
from streamlit_autorefresh import st_autorefresh
import random
import time

# ==========================================
# 1. KONFIGURASI HALAMAN & ENVIRONMENT
# ==========================================
st.set_page_config(page_title="Smart Locker OS", page_icon="⚡", layout="wide", initial_sidebar_state="collapsed")
st_autorefresh(interval=3000, limit=None, key="realtime_mqtt_refresh")

# Muat variabel environment dari file .env (Pastikan file .env masuk ke .gitignore)
load_dotenv()
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")    # Masukkan ID Google Sheets Anda di file .env
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")    # Masukkan API Key Google Gemini Anda di file .env

# ==========================================
# 2. KONEKSI MQTT (MULTI-TOPIC LISTENER)
# ==========================================
@st.cache_resource
def init_mqtt():
    unik_id = f"Dash_Suhu_{random.randint(1000, 9999)}"
    try:
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id=unik_id, protocol=mqtt.MQTTv311)
    except AttributeError:
        client = mqtt.Client(client_id=unik_id, protocol=mqtt.MQTTv311)
    
    # Kotak surat (placeholder) untuk 3 loker
    client.s = {"suhu01": "...", "suhu02": "...", "suhu03": "..."}
    
    def on_connect(client, userdata, flags, rc, *args):
        if rc == 0:
            # Ganti 'nama_pengguna' dengan prefix topik MQTT milik Anda sendiri
            client.subscribe([("nama_pengguna/smartlock/suhu01", 0), 
                              ("nama_pengguna/smartlock/suhu02", 0), 
                              ("nama_pengguna/smartlock/suhu03", 0)])
            
    def on_message(client, userdata, msg):
        topic = msg.topic.split('/')[-1]
        client.s[topic] = msg.payload.decode("utf-8")
        
    client.on_connect = on_connect
    client.on_message = on_message
    
    # Konfigurasi Broker MQTT Publik (Ganti jika menggunakan broker privat)
    client.connect("broker.emqx.io", 1883, 60)
    client.loop_start() 
    return client

mqtt_client = init_mqtt()
suhu = mqtt_client.s

# ==========================================
# 3. LOAD DATA & SINKRONISASI GOOGLE SHEETS
# ==========================================
def load_data():
    try:
        # Ganti 'kunci.json' dengan path/nama file kredensial Service Account Google Cloud Anda
        gc = gspread.service_account(filename='kunci.json')
        sh = gc.open_by_key(SPREADSHEET_ID)
        sheet_log = sh.get_worksheet(0)
        data = sheet_log.get_all_values()
        
        if len(data) > 1:
            df = pd.DataFrame(data[1:], columns=["Waktu", "ID Loker", "Nama Alat", "Durasi", "Status Log", "Suhu", "Nama Lengkap", "NIM", "Telp", "Email"])
            return df
        return pd.DataFrame()
    except: 
        return pd.DataFrame()

# Sinkronisasi Data Suhu MQTT ke Google Sheets setiap 60 detik
if 'last_sync' not in st.session_state: 
    st.session_state.last_sync = 0
    
if time.time() - st.session_state.last_sync > 60:
    try:
        gc = gspread.service_account(filename='kunci.json')
        sh = gc.open_by_key(SPREADSHEET_ID)
        sheet_stok = sh.get_worksheet(1)
        headers = sheet_stok.row_values(1)
        col_suhu = headers.index("SUHU") + 1
        
        for i, row in enumerate(sheet_stok.get_all_records(), start=2):
            loker = row.get('ID LOKER')
            if loker in ["LOKER01", "LOKER02", "LOKER03"]:
                s = suhu.get('suhu01' if loker=='LOKER01' else 'suhu02' if loker=='LOKER02' else 'suhu03')
                sheet_stok.update_cell(i, col_suhu, f"{s} °C")
                
        st.session_state.last_sync = time.time()
    except: pass

# ==========================================
# 4. STYLING UI (GLASSMORPHISM)
# ==========================================
st.markdown("""<style>
    .stApp { background: linear-gradient(180deg, #0f0b0b 0%, #120707 60%); color: #E6EDF3; font-family: 'Plus Jakarta Sans', sans-serif; }
    .glass { background: rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.04); border-radius:14px; padding:18px; }
    .massive-title { font-size: 3.2rem; font-weight:800; color: #FFD27D; }
    .status-aktif { color: #50FA7B; font-weight: 800; font-size: 2.2rem; }
    </style>""", unsafe_allow_html=True)

st.markdown('<p class="massive-title">Smart Locker OS</p>', unsafe_allow_html=True)

# Panel Indikator Suhu Real-time
t1, t2, t3 = st.columns(3)
with t1: st.markdown(f'<div class="glass"><div>SUHU LOKER 01</div><div class="status-aktif">🌡️ {suhu["suhu01"]} °C</div></div>', unsafe_allow_html=True)
with t2: st.markdown(f'<div class="glass"><div>SUHU LOKER 02</div><div class="status-aktif">🌡️ {suhu["suhu02"]} °C</div></div>', unsafe_allow_html=True)
with t3: st.markdown(f'<div class="glass"><div>SUHU LOKER 03</div><div class="status-aktif">🌡️ {suhu["suhu03"]} °C</div></div>', unsafe_allow_html=True)

# ==========================================
# 5. KONTEN UTAMA (TELEMETRY LOGS & AI CHAT)
# ==========================================
df = load_data()
if not df.empty:
    col_chart, col_table = st.columns([1, 1.4])
    with col_table:
        st.markdown('<div class="glass"><h4>Telemetry Logs</h4>', unsafe_allow_html=True)
        st.dataframe(df.tail(8), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# Integrasi AI Support Agent
if "chat_history" not in st.session_state: 
    st.session_state.chat_history = []
    
with st.form("ai_form"):
    user_input = st.text_area("AI Input", placeholder="Tanyakan seputar status lab atau loker...")
    submit = st.form_submit_button("Kirim")
    
if submit and user_input:
    st.session_state.chat_history.append(("user", user_input))
    # Integrasi prompt AI dan pengiriman ke API Gemini diletakkan di sini