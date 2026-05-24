# 📦 Integrated Smart Locker OS
![Project Status](https://img.shields.io/badge/Status-Active-success?style=for-the-badge)
![Hardware](https://img.shields.io/badge/Hardware-ESP32%20%7C%20MG996R%20%7C%20DHT22-blue?style=for-the-badge)
![Software](https://img.shields.io/badge/Software-MicroPython%20%7C%20Streamlit%20%7C%20Telegram%20Bot-yellow?style=for-the-badge)
![Integration](https://img.shields.io/badge/Integration-MQTT%20%7C%20Google%20Sheets%20%7C%20Gemini%20AI-orange?style=for-the-badge)

<div align="center">
  <img src="https://via.placeholder.com/1000x400/1a1a1a/ffffff?text=Smart+Locker+OS+Integrated+System+Banner" alt="Smart Locker OS Banner" width="100%">
</div>

<br>

## 📖 Tentang Proyek
**Integrated Smart Locker OS** adalah sebuah ekosistem solusi total (*end-to-end IoT solution*) untuk pengelolaan loker penyimpanan cerdas mandiri (*self-service*). Proyek ini menggabungkan arsitektur *Operational Technology* (OT) berupa kendali perangkat keras kelistrikan dengan kekuatan *Information Technology* (IT) berupa dasbor analitik web, robot interaktif Telegram, otomatisasi basis data awan (*cloud database*), dan kecerdasan buatan (AI).

Sistem ini dirancang tidak hanya untuk mengamankan aset fisik, tetapi juga untuk menyajikan telemetri lingkungan yang andal dan antarmuka pengguna yang sangat interaktif, menjadikannya sebuah contoh nyata dari penerapan **IT/OT Cyber-Physical System Integration**.

### ✨ Nilai Utama Sistem (Core Values)
1. **Safety Factor & Power Isolation:** Pemisahan mutlak secara kelistrikan antara jalur sinyal digital mikrokontroler dengan jalur daya motor penggerak berkebutuhan arus tinggi menggunakan teknik *Common Ground* terpusat pada PSU 5V/10A untuk mencegah kegagalan sistem (*brownout reset*).
2. **Data Streaming & Silent Telemetry:** Pengiriman parameter suhu internal dari 3 kompartemen loker (DHT22) berjalan secara asinkron menggunakan protokol MQTT di latar belakang, tanpa mengganggu performa respons antarmuka lokal maupun server web.
3. **Data Synchronization & Intelligent Support:** Alur peminjaman divalidasi langsung secara dua arah ke Google Sheets dengan fitur pembuatan struk tiket digital berupa *QR Code*, didukung oleh Google Gemini AI sebagai agen pintar pelayan lab.

---

## 💻 Arsitektur Perangkat Lunak (Software Architecture)

Sistem perangkat lunak terbagi menjadi tiga komponen utama yang saling berkolaborasi melalui jaringan:

### 1. Telemetry Subscriber Test (`CeksuhuMQTT.py`)
Skrip Python ringan yang berjalan di sisi komputer klien lokal untuk memastikan lalu lintas data MQTT dari perangkat keras *edge* mengalir dengan lancar tanpa ada paket data yang hilang.
* **Mekanisme Kerja:** Melakukan *subscribing* ke topik broker publik dengan perlindungan penanganan *error* otomatis (*try-except*) untuk mendeteksi versi pustaka `paho-mqtt` yang terinstal.

### 2. Command Center Dasbor Web (`dashboard.py`)
Aplikasi web berbasis framework Streamlit yang berfungsi sebagai pusat kendali (*Control Room Dashboard*) bagi operator laboratorium atau admin loker.
* **Mekanisme Kerja:** Menampilkan data telemetri MQTT dalam visualisasi UI bernuansa *Glassmorphism Modern*, melakukan sinkronisasi data suhu ke Google Sheets setiap 60 detik, serta memuat riwayat *Telemetry Logs* peminjaman alat.

### 3. Automated Ticketing & AI Bot (`bot_telegram.py`)
Antarmuka pengguna akhir (*end-user interface*) berbentuk Bot Telegram interaktif yang melayani seluruh proses administrasi peminjaman alat laboratorium secara mandiri.
* **Mekanisme Kerja:** Memandu pengguna mengisi formulir, memotong stok barang secara otomatis di Google Sheets, memancarkan struk digital dalam bentuk gambar *QR Code* instan, serta berdiskusi ramah menggunakan kecerdasan buatan Google Gemini AI.

---

## 🚀 Panduan Instalasi & Penerapan (Deployment Guide)

Ikuti langkah-langkah di bawah ini untuk menjalankan seluruh ekosistem perangkat lunak di komputer/server Anda:

### 📥 1. Prasyarat Sistem
Pastikan komputer Anda sudah terinstal **Python 3.9 atau versi di atasnya**, serta memiliki akses internet untuk terhubung ke broker MQTT publik dan API Google Cloud.

### ⚙️ 2. Unduh File Kode & Instalasi Pustaka
Seluruh file kode Python (`CeksuhuMQTT.py`, `dashboard.py`, dan `bot_telegram.py`) sudah tersedia **di bagian atas halaman repositori ini**. 
Silakan unduh file-file tersebut dan letakkan di dalam satu folder khusus di komputer Anda.

Buka terminal/command prompt, arahkan ke folder tersebut, lalu instal seluruh library Python yang
