# 📋 HISTÓRICO DO SISTEMA — INSTAGRAM IA 360

> Documento de referência do sistema: arquitetura, configurações e histórico de mudanças.
> Última atualização: **11/06/2026** *(sessão: painel visual, remoção de emojis e aba de criativos com imagem por IA)*

---

## 🎯 O QUE É
**Instagram IA 360** — sistema separado e independente (sem nenhuma ligação com o RADAR EMPRESARIAL 360), de automação para Instagram via API oficial da Meta (Instagram Messaging API).

---

## 🏗️ ARQUITETURA / INFRAESTRUTURA

| Componente | Detalhe |
|-----------|---------|
| **App principal** | Flask (Python) + gunicorn |
| **Hospedagem** | Railway — `https://web-production-5e454.up.railway.app` |
| **Repositório** | GitHub `documentoacredcard-collab/instagram-ia-360` |
| **Armazenamento** | `storage.py` (JSON em arquivo, chave/valor) — **efêmero no Railway** (sem volume; `data/` no `.gitignore`) |
| **IA de texto** | Anthropic Claude (`claude-opus-4-8`, thinking adaptive, effort low) |
| **IA de imagem** | OpenAI DALL-E 3 (`image_gen.py`) — requer `OPENAI_API_KEY` |

### Deploy
- `git push` no `main` → GitHub webhook → build/deploy automático no Railway.
- Build costuma demorar de 6 a 15+ minutos.

---

## 🌐 FUNCIONALIDADES

- **Webhook do Instagram** (`/webhook`): recebe mensagens do Direct e comentários.
- **Resposta automática no Direct** (IA, sem emojis, tom humano e natural).
- **Comentários → Direct**: responde no privado quem comenta nos posts/Reels.
- **Qualificador de leads** (`/leads`): classifica novos contatos (lead_qualificado, curioso, sem_interesse).
- **Rastreador de perfis do nicho** (`/perfis-nicho`): indica se quem interagiu pertence ao público-alvo.
- **Exclusão automática de comentários negativos** (ofensivos, spam, "porcaria", "golpe" etc.).
- **Painel visual** (`/painel`): KPIs + gráficos (Chart.js) de leads, perfis do nicho e comentários.
- **Criativos** (`/criativos`): gera post completo a partir de um tema — legenda (sem emojis), hashtags, ideia visual e a **imagem do post via DALL-E 3**.

---

## 🎨 VISUAL

- Tema escuro: fundo preto (`#0a0a0a`) com gradientes verdes (`#46c81c`, `#6ddc2f`, `#8be33f`), inspirado na paleta do site da ADGN.
- CSS centralizado em `ESTILO_BASE` (constante em `app.py`), compartilhado entre `/painel` e `/criativos`.
- Navegação por abas (`NAV_HTML` / `nav_html()`) entre **Painel** e **Criativos**.

---

## ⚙️ VARIÁVEIS DE AMBIENTE (Railway)

| Variável | Uso |
|---|---|
| `IG_ACCESS_TOKEN` | Token de acesso da conta Instagram |
| `IG_VERIFY_TOKEN` | Validação do webhook |
| `ANTHROPIC_API_KEY` | Geração de respostas e criativos (texto) |
| `OPENAI_API_KEY` | Geração das imagens dos criativos (DALL-E 3) — **⚠️ ainda precisa ser configurada no Railway** |

---

## 🕐 HISTÓRICO DE MUDANÇAS

### Junho/2026
- ✅ **Painel visual** (`/painel`) criado: KPIs (contatos, leads qualificados, perfis do nicho, comentários excluídos) + gráficos doughnut/bar (Chart.js) para classificação de leads, perfis do nicho e comentários respondidos x excluídos.
- ✅ **Redesigns sucessivos do painel**: tabelas simples → KPIs + gráficos → tema claro com paleta moderna → fundo preto com cores vibrantes → verde neon fluorescente → **paleta final adotada do site ADGN** (`#46c81c` sobre `#0a0a0a`).
- ✅ **Remoção de emojis** nas respostas da IA (Direct e respostas a comentários) — instrução de prompt ajustada para tom mais humano/natural.
- ✅ **Aba de Criativos** (`/criativos`): formulário para gerar post (tema → legenda + hashtags + ideia visual) via `ai_responder.gerar_criativo()`, salvo em `storage["criativos"]` (até 50 itens).
- ✅ **Geração de imagem do post** (`image_gen.py`, DALL-E 3): cada criativo agora também gera uma imagem ilustrativa baseada na "ideia visual", exibida no card. **Pendente**: configurar `OPENAI_API_KEY` no Railway para a imagem ser gerada (sem a chave, o sistema funciona normalmente mas sem imagem).
- ♻️ Refatoração: CSS extraído para `ESTILO_BASE` e navegação compartilhada (`NAV_HTML`) entre as páginas `/painel` e `/criativos`.
