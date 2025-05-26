# version.py
__version__ = "2.2.0"

import os
import requests
from telegram import Update
from dotenv import load_dotenv
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from utilities import format_total_by_category, format_resumo
from db import (
    init_db,
    save_message,
    get_user_history,
    save_transaction,
    parse_transaction,
    get_summary_by_period,
    get_total_by_category,
    clear_user_data
)

init_db()
load_dotenv()

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
MODEL = "meta-llama/llama-3-8b-instruct"
MAX_HISTORY = 10

# Prompt inicial
SYSTEM_PROMPT = """
Você é um assistente financeiro pessoal inteligente. Seu papel é ajudar o usuário a entender e controlar sua vida financeira.

1. Se a mensagem parecer uma movimentação (ex: "Mercado 120", "Recebi 1000"), extraia:
  - Valor (Moeda R$ x,xx)
  - Descrição
  - Categoria (ex: Alimentação, Transporte, Lazer, etc.)
  - Tipo: Despesa ou Receita
  - Data (assuma hoje no formato dd/mm/yyyy)

2. Retorne isso em formato:
✅ Nova movimentação **registrada**!

💸 Tipo: ...
🧾 Item: ...
🗂️ Categoria: ...
💰 Valor: ...
📅 Data: ...

💡 Dica: ...

3. Se for uma pergunta, responda como um consultor financeiro amigável e didático.

Use sempre emojis e linguagem clara e leve. Se não entender a mensagem, peça para reformular.
"""

def query_openrouter(messages):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/seu-usuario/seu-projeto",
        "X-Title": "AssistenteFinanceiroTelegram"
    }

    json_data = {
        "model": MODEL,
        "messages": messages
    }

    response = requests.post(OPENROUTER_API_URL, headers=headers, json=json_data)
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"].strip()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Olá! 👋 Sou seu assistente financeiro pessoal.\n"
        "Me envie uma movimentação como \"Mercado 120\" ou \"Ganhei 500\", ou pergunte algo sobre finanças!"
    )

async def respond(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_message = update.message.text.strip()

    save_message(user_id, "user", user_message)
    history = get_user_history(user_id, MAX_HISTORY)
    history.insert(0, {"role": "system", "content": SYSTEM_PROMPT})

    try:
        reply = query_openrouter(history)
        save_message(user_id, "assistant", reply)

        extracted = parse_transaction(reply)
        if extracted:
            save_transaction(user_id, **extracted)

        await update.message.reply_text(reply)

    except Exception as e:
        await update.message.reply_text(f"❌ Ocorreu um erro ao processar: {e}")

async def resumo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    args = context.args
    if not args:
        await update.message.reply_text("❓ Use /resumo hoje | semana | mes | ou informe datas: /resumo dd/mm/yyyy a dd/mm/yyyy")
        return

    from datetime import datetime, timedelta
    texto = " ".join(args).lower()
    hoje = datetime.now().date()

    if texto == "hoje":
        inicio = fim = hoje
    elif texto == "semana":
        inicio = hoje - timedelta(days=7)
        fim = hoje
    elif texto == "mes":
        inicio = hoje.replace(day=1)
        fim = hoje
    elif " a " in texto:
        try:
            partes = texto.split(" a ")
            inicio = datetime.strptime(partes[0], "%d/%m/%Y").date()
            fim = datetime.strptime(partes[1], "%d/%m/%Y").date()
        except:
            await update.message.reply_text("⚠️ Datas inválidas. Use o formato: /resumo 01/05/2025 a 15/05/2025")
            return
    else:
        await update.message.reply_text("❓ Período não reconhecido. Use hoje, semana, mes ou datas personalizadas.")
        return

    resumo = get_summary_by_period(user_id, inicio, fim)
    mensagem = format_resumo(resumo)
    await update.message.reply_text(mensagem, parse_mode=ParseMode.MARKDOWN)

async def total_categoria(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    total = get_total_by_category(user_id)
    mensagem = format_total_by_category(total)
    await update.message.reply_text(mensagem, parse_mode=ParseMode.MARKDOWN)

async def limpar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if context.args and context.args[0].lower() == "confirmar":
        clear_user_data(user_id)
        await update.message.reply_text("📉 Histórico de mensagens e transações apagado com sucesso!")
    else:
        await update.message.reply_text("⚠️ Essa ação é irreversível. Se tem certeza, envie: /limpar confirmar")

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("resumo", resumo))
    app.add_handler(CommandHandler("total", total_categoria))
    app.add_handler(CommandHandler("limpar", limpar))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, respond))

    print("🤖 Bot financeiro rodando...")
    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 8443)),
        webhook_url=WEBHOOK_URL
    )

if __name__ == "__main__":
    main()
