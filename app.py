import os
from flask import Flask, request, jsonify
from google.cloud import dialogflow_v2 as dialogflow


app = Flask(__name__)

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "HorizontIA.json"


DIALOGFLOW_PROJECT_ID = "horizontia-ggrs"  # Troque pelo ID do seu projeto
DIALOGFLOW_LANGUAGE_CODE = "pt-BR"


# --- FUNÇÃO DE INTELIGÊNCIA (ATUALIZADA) ---
def detectar_intent_do_texto(texto, session_id):
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(DIALOGFLOW_PROJECT_ID, session_id)
    text_input = dialogflow.types.TextInput(
        text=texto, language_code=DIALOGFLOW_LANGUAGE_CODE
    )
    query_input = dialogflow.types.QueryInput(text=text_input)

    try:
        response = session_client.detect_intent(
            session=session, query_input=query_input
        )

        # Pega o resultado da consulta
        query_result = response.query_result

        # Verifica se a IA entendeu ou não
        # 'Default Fallback Intent' é o nome da intenção "não entendi" do Dialogflow
        if query_result.intent.display_name == "Default Fallback Intent":
            # Se não entendeu, anota a pergunta em um arquivo
            with open("perguntas_nao_entendidas.txt", "a", encoding="utf-8") as f:
                f.write(texto + "\n")

        return query_result.fulfillment_text

    except Exception as e:
        print("Erro no Dialogflow:", e)
        return "Desculpe, tive um problema para processar sua pergunta. Pode repetir?"


# ... (o resto do seu código, como a função detectar_intent_do_texto, fica igual) ...

# SENHA SECRETA PARA O WHATSAPP (VOCÊ PODE MUDAR)
VERIFY_TOKEN = "161410Jv!"


# --- ROTA DO WEBHOOK (ATUALIZADA) ---
@app.route("/webhook", methods=["GET", "POST"])
def receber_mensagem():
    # Lógica para a verificação inicial do WhatsApp
    if request.method == "GET":
        if (
            request.args.get("hub.mode") == "subscribe"
            and request.args.get("hub.verify_token") == VERIFY_TOKEN
        ):
            print("Webhook verificado com sucesso!")
            return request.args.get("hub.challenge"), 200
        else:
            return "Verification token mismatch", 403

    # Lógica para receber mensagens normais (POST)
    if request.method == "POST":
        dados = request.get_json()

        # TODO: Adaptar para extrair a mensagem do formato complexo do WhatsApp/iFood
        # Por enquanto, vamos manter o formato simples do Postman para teste
        texto_recebido = dados.get("mensagem", "")
        id_cliente = dados.get("cliente", "default_user")

        resposta_da_ia = detectar_intent_do_texto(texto_recebido, id_cliente)

        print("=============================================")
        print(f"Cliente ({id_cliente}) disse: {texto_recebido}")
        print(f"IA respondeu: {resposta_da_ia}")
        print("=============================================")

        # TODO: Enviar a resposta de volta para a API do WhatsApp
        return jsonify({"status": "sucesso", "resposta_da_ia": resposta_da_ia})


# ... (o if __name__ == '__main__': ... continua igual) ...


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
