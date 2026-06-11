# INSTAGRAM IA 360

Sistema separado e independente de automacao para Instagram (sem nenhuma ligacao
com o RADAR EMPRESARIAL 360). Usa a API oficial da Meta (Instagram Messaging API).

## Funcionalidade atual

- **Responder DMs com mensagem personalizada (IA)**: quando alguem manda mensagem
  no Direct, o sistema busca o perfil de quem mandou, monta um historico da
  conversa e usa o Claude (Anthropic) para gerar uma resposta personalizada,
  enviando de volta automaticamente.

## Funcionalidades futuras (planejadas)

- Responder comentarios de Reels/Feed levando para o Direct
- Qualificador de perfil de novos contatos
- Rastreador de perfis do nicho
- Exclusao automatica de comentarios negativos

## Configuracao

1. Crie um app no [Meta for Developers](https://developers.facebook.com/) com o
   produto "Instagram" (Instagram Messaging API), vinculado a uma conta
   Instagram Business/Creator.
2. Configure o webhook apontando para `https://SEU-DOMINIO/webhook`,
   inscrevendo o campo `messages`.
3. Copie `.env.example` para `.env` e preencha:
   - `IG_ACCESS_TOKEN`: token de acesso da pagina/conta do Instagram
   - `IG_VERIFY_TOKEN`: token que voce escolhe para validar o webhook
   - `ANTHROPIC_API_KEY`: chave da API do Claude
4. Configure o negocio (nome, nicho, tom de voz, oferta) via `POST /config`,
   para a IA personalizar as respostas.

## Rodando localmente

```bash
pip install -r requirements.txt
python app.py
```

## Deploy

Pronto para Railway (Procfile + railway.json + runtime.txt).
