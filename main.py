import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import telebot
import requests

# Твои данные (уже вставлены и проверены на пробелы)
BOT_TOKEN = '8810352397:AAFHuC3cLzfPRYSxt99mo-A3yil89kqWoYk'
OPENROUTER_API_KEY = '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'

bot = telebot.TeleBot(BOT_TOKEN)

# Ответ на команду /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я твой ИИ-бот. Задай мне любой вопрос, и я отвечу!")

# Отправка сообщений в нейросеть OpenRouter
@bot.message_handler(func=lambda message: True)
def ask_ai(message):
    # Отправляем визуальный статус, что бот "печатает" ответ
    bot.send_chat_action(message.chat.id, 'typing')
    
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "google/gemini-2.5-flash", # Шустрая и бесплатная модель
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

# Костыль для бесплатного Render (веб-сервер)
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"Bot is running successfully!")

def run_health_check_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

if __name__ == "__main__":
    # Запуск сайта-заглушки для Render
    threading.Thread(target=run_health_check_server, daemon=True).start()
    
    # Запуск бота
    print("Бот успешно стартовал!")
    bot.infinity_polling()
