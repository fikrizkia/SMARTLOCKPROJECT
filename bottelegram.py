import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import gspread
import os
import requests
import io
import qrcode
from datetime import datetime
from dotenv import load_dotenv
import re

# ==========================================
# 1. KONFIGURASI KREDENSIAL & ENVIRONMENT
# ==========================================
# Muat variabel environment dari file .env (Pastikan file .env masuk ke .gitignore)
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")              # Masukkan Token Bot Telegram Anda di file .env
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")    # Masukkan ID Google Sheets Anda di file .env
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")    # Masukkan API Key Google Gemini Anda di file .env

bot = telebot.TeleBot(BOT_TOKEN)
user_session = {}

# Koneksi ke Google Sheets API
# Ganti 'kunci.json' dengan path/nama file kredensial Service Account Google Cloud Anda
gc = gspread.service_account(filename='kunci.json')
sh = gc.open_by_key(SPREADSHEET_ID)

# Inisialisasi Worksheet (Pastikan urutan sheet pada dokumen Anda sesuai)
sheet_log = sh.get_worksheet(0)  # Sheet index 0: Log/Riwayat peminjaman alat
sheet_stok = sh.get_worksheet(1) # Sheet index 1: Database ketersediaan alat dan status suhu

# ==========================================
# 2. FUNGSI UTAMA & VALIDASI DATA
# ==========================================
def get_stok_map():
    data = sheet_stok.get_all_records()
    stok_map = {}
    for item in data:
        # Menambahkan fallback 'SUHU' agar tidak error jika kolom kosong
        stok_map[str(item['ID LOKER']).upper()] = {
            "nama": item['NAMA ALAT'], 
            "tersedia": int(item['STOK TERSEDIA']),
            "suhu": str(item.get('SUHU', 'Tidak ada sensor suhu'))
        }
    return stok_map

def valid_wa(phone: str) -> bool:
    digits = re.sub(r'\D', '', phone)
    return 9 <= len(digits) <= 15

def normalisasi_wa(phone: str) -> str:
    digits = re.sub(r'\D', '', phone)
    if digits.startswith('0'): 
        return '+62' + digits[1:]
    return '+' + digits

def generate_qr(data_text):
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data_text)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf

# ==========================================
# 3. COMMAND HANDLER: /START
# ==========================================
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("🎒 Pinjam Alat", callback_data="ALUR_PINJAM"),
        InlineKeyboardButton("🔍 Cek Ketersediaan Alat", callback_data="MENU_STATUS")
    )
    bot.send_message(message.chat.id, "Selamat datang di Smart Locker OS. Pilih menu administrasi:", reply_markup=markup)

# ==========================================
# 4. CALLBACK HANDLER: CEK STOK
# ==========================================
@bot.callback_query_handler(func=lambda call: call.data == "MENU_STATUS")
def cek_stok(call):
    bot.answer_callback_query(call.id)
    stok_map = get_stok_map()
    text = "📊 Status Stok Smart Locker:\n"
    for loker, info in stok_map.items():
        text += f"- {loker} ({info['nama']}): {info['tersedia']} unit (Suhu Aktual: {info['suhu']})\n"
    bot.send_message(call.message.chat.id, text)

# ==========================================
# 5. ALUR PEMINJAMAN MANDIRI (SELF-SERVICE)
# ==========================================
@bot.callback_query_handler(func=lambda call: call.data == "ALUR_PINJAM")
def mulai_peminjaman(call):
    bot.answer_callback_query(call.id)
    user_session[call.message.chat.id] = {"aksi": "PINJAM"}
    msg = bot.send_message(call.message.chat.id, "📝 Masukkan Nama Lengkap Anda:")
    bot.register_next_step_handler(msg, input_nama)

def input_nama(m):
    user_session[m.chat.id]["nama"] = m.text
    msg = bot.send_message(m.chat.id, "🆔 Masukkan NIM/ID Identitas Anda:")
    bot.register_next_step_handler(msg, input_nim)

def input_nim(m):
    user_session[m.chat.id]["nim"] = m.text
    msg = bot.send_message(m.chat.id, "📱 Masukkan Nomor WhatsApp Aktif:")
    bot.register_next_step_handler(msg, input_wa)

def input_wa(m):
    if not valid_wa(m.text):
        msg = bot.send_message(m.chat.id, "❌ Nomor WhatsApp tidak valid. Silakan ulangi:")
        bot.register_next_step_handler(msg, input_wa)
        return
    user_session[m.chat.id]["wa"] = normalisasi_wa(m.text)
    msg = bot.send_message(m.chat.id, "✉️ Masukkan Alamat Email:")
    bot.register_next_step_handler(msg, input_email)

def input_email(m):
    user_session[m.chat.id]["email"] = m.text
    stok = get_stok_map()
    info = "\n".join([f"- {k} ({v['nama']}): {v['tersedia']} unit" for k, v in stok.items()])
    msg = bot.send_message(m.chat.id, f"📦 Stok Alat Tersedia:\n{info}\n\nKetik ID LOKER yang ingin dipinjam (contoh: LOKER01):")
    bot.register_next_step_handler(msg, input_loker)

def input_loker(m):
    loker = m.text.upper().strip()
    stok_map = get_stok_map()
    if loker not in stok_map or stok_map[loker]['tersedia'] <= 0:
        bot.reply_to(m, "❌ ID Loker tidak ditemukan atau stok habis. Silakan ketik /start untuk mengulang.")
        user_session.pop(m.chat.id, None)
        return
    user_session[m.chat.id]["loker"] = loker
    user_session[m.chat.id]["alat"] = stok_map[loker]['nama']
    user_session[m.chat.id]["suhu_alat"] = stok_map[loker]['suhu']
    msg = bot.send_message(m.chat.id, "⏱️ Masukkan durasi peminjaman (contoh: 2 jam):")
    bot.register_next_step_handler(msg, finalize_pinjam)

def finalize_pinjam(m):
    user = user_session[m.chat.id]
    waktu = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    durasi = m.text
    
    # Menambahkan data ke log Google Sheets
    # Format: [WAKTU, ID LOKER, NAMA ALAT, DURASI, STATUS, SUHU, NAMA, NIM, NOMOR TELEPON, EMAIL]
    sheet_log.append_row([
        waktu, user['loker'], user['alat'], durasi, "🔴 Dipinjam", 
        user['suhu_alat'], user['nama'], user['nim'], user['wa'], user['email']
    ])
    
    # Mengurangi stok di database Google Sheets
    data = sheet_stok.get_all_records()
    for idx, row in enumerate(data, start=2):
        if str(row['ID LOKER']).upper() == user['loker']:
            sheet_stok.update_cell(idx, 4, max(int(row['STOK TERSEDIA']) - 1, 0))
            break
            
    # Mengirimkan Struk Digital berupa QR Code
    qr_data = f"Peminjaman: {user['alat']} | Loker: {user['loker']} | Nama: {user['nama']} | Waktu: {waktu}"
    bot.send_photo(m.chat.id, generate_qr(qr_data), caption=f"✅ Peminjaman Berhasil Dicatat!\n\nSilakan tunjukkan QR Code digital ini kepada petugas lab sebagai bukti peminjaman sah.")
    user_session.pop(m.chat.id, None)

# ==========================================
# 6. INTEGRASI AI INTELLIGENCE (GOOGLE GEMINI)
# ==========================================
@bot.message_handler(func=lambda message: True)
def jawab_ai(message):
    # Keyword trigger untuk agen AI
    if any(k in message.text.lower() for k in ["tanya", "apa", "berapa", "stok", "suhu"]):
        stok = str(get_stok_map())
        prompt = f"Data lab saat ini: {stok}. Jawab pertanyaan pengguna berikut: {message.text}. Jawab dengan ramah dan informatif. PENTING: DILARANG KERAS menggunakan format markdown (seperti tanda bintang ** untuk tebal atau miring), jawab dengan teks polos saja agar mudah dibaca di Telegram."
        
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
            res = requests.post(url, json={"contents": [{"parts":[{"text": prompt}]}]})
            bot.reply_to(message, res.json()['candidates'][0]['content']['parts'][0]['text'])
        except Exception as e: 
            bot.reply_to(message, "⚠️ Mohon maaf, agen AI sedang sibuk atau batas akses API telah tercapai. Silakan coba beberapa saat lagi.")
    else:
        bot.reply_to(message, "Halo! Saya adalah sistem Smart Locker OS. Gunakan perintah /start untuk memulai menu peminjaman.")

# ==========================================
# EKSEKUSI UTAMA
# ==========================================
if __name__ == "__main__":
    print("🤖 Sistem Telemetry & Bot Smart Locker Berjalan...")
    bot.polling(none_stop=True)