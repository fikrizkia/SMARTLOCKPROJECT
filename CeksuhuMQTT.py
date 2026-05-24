import paho.mqtt.client as mqtt
import random

def on_connect(client, userdata, flags, *args):
    print("✅ BERHASIL TERHUBUNG KE BROKER!")
    # Ganti 'nama_pengguna' dengan username atau identifier unik Anda
    client.subscribe("nama_pengguna/smartlock/suhu01")
    print("📡 Menunggu data suhu dari Wokwi...")

def on_message(client, userdata, msg):
    suhu = msg.payload.decode("utf-8")
    print(f"📥 BINGO! Data Masuk -> Suhu: {suhu} °C")

try:
    # Kompatibilitas untuk paho-mqtt versi 2.x
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=f"Tes_{random.randint(1,999)}")
except AttributeError:
    # Kompatibilitas untuk paho-mqtt versi 1.x
    client = mqtt.Client(client_id=f"Tes_{random.randint(1,999)}")

client.on_connect = on_connect
client.on_message = on_message

print("⏳ Menghubungi broker.emqx.io...")
try:
    # broker.emqx.io adalah broker publik gratis. Sesuaikan jika menggunakan broker privat.
    client.connect("broker.emqx.io", 1883, 60)
    client.loop_forever()
except Exception as e:
    print(f"❌ Gagal koneksi jaringan: {e}")
