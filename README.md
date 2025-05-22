# 🤖 Telegram Bot com LLM via OpenRouter

Este projeto é um chatbot de Telegram alimentado por modelos de linguagem (LLMs) como LLaMA 3 e Mistral, usando a API da [OpenRouter.ai](https://openrouter.ai). O bot roda via Webhook e está pronto para deploy gratuito na [Render.com](https://render.com).

---

## 🚀 Funcionalidades

- Integração com modelos LLM como **LLaMA 3** e **Mistral 7B**
- Personalização da personalidade do bot com comando `/estilo`
- Suporte a **histórico de conversas por usuário**
- Rodando via **Webhook** (ideal para uptime 24/7)
- Pronto para deploy gratuito na **Render**

---

## 🧠 Modelos compatíveis

- `meta-llama/llama-3-8b-instruct`
- `mistralai/mistral-7b-instruct`

Você pode alterar o modelo no código, na variável `MODEL`.

---

## 🧱 Requisitos

- Python 3.10+
- Uma conta em [Render](https://render.com)
- Um bot criado no Telegram ([BotFather](https://t.me/BotFather))
- Uma chave da API do [OpenRouter](https://openrouter.ai/)

---

## ⚙️ Como configurar

1. **Clone o projeto:**

```bash
git clone https://github.com/seu-usuario/seu-repositorio.git
cd seu-repositorio
