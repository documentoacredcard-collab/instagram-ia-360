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


@app.route("/perfis-nicho")
def perfis_nicho():
    """Lista os perfis rastreados e a analise de pertencimento ao nicho."""
    return jsonify(storage.ler("perfis_nicho", {}))


@app.route("/leads")
def leads():
    """Lista os contatos do Direct com a qualificacao gerada pela IA."""
    conversas = storage.ler("conversas", {})
    resultado = []
    for igsid, dados in conversas.items():
        resultado.append({
            "igsid": igsid,
            "perfil": dados.get("perfil", {}),
            "qualificacao": dados.get("qualificacao"),
        })
    return jsonify(resultado)


@app.route("/painel")
def painel():
    """Painel visual simples com leads, perfis do nicho e comentarios."""
    conversas = storage.ler("conversas", {})
    perfis_nicho_dados = storage.ler("perfis_nicho", {})
    comentarios_dados = storage.ler("comentarios", {})

    linhas_leads = ""
    for dados in conversas.values():
        perfil = dados.get("perfil", {})
        qualificacao = dados.get("qualificacao") or {}
        linhas_leads += (
            "<tr><td>@%s</td><td>%s</td><td>%s</td><td>%s</td></tr>"
        ) % (
            perfil.get("username", ""),
            perfil.get("name", ""),
            qualificacao.get("classificacao", ""),
            qualificacao.get("resumo", ""),
        )
    if not linhas_leads:
        linhas_leads = "<tr><td colspan='4'>Nenhum contato ainda.</td></tr>"

    linhas_nicho = ""
    for dados in perfis_nicho_dados.values():
        perfil = dados.get("perfil", {})
        analise = dados.get("analise") or {}
        linhas_nicho += (
            "<tr><td>@%s</td><td>%s</td><td>%s</td><td>%s</td></tr>"
        ) % (
            perfil.get("username", ""),
            "Sim" if analise.get("pertence_ao_nicho") else "Nao",
            analise.get("categoria", ""),
            analise.get("observacao", ""),
        )
    if not linhas_nicho:
        linhas_nicho = "<tr><td colspan='4'>Nenhum perfil rastreado ainda.</td></tr>"

    linhas_comentarios = ""
    for dados in comentarios_dados.values():
        if dados.get("excluido"):
            status = "Excluido (negativo)"
        else:
            status = "Respondido"
        linhas_comentarios += (
            "<tr><td>@%s</td><td>%s</td><td>%s</td><td>%s</td></tr>"
        ) % (
            dados.get("username", ""),
            dados.get("texto", ""),
            status,
            dados.get("motivo", ""),
        )
    if not linhas_comentarios:
        linhas_comentarios = "<tr><td colspan='4'>Nenhum comentario processado ainda.</td></tr>"

    html = """
    <html>
      <head>
        <title>Painel - Instagram IA 360</title>
        <meta charset="utf-8">
        <style>
          body { font-family: Arial, sans-serif; max-width: 1000px; margin: 30px auto; padding: 0 16px; }
          h1 { margin-bottom: 4px; }
          h2 { margin-top: 40px; border-bottom: 2px solid #eee; padding-bottom: 6px; }
          table { width: 100%%; border-collapse: collapse; margin-top: 10px; }
          th, td { border: 1px solid #ddd; padding: 8px; text-align: left; font-size: 14px; }
          th { background: #f5f5f5; }
          tr:nth-child(even) { background: #fafafa; }
        </style>
      </head>
      <body>
        <h1>Instagram IA 360</h1>
        <p>Painel de acompanhamento do sistema.</p>

        <h2>Leads (contatos do Direct)</h2>
        <table>
          <tr><th>Perfil</th><th>Nome</th><th>Classificacao</th><th>Resumo</th></tr>
          %s
        </table>

        <h2>Perfis do nicho</h2>
        <table>
          <tr><th>Perfil</th><th>Pertence ao nicho</th><th>Categoria</th><th>Observacao</th></tr>
          %s
        </table>

        <h2>Comentarios processados</h2>
        <table>
          <tr><th>Perfil</th><th>Comentario</th><th>Status</th><th>Motivo</th></tr>
          %s
        </table>
      </body>
    </html>
    """ % (linhas_leads, linhas_nicho, linhas_comentarios)

    return html, 200


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
        for change in entrada.get("changes", []):
            if change.get("field") == "comments":
                processar_comentario(change.get("value", {}))

    return jsonify({"status": "ok"}), 200


def registrar_perfil_nicho(perfil_id, perfil, texto, negocio):
    """Analisa e registra um perfil que interagiu, para o rastreador de nicho."""
    if not perfil_id:
        return
    perfis = storage.ler("perfis_nicho", {})
    if perfil_id in perfis:
        return
    analise = ai_responder.analisar_perfil_nicho(perfil, texto, negocio)
    perfis[perfil_id] = {
        "perfil": perfil,
        "analise": analise,
    }
    storage.gravar("perfis_nicho", perfis)


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
    contato_novo = igsid not in conversas
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
        "qualificacao": conversas.get(igsid, {}).get("qualificacao"),
    }

    # qualifica o contato na primeira mensagem dele
    if contato_novo:
        conversas[igsid]["qualificacao"] = ai_responder.qualificar_perfil(
            perfil, texto_recebido, negocio
        )

    storage.gravar("conversas", conversas)

    # rastreia o perfil para o radar de nicho
    registrar_perfil_nicho(igsid, perfil, texto_recebido, negocio)


def processar_comentario(valor):
    comment_id = valor.get("id")
    texto = valor.get("text")
    autor = valor.get("from", {})
    username = autor.get("username")

    # ignora comentarios sem texto, sem autor ou feitos pela propria conta
    if not comment_id or not texto or not username:
        return

    # evita responder de novo a um comentario ja tratado
    comentarios = storage.ler("comentarios", {})
    if comment_id in comentarios:
        return

    # exclui comentarios negativos/ofensivos automaticamente
    analise_sentimento = ai_responder.comentario_e_negativo(texto)
    if analise_sentimento.get("negativo"):
        ig_client.delete_comment(comment_id)
        comentarios[comment_id] = {
            "username": username,
            "texto": texto,
            "negativo": True,
            "motivo": analise_sentimento.get("motivo", ""),
            "excluido": True,
        }
        registrar_historico(comentarios)
        return

    negocio = get_config()
    resposta = ai_responder.gerar_resposta_comentario(username, texto, negocio)
    ig_client.send_private_reply(comment_id, resposta)

    comentarios[comment_id] = {
        "username": username,
        "texto": texto,
        "negativo": False,
        "motivo": analise_sentimento.get("motivo", ""),
        "excluido": False,
        "resposta_privada": resposta,
    }
    registrar_historico(comentarios)

    # rastreia o perfil para o radar de nicho
    perfil_id = autor.get("id")
    perfil = {"id": perfil_id, "username": username}
    registrar_perfil_nicho(perfil_id, perfil, texto, negocio)


def registrar_historico(comentarios):
    """Salva o dict de comentarios, mantendo apenas os 500 mais recentes."""
    if len(comentarios) > 500:
        for chave in list(comentarios.keys())[:-500]:
            del comentarios[chave]
    storage.gravar("comentarios", comentarios)


if __name__ == "__main__":
    porta = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=porta, debug=True)
