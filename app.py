# app.py
from flask import Flask, request, jsonify
import sqlite3
import datetime
import os
import joblib
import warnings

app = Flask(__name__)
DATABASE_FILE = 'bueiros_data.db'
warnings.filterwarnings("ignore")

# ✅ Carrega o modelo ML se estiver disponível
modelo_ml = None
try:
    modelo_ml = joblib.load('modelo_bueiros.pkl')
    print("✅ Modelo ML carregado com sucesso.")
except Exception as e:
    print(f"⚠️ Erro ao carregar o modelo ML: {e}")

def init_db():
    if not os.path.exists(DATABASE_FILE):
        print("Criando banco de dados...")
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS leituras (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dispositivo_mac TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                espaco_livre_percent INTEGER,
                status_reportado TEXT,
                bateria_percent INTEGER,
                rssi INTEGER,
                FOREIGN KEY (dispositivo_mac) REFERENCES dispositivos (mac_address)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dispositivos (
                mac_address TEXT PRIMARY KEY,
                localizacao_descricao TEXT,
                latitude REAL,
                longitude REAL,
                data_instalacao DATE,
                data_ultima_limpeza DATE,
                observacoes TEXT
            )
        ''')
        conn.commit()
        conn.close()
        print("Banco de dados criado.")
    else:
        print(f"Banco de dados '{DATABASE_FILE}' já existe.")

init_db()

@app.route('/dados_bueiro', methods=['POST'])
def receber_dados_bueiro():
    try:
        data = request.get_json()
        print(f"Dados recebidos: {data}")

        mac_address = data.get('dispositivo')
        espaco_livre = data.get('espaco_livre_percent')
        status_reportado = data.get('status_reportado')
        bateria = data.get('bateria')
        rssi = data.get('rssi', None)

        if not mac_address:
            return jsonify({"status": "erro", "mensagem": "MAC address (dispositivo) não fornecido"}), 400
        if espaco_livre is None:
            return jsonify({"status": "erro", "mensagem": "'espaco_livre_percent' não fornecido"}), 400

        timestamp_atual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()

        cursor.execute("SELECT mac_address FROM dispositivos WHERE mac_address = ?", (mac_address,))
        if not cursor.fetchone():
            cursor.execute(
                "INSERT INTO dispositivos (mac_address, data_instalacao, observacoes) VALUES (?, ?, ?)",
                (mac_address, datetime.date.today(), "Dispositivo registrado automaticamente via POST")
            )
            print(f"Novo dispositivo {mac_address} registrado.")

        cursor.execute('''
            INSERT INTO leituras (dispositivo_mac, timestamp, espaco_livre_percent, status_reportado, bateria_percent, rssi)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (mac_address, timestamp_atual, espaco_livre, status_reportado, bateria, rssi))

        conn.commit()
        conn.close()

        if status_reportado == "CRITICO":
            print(f"🚨 ALERTA IMEDIATO: Bueiro {mac_address} em estado CRÍTICO ({espaco_livre}% livre)!")
        elif status_reportado == "ALERTA":
            print(f"⚠️ ATENÇÃO: Bueiro {mac_address} em estado de ALERTA ({espaco_livre}% livre).")

        # ✅ Predição do modelo se estiver carregado
        if modelo_ml:
            try:
                features_input = [[
                    espaco_livre,
                    bateria,
                    0,  # delta_espaco_livre
                    espaco_livre  # proxy para média móvel
                ]]
                pred = modelo_ml.predict(features_input)
                if pred[0] == 1:
                    print(f"🔮 PREDIÇÃO ML: Bueiro {mac_address} tem ALTO RISCO de entupimento em breve!")
            except Exception as e:
                print(f"Erro na predição ML: {e}")

        return jsonify({"status": "sucesso", "mensagem": "Dados recebidos e processados"}), 200

    except Exception as e:
        print(f"Erro ao processar dados: {e}")
        return jsonify({"status": "erro", "mensagem": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
