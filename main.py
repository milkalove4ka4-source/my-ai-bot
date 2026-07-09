import os
import telebot
import requests
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

# Твои ключи вшиты прямо в код
BOT_TOKEN = '8810352397:AAFHuC3cLzfPRYSxt99mo-A3yil89kqWoYk'
OPENROUTER_API_KEY = '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'

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.reply_to(message, "Привет! Я твой обновленный ИИ-бот. Задай мне любой вопрос, и я отвечу!")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    # Показываем статус "печатает..." в чате
    bot.send_chat_action(message.chat.id, 'typing')
    
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "meta-llama/llama-3.1-8b-instruct:free",  # 100% бесплатная модель
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

# === Веб-сервер для бесплатного тарифа Render ===
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

# === Главный запуск программы ===
if __name__ == "__main__":
    # Запускаем веб-сервер, чтобы Render не ругался
    threading.Thread(target=run_web_server, daemon=True).start()
    
    print("Бот успешно стартовал!")
    
    # Сбрасываем старые вебхуки, если они зависли
    bot.remove_webhook()
    
    # Самый стабильный и классический бесконечный запуск бота
    bot.polling(none_stop=True)
