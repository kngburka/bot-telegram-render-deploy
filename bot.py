import os
import requests
from telegram import Update
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

load_dotenv()

# Modelos disponíveis
models = {
    "llama-3-8b": "meta-llama/llama-3-8b-instruct",
    "mistral-7b": "mistralai/mistral-7b-instruct",
    "openai-3.5": "openai/gpt-3.5-turbo"
}

# === Configurações via variáveis de ambiente ===
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
MODEL = models["llama-3-8b"]

# Histórico e estilos por usuário
user_histories = {}
user_styles = {}
MAX_HISTORY = 10

# === Função para chamar o OpenRouter ===
def query_openrouter(messages):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/seu-usuario/seu-projeto",
        "X-Title": "MeuBotTelegram"
    }

    json_data = {
        "model": MODEL,
        "messages": messages
    }

    response = requests.post(OPENROUTER_API_URL, headers=headers, json=json_data)
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"].strip()

# === Handlers do Telegram ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Olá! Sou um bot IA. Me mande uma pergunta!\n"
        "Use /estilo <formal|engracado|padrao> para mudar o estilo das respostas."
    )

async def set_persona(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    estilo = context.args[0] if context.args else "padrao"

    if estilo == "formal":
        prompt = "Você é um assistente extremamente formal, educado e profissional. Fale sempre em português correto."
    elif estilo == "engracado":
        prompt = "Você é um assistente divertido que faz piadas e responde de forma leve e engraçada, sempre em português."
    else:
        prompt = "Você é um assistente útil que responde sempre em português do Brasil, de forma clara e natural."

    user_styles[user_id] = prompt
    await update.message.reply_text(f"Estilo ajustado para: {estilo}")

async def respond(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_message = update.message.text

    system_prompt = user_styles.get(user_id, "Você é um assistente útil que responde sempre em português do Brasil.")
    
    # Inicia o histórico se ainda não existir
    if user_id not in user_histories:
        user_histories[user_id] = [{"role": "system", "content": system_prompt}]
    else:
        # Atualiza o system prompt
        user_histories[user_id][0] = {"role": "system", "content": system_prompt}

    # Adiciona nova entrada do usuário
    user_histories[user_id].append({"role": "user", "content": user_message})
    
    # Mantém limite de histórico
    if len(user_histories[user_id]) > MAX_HISTORY + 1:
        user_histories[user_id] = [user_histories[user_id][0]] + user_histories[user_id][-MAX_HISTORY:]

    try:
        reply = query_openrouter(user_histories[user_id])
        user_histories[user_id].append({"role": "assistant", "content": reply})
    except Exception as e:
        reply = f"Erro ao acessar a IA: {e}"

    await update.message.reply_text(reply)

# === Inicialização do Bot via Webhook ===
def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("estilo", set_persona))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, respond))
    print("🤖 Bot rodando...")

    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 8443)),
        webhook_url=f"{WEBHOOK_URL}"
    )

if __name__ == "__main__":
    main()
