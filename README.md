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
Treinar o modelo
bash
Copiar
Editar
python train_model.py
Isso irá gerar o arquivo modelo_bueiros.pkl automaticamente após o treino com dados simulados.

3. Iniciar a API Flask
bash
Copiar
Editar
python app.py
Você verá algo como:

csharp
Copiar
Editar
* Running on http://192.168.0.X:5000
4. Rodar o ESP32 no Wokwi
Acesse https://wokwi.com

Crie um projeto e importe os arquivos da pasta wokwi_esp32_code/

No código, altere a linha:

cpp
Copiar
Editar
const char* serverUrl = "http://192.168.0.X:5000/dados_bueiro";
Rode o simulador — os dados começarão a aparecer no Flask 🎯

5. Enviar manualmente do Webhook (opcional)
Caso você tenha feito testes com Webhook.site:

Copie o JSON completo recebido

Cole dentro do script reenviar_para_flask.py

Rode:

bash
Copiar
Editar
python reenviar_para_flask.py
6. Verificar dados no banco
bash
Copiar
Editar
python verificar_banco.py
Saída esperada:

yaml
Copiar
Editar
Total de leituras armazenadas: 12
### 📌 Requisitos

- Python 3.9+
- Git instalado
- VS Code (recomendado)
- Flask, scikit-learn, joblib, pandas

### 📦 Instale as dependências

```bash
pip install flask joblib scikit-learn pandas


