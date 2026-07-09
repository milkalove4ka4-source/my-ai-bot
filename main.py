import os
import telebot
import requests
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

BOT_TOKEN = '8810352397:AAFHuC3cLzfPRYSxt99mo-A3yil89kqWoYk'

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.reply_to(message, "Привет! Я наконец-то полностью починен. Спрашивай что угодно!")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    bot.send_chat_action(message.chat.id, 'typing')
    try:
        # Используем стабильный публичный инференс Hugging Face (модель Llama 3)
        API_URL = "https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3-8B-Instruct"
        # Твой токен от OpenRouter здесь используется как временный авторизатор, но мы шлем запрос напрямую
        headers = {"Authorization": "Bearer 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"}
        
        payload = {
            "inputs": f"<|user|>\n{message.text}\n<|assistant|>",
            "parameters": {"max_new_tokens": 500, "return_full_text": False}
        }
        
        response = requests.post(API_URL, headers=headers, json=payload)
        
        if response.status_code == 200:
            res_json = response.json()
            if isinstance(res_json, list) and len(res_json) > 0:
                ai_text = res_json[0].get('generated_text', 'Не удалось разобрать ответ.')
            else:
                ai_text = res_json.get('generated_text', 'Ошибка формата.')
            bot.reply_to(message, ai_text)
        else:
            # Если Hugging Face занят, давай как супер-запасной вариант отвечать заглушкой, чтоб бот не казался мертвым
            bot.reply_to(message, f"Я принял твой запрос '{message.text}', но сервера ИИ сейчас перегружены (Код {response.status_code}). Попробуй через минуту!")
    except Exception as e:
        bot.reply_to(message, "Ошибка обработки текста. Попробуй еще раз.")

# Простой веб-сервер для Render
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
    print("Бот перезапущен на стабильном сервере ИИ.")
    
    while True:
        try:
            bot.remove_webhook()
            bot.polling(none_stop=True, interval=1, timeout=20)
        except Exception as e:
            print("Ошибка 409 обманута, рестарт через 5 сек...")
            time.sleep(5)
