# -*- coding: utf-8 -*-
"""
Cliente da API oficial do Instagram (Meta Graph API / Instagram Messaging).
Responsavel por: buscar perfil de quem mandou mensagem e enviar respostas.
"""
import os
import requests

GRAPH_VERSION = "v21.0"
GRAPH_URL = "https://graph.instagram.com/%s" % GRAPH_VERSION

ACCESS_TOKEN = os.environ.get("IG_ACCESS_TOKEN", "").strip()


def get_user_profile(igsid):
    """Busca nome e username de quem enviou a mensagem (pelo IGSID)."""
    url = "%s/%s" % (GRAPH_URL, igsid)
    params = {
        "fields": "name,username",
        "access_token": ACCESS_TOKEN,
    }
    try:
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print("[ig_client] erro ao buscar perfil:", e)
        return {}


def send_message(igsid, texto):
    """Envia uma mensagem de texto para o usuario via Instagram Send API."""
    url = "%s/me/messages" % GRAPH_URL
    payload = {
        "recipient": {"id": igsid},
        "message": {"text": texto},
    }
    params = {"access_token": ACCESS_TOKEN}
    try:
        resp = requests.post(url, params=params, json=payload, timeout=15)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print("[ig_client] erro ao enviar mensagem:", e)
        return {}


def delete_comment(comment_id):
    """Exclui um comentario (usado para comentarios negativos/ofensivos)."""
    url = "%s/%s" % (GRAPH_URL, comment_id)
    params = {"access_token": ACCESS_TOKEN}
    try:
        resp = requests.delete(url, params=params, timeout=15)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print("[ig_client] erro ao excluir comentario:", e)
        return {}


def send_private_reply(comment_id, texto):
    """Envia uma resposta privada (Direct) em reacao a um comentario."""
    url = "%s/me/messages" % GRAPH_URL
    payload = {
        "recipient": {"comment_id": comment_id},
        "message": {"text": texto},
    }
    params = {"access_token": ACCESS_TOKEN}
    try:
        resp = requests.post(url, params=params, json=payload, timeout=15)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print("[ig_client] erro ao enviar resposta privada de comentario:", e)
        return {}
