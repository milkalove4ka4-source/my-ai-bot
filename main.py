import os
import asyncio
import requests
from aiogram import Bot, Dispatcher, types
from aiohttp import web

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
                # Вставил самую свежую и 100% рабочую фри-модель
                "model": "openchat/openchat-7b:free", 
                "messages": [{"role": "user", "content": message.text}]
            }
        )
        
        if response.status_code == 200:
            ai_text = response.json()['choices'][0]['message']['content']
            await message.answer(ai_text)
        else:
            await message.answer(f"Ошибка ИИ (Код {response.status_code}). Напиши еще раз.")
            
    except Exception as e:
        await message.answer("Ошибка связи с сервером нейросети.")

# Костыль-сервер для удержания деплоя на Render
def init_app():
    app = web.Application()
    app.router.add_get('/', lambda r: web.Response(text="Бот онлайн!"))
    return app

def main():
    print("Бот успешно стартовал!")
    port = int(os.environ.get("PORT", 10000))
    runner = web.AppRunner(init_app())
    
    loop = asyncio.get_event_loop()
    loop.run_until_complete(runner.setup())
    site = web.TCPSite(runner, '0.0.0.0', port)
    loop.run_until_complete(site.start())
    
    # Сбрасываем все прошлые зависшие клики/сообщения
    loop.run_until_complete(bot.delete_webhook(drop_pending_updates=True))
    # Запускаем бесконечный процесс
    loop.run_until_complete(dp.start_polling(bot))

if __name__ == '__main__':
    main()
