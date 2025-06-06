# 🌧️ Sistema inteligente de monitoramento de enchentes  
**Global Solution FIAP 2025.1 — Turma de Inteligência Artificial**

---

## 🧠 Sobre o projeto

Este projeto foi desenvolvido para monitorar o nível de obstrução de bueiros e prever o risco de entupimento com **dados reais simulados**.  
Ele integra:

- Um **ESP32 com sensor** (simulado no Wokwi)
- Um **servidor Flask** local
- Um modelo de **Machine Learning (Random Forest)**
- Um banco de dados **SQLite**
  
A solução tem como objetivo **emitir alertas e prever entupimentos**, contribuindo com a **prevenção de enchentes** em áreas urbanas.

---

## 🧰 Tecnologias utilizadas

| Tecnologia           | Função                                        |
|----------------------|-----------------------------------------------|
| ESP32 (Wokwi)        | Simula o sensor físico de distância           |
| Python + Flask       | API local que recebe os dados via HTTP POST  |
| SQLite               | Armazena os dados recebidos                   |
| Scikit-learn         | Treinamento do modelo de predição             |
| Webhook.site (teste) | Inspeção de envio de dados durante o dev      |

---

## 🚀 Como Rodar o Projeto

### 📌 Requisitos

- Python 3.9+
- Git instalado
- VS Code (recomendado)
- Flask, scikit-learn, joblib, pandas

### 📦 Instale as dependências

```bash
pip install flask joblib scikit-learn pandas
```
### 🧠 Treine o modelo
Execute no terminal:

python train_model.py

Isso irá treinar um modelo de Machine Learning com base nas leituras armazenadas no banco e salvar o arquivo modelo_bueiros.pkl.

### 🔥 Inicie a API Flask
No terminal:

python app.py

A API Flask será iniciada em http://192.168.0.X:5000 e ficará aguardando dados do ESP32.

### ⚙️ Teste com o ESP32 no Wokwi
Acesse https://wokwi.com

Importe os arquivos da pasta wokwi_esp32_code/

No código, edite a variável serverUrl com seu IP local, por exemplo:

const char* serverUrl = "http://192.168.0.3:5000/dados_bueiro";

Rode a simulação. O ESP32 irá enviar os dados automaticamente para o Flask, que salvará no banco e exibirá os alertas.

### 🧪 Ferramentas auxiliares

reenviar_para_flask.py → reenvia uma leitura salva do Webhook.site para o Flask

verificar_banco.py → exibe quantas leituras estão armazenadas

geracao_de_dados.py → gera dados simulados para treinar o modelo

### 👨‍💻 Desenvolvedores
Enrico RM561352
Larissa RM566418
Daniel   RM564440
Ednilton RM566069
Davi RM566336

