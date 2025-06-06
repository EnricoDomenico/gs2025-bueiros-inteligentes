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

## 🗂️ Estrutura do projeto
ProjetoGs/
├── wokwi_esp32_code/
│ ├── bueiro_sensor.ino # Código principal do ESP32
│ ├── sketch.ino # Alias ou cópia do principal
│ ├── diagram.json # Diagrama de ligação dos pinos
│ └── wokwi-project.txt # Metadados do projeto no Wokwi
│
├── app.py # API Flask que recebe e trata os dados
├── bueiros_data.db # Banco de dados SQLite
├── modelo_bueiros.pkl # Modelo treinado de Machine Learning
│
├── train_model.py # Script de treino do modelo
├── gerar_dados.py # Gera leituras simuladas (com seed)
├── reenviar_para_flask.py # Reenvia payload do webhook para API Flask
├── verificar_banco.py # Conta entradas no banco SQLite
├── teste.py # Código de testes pontuais
└── desktop.ini / pycache/ # Arquivos de sistema (ignorar)


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


