import telebot
import requests
import json

# Твои секретные ключи
TG_TOKEN = "8810352397:AAFHuC3cLzfPRYSxt99mo-A3yi189kqWoYk"
AI_TOKEN = "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"

bot = telebot.TeleBot(TG_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Привет! Я твой полностью бесплатный ИИ-ассистент на базе Llama 3. Спроси меня о чем угодно!")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {AI_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "meta-llama/llama-3-8b-instruct:free",
        "messages": [{"role": "user", "content": message.text}]
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        result = response.json()
        reply = result['choices'][0]['message']['content']
        bot.reply_to(message, reply)
    except Exception as e:
        bot.reply_to(message, "Ой, нейросеть задумалась. Попробуй еще раз!")

bot.polling(none_stop=True)
