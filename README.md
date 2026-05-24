# 📦 Integrated Smart Locker OS
![Project Status](https://img.shields.io/badge/Status-Active-success?style=for-the-badge)
![Hardware](https://img.shields.io/badge/Hardware-ESP32%20%7C%20MG996R%20%7C%20DHT22-blue?style=for-the-badge)
![Software](https://img.shields.io/badge/Software-MicroPython%20%7C%20Streamlit%20%7C%20Telegram%20Bot-yellow?style=for-the-badge)
![Integration](https://img.shields.io/badge/Integration-MQTT%20%7C%20Google%20Sheets%20%7C%20Gemini%20AI-orange?style=for-the-badge)


<br>

## 📖 Tentang Proyek
**Integrated Smart Locker OS** adalah sebuah ekosistem solusi total (*end-to-end IoT solution*) untuk pengelolaan loker penyimpanan cerdas mandiri (*self-service*). Proyek ini menggabungkan arsitektur *Operational Technology* (OT) berupa kendali perangkat keras kelistrikan dengan kekuatan *Information Technology* (IT) berupa dasbor analitik web, robot interaktif Telegram, otomatisasi basis data awan (*cloud database*), dan kecerdasan buatan (AI).

Sistem ini dirancang tidak hanya untuk mengamankan aset fisik, tetapi juga untuk menyajikan telemetri lingkungan yang andal dan antarmuka pengguna yang sangat interaktif, menjadikannya sebuah contoh nyata dari penerapan **IT/OT Cyber-Physical System Integration**.

### ✨ Nilai Utama Sistem (Core Values)
1. **Safety Factor & Power Isolation (OT Standar):** Pemisahan mutlak secara kelistrikan antara jalur sinyal digital mikrokontroler dengan jalur daya motor penggerak berkebutuhan arus tinggi (Servo MG996R) menggunakan teknik *Common Ground* terpusat pada PSU 5V/10A untuk mencegah kegagalan sistem (*brownout reset*).
2. **Data Streaming & Silent Telemetry:** Pengiriman parameter suhu internal dari 3 kompartemen loker (DHT22) berjalan secara asinkron menggunakan protokol MQTT di latar belakang, tanpa mengganggu performa respons antarmuka lokal maupun server web.
3. **Analytical Storytelling in Engineering Drafting:** Seluruh visual rute kabel, penempatan komponen mekanik, dan pembuatan ruang rahasia panel belakang (*False Back routing*) didokumentasikan secara presisi lewat standar gambar teknik AutoCAD Electrical.
4. **Data Synchronization & Intelligent Support (IT Standar):** Alur peminjaman divalidasi langsung secara dua arah ke Google Sheets dengan fitur pembuatan struk tiket digital berupa *QR Code*, didukung oleh Google Gemini AI sebagai agen pintar pelayan lab.

---

## 📐 Arsitektur Perangkat Keras (Hardware Blueprints)

Seluruh rancangan cetak biru kelistrikan dan mekanik terbagi ke dalam dokumen teknik resmi (PDF) yang dapat diakses pada folder repositori:

* 📄 **[MAIN PANEL WIRING](./MAIN%20PANEL%20WIRING.pdf)** - Dokumentasi distribusi catu daya utama industri (PSU 5V DC 10A) menuju terminal pembagi tegangan dan pusat *Common Ground* sistem ESP32.
* 📄 **[TAMPAK DEPAN](./TAMPAKDEPAN.pdf)** - Desain tata letak antarmuka luar pintu lemari, mencakup pemotongan (*cutout*) presisi untuk LCD I2C 20x4 dan unit *Barcode Scanner*.
* 📄 **[WIRING TAMPAK BELAKANG](./WIRINGTAMPAKBELAKANG.pdf)** - Blueprint jalur kabel pita (*ribbon cable*) berstruktur matriks dari *Keypad 4x4* dan penempatan modul *Relay* saklar kelistrikan.
* 📄 **[WIRING LOKER 01-03](./WIRINGLOKER01-03.pdf)** - Dokumentasi metode *Typical Detail View* yang menggambarkan tata letak internal sensor suhu DHT22 dan pergerakan lengan kunci motor Servo di dalam setiap loker.

### 🖧 Alokasi Pin Mikrokontroler (ESP32 Pinout)

| Komponen Elektronik | Pin ESP32 | Jenis Sinyal | Aturan Warna Gambar Kelistrikan |
| :--- | :---: | :--- | :--- |
| **LCD I2C 20x4** | 21 (SDA), 22 (SCL) | I2C Data & Clock | Kabel Biru (SDA) & Kabel Putih (SCL) |
| **Servo Loker 1, 2, 3** | 13, 14, 15 | PWM Output | Kabel Oranye / Kuning |
| **DHT22 Loker 1, 2, 3** | 4, 5, 18 | Digital Input | Kabel Hijau |
| **Modul Relay** | 12 | Digital Output | Kabel Ungu / Abu-abu |
| **Keypad Matriks 4x4** | *19, 23, 25, 26 (Row)*<br>*27, 32, 33, 2 (Col)* | Digital I/O Matrix | Jalur Garis Kabel Pita Abu-abu |

---

## 💻 Arsitektur Perangkat Lunak (Software Architecture)

Sistem perangkat lunak terbagi menjadi tiga komponen utama yang saling berkolaborasi melalui jaringan:

### 1. Telemetry Subscriber Test (`CeksuhuMQTT.py`)
Skrip Python ringan yang berjalan di sisi komputer klien lokal untuk memastikan lalu lintas data MQTT dari perangkat keras *edge* mengalir dengan lancar tanpa ada paket data yang hilang.
* **Mekanisme Kerja:** Melakukan *subscribing* ke topik broker publik dengan perlindungan penanganan *error* otomatis (*try-except*) untuk mendeteksi versi pustaka `paho-mqtt` yang terinstal (v1 atau v2) serta pembuatan *Client ID* acak demi menghindari pemutusan koneksi sepihak oleh broker.

### 2. Command Center Dasbor Web (`dashboard.py`)
Aplikasi web berbasis framework Streamlit yang berfungsi sebagai pusat kendali (*Control Room Dashboard*) bagi operator laboratorium atau admin loker.
* **Mekanisme Kerja:** Secara berkala membaca data telemetri MQTT multi-topik dari ketiga loker sekaligus, menampilkannya dalam visualisasi UI bernuansa *Glassmorphism Modern*, melakukan sinkronisasi data suhu langsung ke kolom baris Google Sheets setiap 60 detik, serta memuat riwayat *Telemetry Logs* peminjaman alat.

### 3. Automated Ticketing & AI Bot (`bot_telegram.py`)
Antarmuka pengguna akhir (*end-user interface*) berbentuk Bot Telegram interaktif yang melayani seluruh proses administrasi peminjaman alat laboratorium secara mandiri.
* **Mekanisme Kerja:** Memandu pengguna mengisi formulir (Nama, NIM, WA, Email), memvalidasi ketersediaan unit alat di dalam database Google Sheets, memotong stok barang secara otomatis jika peminjaman sukses, memperbarui parameter suhu aktual loker, memancarkan struk digital dalam bentuk gambar *QR Code* instan, serta berdiskusi ramah menggunakan kecerdasan buatan Google Gemini AI (dengan proteksi *plain-text response* tanpa markdown yang mengganggu).

---

## 🚀 Panduan Instalasi & Penerapan (Deployment Guide)

Ikuti langkah-langkah di bawah ini untuk menjalankan seluruh ekosistem perangkat lunak di komputer/server Anda:

### 📥 1. Prasyarat Sistem
Pastikan komputer Anda sudah terinstal **Python 3.9 atau versi di atasnya**, serta memiliki akses internet untuk terhubung ke broker MQTT publik dan API Google Cloud.

### ⚙️ 2. Kloning Repositori & Instalasi Pustaka
Buka terminal/command prompt, lalu jalankan perintah berikut secara berurutan:
```bash
# Clone repository ini
git clone (https://github.com/fikrizkia/ELECTRICAL/blob/main/bottelegram.py)(https://github.com/fikrizkia/ELECTRICAL/blob/main/dashboard.py)
# Instal seluruh library Python yang dibutuhkan
pip install paho-mqtt streamlit pandas gspread plotly python-dotenv streamlit-autorefresh pyTelegramBotAPI qrcode[pil] requests
