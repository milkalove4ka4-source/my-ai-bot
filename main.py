import os
import telebot
import requests
from flask import Flask, request

# Твои ключи
BOT_TOKEN = '8810352397:AAFHuC3cLzfPRYSxt99mo-A3yil89kqWoYk'
OPENROUTER_API_KEY = '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'

# Имя твоего приложения на Render (взято из твоих логов)
RENDER_APP_NAME = 'my-ai-bot-5gyc'
WEBHOOK_URL = f"https://{RENDER_APP_NAME}.onrender.com/{BOT_TOKEN}"

bot = telebot.TeleBot(BOT_TOKEN, threaded=False)
app = Flask(__name__)

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.reply_to(message, "Привет! Я твой обновленный ИИ-бот. Задай мне любой вопрос, и я отвечу!")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    bot.send_chat_action(message.chat.id, 'typing')
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "meta-llama/llama-3.1-8b-instruct:free",
                "messages": [{"role": "user", "content": message.text}]
            }
        )
        if response.status_code == 200:
            ai_text = response.json()['choices'][0]['message']['content']
            bot.reply_to(message, ai_text)
        else:
            bot.reply_to(message, f"Ошибка нейросети (Код {response.status_code}).")
    except Exception as e:
        bot.reply_to(message, "Произошла ошибка при попытке связаться с ИИ.")

# Обработчик запросов от Telegram
@app.route(f'/{BOT_TOKEN}', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return '', 200
    else:
        return 'Invalid request', 403

@app.route('/')
def index():
    return "Bot is running via Webhook!", 200

if __name__ == "__main__":
    print("Установка вебхука в Telegram...")
    bot.remove_webhook()
    # Принудительно очищаем очередь обновлений и ставим вебхук
    bot.set_webhook(url=WEBHOOK_URL, drop_pending_updates=True)
    
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
