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


# --- ROTA DO WEBHOOK (Sem alterações, mas a lógica acima a afeta) ---
@app.route("/webhook", methods=["POST"])
def receber_mensagem():
    dados = request.get_json()

    texto_recebido = dados.get("mensagem", "")
    id_cliente = dados.get("cliente", "default_user")

    resposta_da_ia = detectar_intent_do_texto(texto_recebido, id_cliente)

    print("=============================================")
    print(f"Cliente ({id_cliente}) disse: {texto_recebido}")
    print(f"IA respondeu: {resposta_da_ia}")
    print("=============================================")

    return jsonify({"resposta_da_ia": resposta_da_ia})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
