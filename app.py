# Importa o Flask, a ferramenta para criar o servidor web
from flask import Flask, request, jsonify

# Cria a aplicação Flask
app = Flask(__name__)


# Define a rota (URL) do webhook. Só aceita requisições do tipo POST.
@app.route("/webhook", methods=["POST"])
def receber_mensagem():
    # Pega os dados JSON que o WhatsApp ou iFood enviarão
    dados = request.get_json()

    # Imprime os dados no terminal para a gente poder ver o que chegou
    print("=============================================")
    print("DADOS RECEBIDOS:")
    print(dados)
    print("=============================================")

    # Responde à plataforma que a mensagem foi recebida com sucesso
    return jsonify({"status": "sucesso"}), 200


# Linha que faz o servidor rodar quando executamos o arquivo python app.py
if __name__ == "__main__":
    # O host='0.0.0.0' é importante para o Render funcionar
    app.run(host="0.0.0.0", port=5000)
