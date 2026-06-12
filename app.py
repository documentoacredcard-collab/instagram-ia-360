# -*- coding: utf-8 -*-
"""
INSTAGRAM IA 360
Sistema separado e independente (sem ligacao com o RADAR EMPRESARIAL 360).

Funcionalidade atual (Prioridade #1):
- Responder mensagens do Direct do Instagram automaticamente,
  com resposta personalizada gerada por IA (Claude).
"""
import os
from flask import Flask, request, jsonify

import storage
import ig_client
import ai_responder

app = Flask(__name__)

VERIFY_TOKEN = os.environ.get("IG_VERIFY_TOKEN", "").strip()


# ---------------- Configuracao do negocio ----------------
NEGOCIO_PADRAO = {
    "nome": "",
    "nicho": "",
    "tom": "amigavel e profissional",
    "oferta": "",
}


def get_config():
    return storage.ler("config", NEGOCIO_PADRAO)


# ---------------- Rotas basicas ----------------
@app.route("/")
def home():
    return jsonify({"status": "online", "sistema": "INSTAGRAM IA 360"})


@app.route("/privacy")
def privacy():
    return """
    <html>
      <head><title>Politica de Privacidade - Radar IA 360</title></head>
      <body style="font-family: Arial, sans-serif; max-width: 700px; margin: 40px auto; line-height: 1.6;">
        <h1>Politica de Privacidade</h1>
        <p>Este aplicativo (Radar IA 360) usa a API do Instagram para responder
        automaticamente mensagens recebidas no Direct da conta comercial conectada.</p>
        <p>As mensagens trocadas sao usadas exclusivamente para gerar respostas
        automaticas e nao sao compartilhadas com terceiros.</p>
        <p>Para solicitar a exclusao dos seus dados, entre em contato pelo email
        radarempresarial360@gmail.com.</p>
      </body>
    </html>
    """, 200


@app.route("/config", methods=["GET", "POST"])
def config():
    if request.method == "GET":
        return jsonify(get_config())

    dados = request.get_json(force=True, silent=True) or {}
    atual = get_config()
    for campo in ("nome", "nicho", "tom", "oferta"):
        if campo in dados:
            atual[campo] = dados[campo]
    storage.gravar("config", atual)
    return jsonify(atual)


# ---------------- Webhook do Instagram ----------------
@app.route("/webhook", methods=["GET"])
def verificar_webhook():
    modo = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if modo == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Token invalido", 403


@app.route("/webhook", methods=["POST"])
def receber_webhook():
    dados = request.get_json(force=True, silent=True) or {}

    for entrada in dados.get("entry", []):
        for evento in entrada.get("messaging", []):
            processar_mensagem(evento)

    return jsonify({"status": "ok"}), 200


def processar_mensagem(evento):
    mensagem = evento.get("message", {})

    # ignora mensagens enviadas pelo proprio negocio (eco) e mensagens sem texto
    if mensagem.get("is_echo"):
        return
    texto_recebido = mensagem.get("text")
    if not texto_recebido:
        return

    igsid = evento.get("sender", {}).get("id")
    if not igsid:
        return

    # busca historico da conversa
    conversas = storage.ler("conversas", {})
    historico = conversas.get(igsid, {}).get("historico", [])

    # busca perfil de quem mandou a mensagem
    perfil = ig_client.get_user_profile(igsid)

    # gera resposta personalizada com IA
    negocio = get_config()
    resposta = ai_responder.gerar_resposta(perfil, texto_recebido, historico, negocio)

    # envia resposta pelo Direct
    ig_client.send_message(igsid, resposta)

    # salva no historico
    historico.append({"de": "cliente", "texto": texto_recebido})
    historico.append({"de": "negocio", "texto": resposta})
    conversas[igsid] = {
        "perfil": perfil,
        "historico": historico,
    }
    storage.gravar("conversas", conversas)


if __name__ == "__main__":
    porta = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=porta, debug=True)
