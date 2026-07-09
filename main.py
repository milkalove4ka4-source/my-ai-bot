import os
import telebot
import requests
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

# Загружаем ключи из настроек Render
BOT_TOKEN = os.environ.get('BOT_TOKEN')
OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY')

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.reply_to(message, "Привет! Я твой обновленный ИИ-бот. Задай мне любой вопрос, и я отвечу!")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    # Показываем статус "печатает..."
    bot.send_chat_action(message.chat.id, 'typing')
    
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "meta-llama/llama-3-8b-instruct:free",  # 100% бесплатная и быстрая модель
                "messages": [
                    {"role": "user", "content": message.text}
                ]
            }
        )
        
        if response.status_code == 200:
            ai_text = response.json()['choices'][0]['message']['content']
            bot.reply_to(message, ai_text)
        else:
            bot.reply_to(message, f"Ошибка нейросети (Код {response.status_code}). Попробуй позже.")
            
    except Exception as e:
        bot.reply_to(message, "Произошла ошибка при попытке связаться с ИИ.")

# === Костыль для бесплатного Render (веб-сервер) ===
class WebServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")
    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), WebServer)
    server.serve_forever()

if __name__ == "__main__":
    # Запускаем веб-сервер в отдельном потоке
    threading.Thread(target=run_web_server, daemon=True).start()
    
    print("Бот успешно стартовал!")
    
    # Жесткий сброс всех зависших сессий Telegram, чтобы убрать ошибку 409
    bot.remove_webhook(drop_pending_updates=True)
    
    # Запуск приема сообщений
    bot.infinity_polling()
