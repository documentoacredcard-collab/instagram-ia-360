# -*- coding: utf-8 -*-
"""
Geracao de imagens para os criativos do Instagram, usando a API da OpenAI (DALL-E 3).
"""
import os
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "").strip())


def gerar_imagem(descricao):
    """
    Gera uma imagem a partir da descricao visual do criativo.

    descricao: texto descrevendo a imagem/cena desejada para o post
    Retorna a URL da imagem gerada, ou None em caso de erro.
    """
    if not descricao:
        return None

    prompt = (
        "Imagem para post de Instagram, estilo fotografico profissional, "
        "sem texto sobreposto: %s"
    ) % descricao

    try:
        resposta = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        return resposta.data[0].url
    except Exception as e:
        print("[image_gen] erro ao gerar imagem:", e)
        return None
