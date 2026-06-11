# -*- coding: utf-8 -*-
"""
Armazenamento simples em arquivos JSON (sem banco de dados).
Cada "chave" vira um arquivo <chave>.json dentro de DATA_DIR.
"""
import os
import json
import threading

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = "/data" if os.path.isdir("/data") else os.path.join(BASE, "data")
os.makedirs(DATA_DIR, exist_ok=True)

LOCK = threading.Lock()


def ler(chave, padrao):
    """Le um valor (dict/list) pela chave. Retorna padrao se nao existir."""
    caminho = os.path.join(DATA_DIR, chave + ".json")
    if not os.path.exists(caminho):
        return padrao
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return padrao


def gravar(chave, valor):
    """Grava um valor (dict/list) na chave."""
    with LOCK:
        caminho = os.path.join(DATA_DIR, chave + ".json")
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(valor, f, ensure_ascii=False, indent=2)
