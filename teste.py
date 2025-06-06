from flask import Flask

# Cria o servidor
app = Flask(__name__)

# Cria uma única página inicial ("/") que responde a qualquer um
@app.route("/")
def hello():
    # Imprime uma mensagem no terminal para sabermos que a conexão chegou
    print(">>> CONEXÃO RECEBIDA! O TESTE FUNCIONOU!")
    # Responde ao navegador com uma mensagem
    return "<h1>O Servidor de Teste está no ar!</h1>"

# Garante que o servidor rode na rede e na porta 5000
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)