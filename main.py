import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiohttp import web

BOT_TOKEN = '8810352397:AAFHuC3cLzfPRYSxt99mo-A3yil89kqWoYk'

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Бот будет просто возвращать твой текст обратно
@dp.message()
def echo_handler(message: types.Message):
    message.answer(f"Ты написал: {message.text}")

# Веб-сервер для Render (без него он засыпает)
def init_app():
    app = web.Application()
    app.router.add_get('/', lambda r: web.Response(text="Бот активен"))
    return app

def main():
    print("Запуск эхо-бота...")
    # Запускаем веб-сервер на фоне
    port = int(os.environ.get("PORT", 10000))
    runner = web.AppRunner(init_app())
    
    loop = asyncio.get_event_loop()
    loop.run_until_complete(runner.setup())
    site = web.TCPSite(runner, '0.0.0.0', port)
    loop.run_until_complete(site.start())
    
    # Сбрасываем все старые зависшие сообщения
    loop.run_until_complete(bot.delete_webhook(drop_pending_updates=True))
    
    # Запускаем чтение сообщений
    loop.run_until_complete(dp.start_polling(bot))

if __name__ == '__main__':
    main()

