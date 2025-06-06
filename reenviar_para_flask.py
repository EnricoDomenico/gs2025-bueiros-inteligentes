# reenviar_para_flask.py
import requests
import time

# Troque aqui pelo seu endpoint real do Flask
flask_url = "http://192.168.0.3:5000/dados_bueiro"

# JSON exemplo vindo do webhook.site
dados_simulados = {
    "dispositivo": "24:0A:C4:00:01:10",
    "espaco_livre_percent": 33,
    "status_reportado": "CRITICO",
    "bateria": 85,
    "rssi": -71
}

while True:
    print("Reenviando dados ao Flask...")
    r = requests.post(flask_url, json=dados_simulados)
    print(f"Resposta do Flask: {r.status_code} - {r.text}")
    time.sleep(30)  # Simula ciclo do ESP
