import serial
import requests

SERIAL_PORT = "COM10"
BAUD_RATE = 9600
API_URL = "http://127.0.0.1:8000/kiosk/api/rfid/"

ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)

print("RFID listener running...")

while True:
    line = ser.readline().decode(errors="ignore").strip()

    if line.startswith("UID:"):
        uid = line.replace("UID:", "").strip()
        print("Scanned UID:", uid)

        try:
            res = requests.post(API_URL, json={"uid": uid})
            print("Server:", res.json())
        except Exception as e:
            print("API error:", e)