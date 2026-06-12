# -*- coding: utf-8 -*-
"""
Geracao de respostas personalizadas com IA (Claude) para o Direct do Instagram.
"""
import os
import json
from anthropic import Anthropic

client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", "").strip())

MODEL = "claude-opus-4-8"


def gerar_resposta(perfil, mensagem, historico, negocio):
    """
    Gera uma resposta personalizada para o Direct.

    perfil: dict com dados do perfil de quem mandou a mensagem (name, username)
    mensagem: texto recebido agora
    historico: lista de mensagens anteriores da conversa [{"de": "cliente"/"negocio", "texto": ...}]
    negocio: dict com dados do negocio que esta respondendo (nome, nicho, tom, oferta)
    """
    nome = perfil.get("name") or perfil.get("username") or "amigo(a)"
    username = perfil.get("username", "")

    contexto_negocio = (
        "Voce e o assistente de atendimento do Instagram do negocio '%s'.\n"
        "Nicho: %s\n"
        "Tom de voz: %s\n"
        "Oferta/Objetivo principal: %s\n"
    ) % (
        negocio.get("nome", ""),
        negocio.get("nicho", ""),
        negocio.get("tom", "amigavel e profissional"),
        negocio.get("oferta", ""),
    )

    historico_txt = ""
    for h in historico[-10:]:
        quem = "Cliente" if h.get("de") == "cliente" else "Voce"
        historico_txt += "%s: %s\n" % (quem, h.get("texto", ""))

    prompt = (
        "%s\n"
        "Voce esta respondendo uma mensagem direta no Instagram de @%s (nome: %s).\n\n"
        "Historico recente da conversa:\n%s\n"
        "Nova mensagem recebida: \"%s\"\n\n"
        "Escreva uma resposta curta, natural e personalizada para o Direct do Instagram, "
        "usando o nome da pessoa quando fizer sentido. Nao use markdown, nao assine, "
        "responda como se fosse uma conversa real de WhatsApp/Instagram."
    ) % (contexto_negocio, username, nome, historico_txt, mensagem)

    resposta = client.messages.create(
        model=MODEL,
        max_tokens=512,
        thinking={"type": "adaptive"},
        output_config={"effort": "low"},
        messages=[{"role": "user", "content": prompt}],
    )

    texto_final = ""
    for bloco in resposta.content:
        if bloco.type == "text":
            texto_final += bloco.text

    return texto_final.strip()


def qualificar_perfil(perfil, mensagem, negocio):
    """
    Analisa a primeira mensagem de um novo contato e classifica o perfil
    em relacao ao negocio, para ajudar a priorizar leads.

    Retorna um dict: {"classificacao": ..., "interesse": ..., "resumo": ...}
    classificacao: "lead_qualificado", "curioso" ou "sem_interesse"
    """
    nome = perfil.get("name") or perfil.get("username") or "amigo(a)"
    username = perfil.get("username", "")

    contexto_negocio = (
        "Negocio: %s\n"
        "Nicho: %s\n"
        "Oferta/Objetivo principal: %s\n"
    ) % (
        negocio.get("nome", ""),
        negocio.get("nicho", ""),
        negocio.get("oferta", ""),
    )

    prompt = (
        "%s\n"
        "Um novo contato (@%s, nome: %s) acabou de mandar a primeira mensagem "
        "no Direct: \"%s\"\n\n"
        "Classifique esse contato em relacao a oferta do negocio. "
        "Responda APENAS com um JSON no formato:\n"
        '{"classificacao": "lead_qualificado" | "curioso" | "sem_interesse", '
        '"interesse": "breve descricao do que a pessoa parece querer", '
        '"resumo": "uma frase curta sobre o contato"}'
    ) % (contexto_negocio, username, nome, mensagem)

    resposta = client.messages.create(
        model=MODEL,
        max_tokens=300,
        thinking={"type": "adaptive"},
        output_config={"effort": "low"},
        messages=[{"role": "user", "content": prompt}],
    )

    texto_final = ""
    for bloco in resposta.content:
        if bloco.type == "text":
            texto_final += bloco.text

    try:
        inicio = texto_final.index("{")
        fim = texto_final.rindex("}") + 1
        return json.loads(texto_final[inicio:fim])
    except Exception:
        return {
            "classificacao": "curioso",
            "interesse": "",
            "resumo": texto_final.strip(),
        }


def gerar_resposta_comentario(username, comentario, negocio):
    """
    Gera uma resposta privada (enviada para o Direct) em reacao a um
    comentario publico, convidando a pessoa para continuar a conversa.

    username: quem comentou
    comentario: texto do comentario
    negocio: dict com dados do negocio (nome, nicho, tom, oferta)
    """
    contexto_negocio = (
        "Voce e o assistente de atendimento do Instagram do negocio '%s'.\n"
        "Nicho: %s\n"
        "Tom de voz: %s\n"
        "Oferta/Objetivo principal: %s\n"
    ) % (
        negocio.get("nome", ""),
        negocio.get("nicho", ""),
        negocio.get("tom", "amigavel e profissional"),
        negocio.get("oferta", ""),
    )

    prompt = (
        "%s\n"
        "A pessoa @%s comentou no seu post/Reels: \"%s\"\n\n"
        "Escreva uma mensagem curta e calorosa para enviar no Direct dela, "
        "agradecendo o comentario e abrindo conversa para continuar por ali "
        "(sem ser insistente). Nao use markdown, nao assine, responda como "
        "se fosse uma conversa real de WhatsApp/Instagram."
    ) % (contexto_negocio, username, comentario)

    resposta = client.messages.create(
        model=MODEL,
        max_tokens=512,
        thinking={"type": "adaptive"},
        output_config={"effort": "low"},
        messages=[{"role": "user", "content": prompt}],
    )

    texto_final = ""
    for bloco in resposta.content:
        if bloco.type == "text":
            texto_final += bloco.text

    return texto_final.strip()
