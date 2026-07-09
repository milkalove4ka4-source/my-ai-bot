import os
import asyncio
import requests
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from aiogram import Bot, Dispatcher, types

BOT_TOKEN = '8810352397:AAFHuC3cLzfPRYSxt99mo-A3yil89kqWoYk'
OPENROUTER_API_KEY = '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'

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message()
async def ai_handler(message: types.Message):
    # Показываем статус "печатает..."
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")
    
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "openchat/openchat-7b:free", 
                "messages": [{"role": "user", "content": message.text}]
            }
        )
        
        if response.status_code == 200:
            ai_text = response.json()['choices'][0]['message']['content']
            await message.answer(ai_text)
        else:
            await message.answer(f"Ошибка ИИ (Код {response.status_code}). Напиши еще раз чуть позже.")
            
    except Exception as e:
        await message.answer("Ошибка связи с сервером нейросети.")

# Легковесный синхронный сервер для обхода проверки портов Render
class WebServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")
    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), WebServer)
    server.serve_forever()

async def main():
    # Принудительно сбрасываем старые вебхуки и зависшие сообщения
    await bot.delete_webhook(drop_pending_updates=True)
    print("Запуск бота...")
    await dp.start_polling(bot)

if __name__ == '__main__':
    # Запускаем веб-сервер в фоновом потоке (он займет порт мгновенно)
    threading.Thread(target=run_web_server, daemon=True).start()
    print("Веб-сервер запущен для прохождения проверок Render.")
    
    # Запускаем асинхронного бота в основном потоке
    asyncio.run(main())
