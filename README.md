# INSTAGRAM IA 360

Sistema separado e independente de automacao para Instagram (sem nenhuma ligacao
com o RADAR EMPRESARIAL 360). Usa a API oficial da Meta (Instagram Messaging API).

## Funcionalidades

- **Responder DMs com mensagem personalizada (IA)**: quando alguem manda mensagem
  no Direct, o sistema busca o perfil de quem mandou, monta um historico da
  conversa e usa o Claude (Anthropic) para gerar uma resposta personalizada,
  enviando de volta automaticamente.
- **Comentarios -> Direct**: quando alguem comenta em um post/Reels, o sistema
  envia uma resposta privada personalizada (IA) no Direct, convidando para
  continuar a conversa por la.
- **Qualificador de perfil de novos contatos**: na primeira mensagem de um
  contato novo, a IA classifica o perfil (lead_qualificado, curioso,
  sem_interesse) e o resultado pode ser consultado em `/leads`.
- **Rastreador de perfis do nicho**: cada perfil que interage (DM ou
  comentario) e analisado pela IA para indicar se pertence ao
  nicho/publico-alvo do negocio, consultavel em `/perfis-nicho`.
- **Exclusao automatica de comentarios negativos**: comentarios ofensivos,
  com discurso de odio, assedio, spam ou que depreciem o negocio (ex:
  "porcaria", "golpe") sao identificados pela IA e excluidos automaticamente.
- **Painel visual** (`/painel`): tela simples com leads, perfis do nicho e
  comentarios processados (respondidos ou excluidos).
- **Criativos** (`/criativos`): tela para gerar posts completos para o
  Instagram (legenda, hashtags, ideia visual e a imagem gerada por IA) a
  partir de um tema.

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
   - `OPENAI_API_KEY`: chave da API da OpenAI, usada para gerar as imagens
     dos criativos (DALL-E 3)
4. Configure o negocio (nome, nicho, tom de voz, oferta) via `POST /config`,
   para a IA personalizar as respostas.

## Rodando localmente

```bash
pip install -r requirements.txt
python app.py
```

## Deploy

Pronto para Railway (Procfile + railway.json + runtime.txt).
