# -*- coding: utf-8 -*-
"""
INSTAGRAM IA 360
Sistema separado e independente (sem ligacao com o RADAR EMPRESARIAL 360).

Funcionalidade atual (Prioridade #1):
- Responder mensagens do Direct do Instagram automaticamente,
  com resposta personalizada gerada por IA (Claude).
"""
import os
import json
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
    """Painel visual com indicadores e graficos: leads, perfis do nicho e comentarios."""
    conversas = storage.ler("conversas", {})
    perfis_nicho_dados = storage.ler("perfis_nicho", {})
    comentarios_dados = storage.ler("comentarios", {})

    # ---- indicadores (KPIs) ----
    total_leads = len(conversas)
    contagem_classificacao = {"lead_qualificado": 0, "curioso": 0, "sem_interesse": 0}
    for dados in conversas.values():
        classificacao = (dados.get("qualificacao") or {}).get("classificacao")
        if classificacao in contagem_classificacao:
            contagem_classificacao[classificacao] += 1

    total_perfis_nicho = len(perfis_nicho_dados)
    perfis_no_nicho = sum(
        1 for d in perfis_nicho_dados.values()
        if (d.get("analise") or {}).get("pertence_ao_nicho")
    )

    total_comentarios = len(comentarios_dados)
    comentarios_excluidos = sum(1 for d in comentarios_dados.values() if d.get("excluido"))
    comentarios_respondidos = total_comentarios - comentarios_excluidos

    # ---- linhas das tabelas ----
    linhas_leads = ""
    for dados in conversas.values():
        perfil = dados.get("perfil", {})
        qualificacao = dados.get("qualificacao") or {}
        linhas_leads += (
            "<tr><td>@%s</td><td>%s</td><td><span class='badge badge-%s'>%s</span></td><td>%s</td></tr>"
        ) % (
            perfil.get("username", ""),
            perfil.get("name", ""),
            qualificacao.get("classificacao", ""),
            qualificacao.get("classificacao", "-"),
            qualificacao.get("resumo", ""),
        )
    if not linhas_leads:
        linhas_leads = "<tr><td colspan='4' class='vazio'>Nenhum contato ainda.</td></tr>"

    linhas_nicho = ""
    for dados in perfis_nicho_dados.values():
        perfil = dados.get("perfil", {})
        analise = dados.get("analise") or {}
        pertence = analise.get("pertence_ao_nicho")
        linhas_nicho += (
            "<tr><td>@%s</td><td><span class='badge badge-%s'>%s</span></td><td>%s</td><td>%s</td></tr>"
        ) % (
            perfil.get("username", ""),
            "sim" if pertence else "nao",
            "Sim" if pertence else "Nao",
            analise.get("categoria", ""),
            analise.get("observacao", ""),
        )
    if not linhas_nicho:
        linhas_nicho = "<tr><td colspan='4' class='vazio'>Nenhum perfil rastreado ainda.</td></tr>"

    linhas_comentarios = ""
    for dados in comentarios_dados.values():
        if dados.get("excluido"):
            status_classe = "excluido"
            status_texto = "Excluido (negativo)"
        else:
            status_classe = "respondido"
            status_texto = "Respondido"
        linhas_comentarios += (
            "<tr><td>@%s</td><td>%s</td><td><span class='badge badge-%s'>%s</span></td><td>%s</td></tr>"
        ) % (
            dados.get("username", ""),
            dados.get("texto", ""),
            status_classe,
            status_texto,
            dados.get("motivo", ""),
        )
    if not linhas_comentarios:
        linhas_comentarios = "<tr><td colspan='4' class='vazio'>Nenhum comentario processado ainda.</td></tr>"

    dados_grafico = {
        "classificacao": contagem_classificacao,
        "nicho": {"no_nicho": perfis_no_nicho, "fora_nicho": total_perfis_nicho - perfis_no_nicho},
        "comentarios": {"respondidos": comentarios_respondidos, "excluidos": comentarios_excluidos},
    }

    html = """
    <html>
      <head>
        <title>Painel - Instagram IA 360</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
          * { box-sizing: border-box; }
          body {
            font-family: 'Segoe UI', Arial, sans-serif;
            max-width: 1100px;
            margin: 0 auto;
            padding: 24px 16px 60px;
            background: #0a0a12;
            background-image:
              radial-gradient(circle at 15%% 0%%, rgba(99,102,241,0.20), transparent 40%%),
              radial-gradient(circle at 85%% 15%%, rgba(236,72,153,0.18), transparent 40%%),
              radial-gradient(circle at 50%% 100%%, rgba(34,211,238,0.12), transparent 45%%);
            color: #e5e7eb;
          }
          header h1 {
            margin: 0;
            font-size: 30px;
            font-weight: 800;
            background: linear-gradient(135deg, #818cf8, #f472b6, #22d3ee);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
            display: inline-block;
          }
          header p { color: #9ca3af; margin-top: 4px; }

          .kpis {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 16px;
            margin: 24px 0;
          }
          .kpi {
            border-radius: 16px;
            padding: 20px 22px;
            box-shadow: 0 8px 24px -8px rgba(0,0,0,0.6);
            color: #fff;
          }
          .kpi .valor { font-size: 32px; font-weight: 800; }
          .kpi .label { color: rgba(255,255,255,0.85); font-size: 13px; margin-top: 4px; font-weight: 500; }
          .kpi.azul { background: linear-gradient(135deg, #818cf8, #4f46e5); }
          .kpi.verde { background: linear-gradient(135deg, #34d399, #059669); }
          .kpi.roxo { background: linear-gradient(135deg, #e879f9, #a21caf); }
          .kpi.vermelho { background: linear-gradient(135deg, #fb7185, #be123c); }

          .graficos {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
            gap: 16px;
            margin-bottom: 32px;
          }
          .card {
            background: #15151f;
            border: 1px solid #2a2a3a;
            border-radius: 16px;
            padding: 16px;
            box-shadow: 0 8px 24px -12px rgba(99,102,241,0.35);
          }
          .card h3 { margin: 0 0 12px; font-size: 15px; color: #c4b5fd; font-weight: 700; }
          .card canvas { max-height: 220px; }

          section h2 {
            font-size: 18px;
            margin: 32px 0 12px;
            color: #e5e7eb;
            font-weight: 700;
          }
          table {
            width: 100%%;
            border-collapse: collapse;
            background: #15151f;
            border: 1px solid #2a2a3a;
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 8px 24px -12px rgba(99,102,241,0.25);
          }
          th, td { padding: 10px 12px; text-align: left; font-size: 13px; border-bottom: 1px solid #232333; color: #e5e7eb; }
          th { background: #1c1c2b; color: #a5b4fc; font-weight: 700; text-transform: uppercase; font-size: 11px; letter-spacing: 0.04em; }
          tr:last-child td { border-bottom: none; }
          tr:hover td { background: #1c1c2b; }
          td.vazio { text-align: center; color: #6b7280; padding: 18px; }

          .badge {
            display: inline-block;
            padding: 3px 12px;
            border-radius: 999px;
            font-size: 12px;
            font-weight: 700;
          }
          .badge-lead_qualificado { background: linear-gradient(135deg, #34d399, #059669); color: #ecfdf5; }
          .badge-curioso { background: linear-gradient(135deg, #fbbf24, #d97706); color: #1c1306; }
          .badge-sem_interesse { background: linear-gradient(135deg, #fb7185, #be123c); color: #fff1f2; }
          .badge-sim { background: linear-gradient(135deg, #34d399, #059669); color: #ecfdf5; }
          .badge-nao { background: #2a2a3a; color: #9ca3af; }
          .badge-respondido { background: linear-gradient(135deg, #818cf8, #4f46e5); color: #eef2ff; }
          .badge-excluido { background: linear-gradient(135deg, #fb7185, #be123c); color: #fff1f2; }
        </style>
      </head>
      <body>
        <header>
          <h1>Instagram IA 360</h1>
          <p>Painel de acompanhamento em tempo real.</p>
        </header>

        <div class="kpis">
          <div class="kpi azul"><div class="valor">%s</div><div class="label">Contatos no Direct</div></div>
          <div class="kpi verde"><div class="valor">%s</div><div class="label">Leads qualificados</div></div>
          <div class="kpi roxo"><div class="valor">%s</div><div class="label">Perfis do nicho rastreados</div></div>
          <div class="kpi vermelho"><div class="valor">%s</div><div class="label">Comentarios excluidos</div></div>
        </div>

        <div class="graficos">
          <div class="card">
            <h3>Classificacao dos leads</h3>
            <canvas id="graficoLeads"></canvas>
          </div>
          <div class="card">
            <h3>Perfis dentro do nicho</h3>
            <canvas id="graficoNicho"></canvas>
          </div>
          <div class="card">
            <h3>Comentarios: respondidos x excluidos</h3>
            <canvas id="graficoComentarios"></canvas>
          </div>
        </div>

        <section>
          <h2>Leads (contatos do Direct)</h2>
          <table>
            <tr><th>Perfil</th><th>Nome</th><th>Classificacao</th><th>Resumo</th></tr>
            %s
          </table>
        </section>

        <section>
          <h2>Perfis do nicho</h2>
          <table>
            <tr><th>Perfil</th><th>Pertence ao nicho</th><th>Categoria</th><th>Observacao</th></tr>
            %s
          </table>
        </section>

        <section>
          <h2>Comentarios processados</h2>
          <table>
            <tr><th>Perfil</th><th>Comentario</th><th>Status</th><th>Motivo</th></tr>
            %s
          </table>
        </section>

        <script>
          const dados = %s;

          new Chart(document.getElementById('graficoLeads'), {
            type: 'doughnut',
            data: {
              labels: ['Lead qualificado', 'Curioso', 'Sem interesse'],
              datasets: [{
                data: [
                  dados.classificacao.lead_qualificado,
                  dados.classificacao.curioso,
                  dados.classificacao.sem_interesse
                ],
                backgroundColor: ['#34d399', '#fbbf24', '#fb7185'],
                borderWidth: 0
              }]
            },
            options: { plugins: { legend: { position: 'bottom', labels: { color: '#c4b5fd' } } } }
          });

          new Chart(document.getElementById('graficoNicho'), {
            type: 'doughnut',
            data: {
              labels: ['Dentro do nicho', 'Fora do nicho'],
              datasets: [{
                data: [dados.nicho.no_nicho, dados.nicho.fora_nicho],
                backgroundColor: ['#e879f9', '#3f3f5f'],
                borderWidth: 0
              }]
            },
            options: { plugins: { legend: { position: 'bottom', labels: { color: '#c4b5fd' } } } }
          });

          new Chart(document.getElementById('graficoComentarios'), {
            type: 'bar',
            data: {
              labels: ['Comentarios'],
              datasets: [
                { label: 'Respondidos', data: [dados.comentarios.respondidos], backgroundColor: '#818cf8', borderRadius: 8 },
                { label: 'Excluidos', data: [dados.comentarios.excluidos], backgroundColor: '#fb7185', borderRadius: 8 }
              ]
            },
            options: { plugins: { legend: { position: 'bottom', labels: { color: '#c4b5fd' } } }, scales: { y: { beginAtZero: true, ticks: { precision: 0 } } } }
          });
        </script>
      </body>
    </html>
    """ % (
        total_leads,
        contagem_classificacao["lead_qualificado"],
        total_perfis_nicho,
        comentarios_excluidos,
        linhas_leads,
        linhas_nicho,
        linhas_comentarios,
        json.dumps(dados_grafico),
    )

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
