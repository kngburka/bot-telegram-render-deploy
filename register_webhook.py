import os
import requests
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_URL = "https://bot-telegram-render-deploy.onrender.com"

set_webhook_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook"
response = requests.post(set_webhook_url, params={"url": WEBHOOK_URL})

print("Webhook setado:", response.status_code, response.text)

get_webhook_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getWebhookInfo"

try:
    response = requests.get(get_webhook_url)
    response.raise_for_status()
    print("Webhook Info:", response.json())
except requests.exceptions.RequestException as e:
    print(f"Erro na requisição: {e}")