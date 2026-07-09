import os
import telebot
import requests
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

BOT_TOKEN = '8810352397:AAFHuC3cLzfPRYSxt99mo-A3yil89kqWoYk'
OPENROUTER_API_KEY = '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'

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.reply_to(message, "Привет! Я наконец-то работаю. Задавай вопрос!")

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
            bot.reply_to(message, f"Ошибка нейросети: {response.status_code}")
    except Exception as e:
        bot.reply_to(message, "Ошибка связи с ИИ.")

# Простой веб-сервер, чтобы Render не закрывал приложение
class WebServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), WebServer)
    server.serve_forever()

if __name__ == "__main__":
    threading.Thread(target=run_web_server, daemon=True).start()
    print("Бот запущен. Начинаем пробивать ошибку 409...")
    
    # Пытаемся запустить бота по кругу. Если старый процесс мешает (409), 
    # код не падает, а просто ждет 5 секунд и пробует снова, пока старый процесс не сдохнет.
    while True:
        try:
            bot.remove_webhook()
            bot.polling(none_stop=True, interval=1, timeout=20)
        except Exception as e:
            print(f"Зависло старое соединение (ошибка 409). Повтор через 5 сек...")
            time.sleep(5)
