import sqlite3
import datetime
import random

DATABASE_FILE = 'bueiros_data.db'
MAC = '24:0A:C4:00:01:10'

conn = sqlite3.connect(DATABASE_FILE)
cursor = conn.cursor()

for i in range(20):
    timestamp = (datetime.datetime.now() - datetime.timedelta(minutes=i*10)).strftime("%Y-%m-%d %H:%M:%S")
    espaco = random.randint(5, 90)
    bateria = random.randint(40, 100)
    rssi = random.randint(-90, -50)
    status = "NORMAL"
    if espaco <= 20:
        status = "CRITICO"
    elif espaco <= 40:
        status = "ALERTA"

    cursor.execute('''
        INSERT INTO leituras (dispositivo_mac, timestamp, espaco_livre_percent, status_reportado, bateria_percent, rssi)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (MAC, timestamp, espaco, status, bateria, rssi))

conn.commit()
conn.close()

print("Leituras simuladas inseridas com sucesso.")
