import os
import random
import telebot
from telebot import types

# БЕЗОПАСНОСТЬ: Сначала бот ищет токен в настройках сервера Render (переменная BOT_TOKEN).
# Если не находит (например, при запуске в Pydroid 3), берет строку вручную.
# ЗАМЕНИ 'ТВОЙ_ТОКЕН_ОТ_BOTFATHER' на свой настоящий токен для тестов в Pydroid.
TOKEN = os.environ.get('BOT_TOKEN') or 'ТВОЙ_ТОКЕН_ОТ_BOTFATHER'

bot = telebot.TeleBot(TOKEN)

# Расширенная база персонажей из вселенной "Пацаны" (The Boys)
CHARACTERS = [
    # Легендарные (Шанс 5%)
    {"name": "🇺🇸 Хоумлендер (Homelander)", "rarity": "Легендарный 👑", "chance": 5, "desc": "Лидер Семёрки. Самый могущественный и самый нестабильный супергерой на планете. Пьет молоко, лазер из глаз делает 'вжух'."},
    {"name": "🕵️‍♂️ Билли Бутчер (Billy Butcher)", "rarity": "Легендарный 👑", "chance": 5, "desc": "Лидер Пацанов. Ненавидит суперов всей душой. Его главное суперсвойство — невероятная харизма и коронное слово на букву 'C'."},
    {"name": "🛡️ Солдатик (Soldier Boy)", "rarity": "Легендарный 👑", "chance": 5, "desc": "Супергерой золотой эпохи и живое оружие. Обладает сокрушительным радиоактивным лучом, выжигающим Сыворотку V. Немного застрял в 1980-х."},
    {"name": "⚡ Штормфронт (Stormfront)", "rarity": "Легендарный 👑", "chance": 5, "desc": "Повелительница плазмы и молний с очень мрачным прошлым из 1940-х. Мастер манипуляций в соцсетях и настоящая нацистка."},

    # Эпические (Шанс 15%)
    {"name": "🗡️ Королева Мэйв (Queen Maeve)", "rarity": "Эпический 🔥", "chance": 15, "desc": "Вторая по силе в Семёрке. Долгое время топила цинизм в алкоголе, но внутри осталась настоящим героем. Готова пойти против Хоумлендера."},
    {"name": "🦾 Кимико / Самка (Kimiko)", "rarity": "Эпический 🔥", "chance": 15, "desc": "Немая воительница из команды Пацанов. Обладает безумной регенерацией и способностью разрывать врагов голыми руками. Любит мюзиклы."},
    {"name": "💥 Виктория Ньюман (Victoria Neuman)", "rarity": "Эпический 🔥", "chance": 15, "desc": "Политикет, конгрессвумен и скрытый супер. Взрывает головы силой мысли направо и налево. Буквально."},
    {"name": "🥷 Черный Нуар (Black Noir)", "rarity": "Эпический 🗡️", "chance": 15, "desc": "Молчаливый и смертоносный инструмент Воут. Мастер боевых искусств и любитель воображаемых мягких игрушек."},
    {"name": "⚡ Старлайт (Starlight)", "rarity": "Эпический ✨", "chance": 15, "desc": "Энни Дженьюари. Излучает чистый свет и пытается искренне помогать людям, несмотря на весь грязь и коммерцию Воут."},
    {"name": "🐟 Подводный (The Deep)", "rarity": "Эпический 🐙", "chance": 15, "desc": "Повелитель морей и океанов (по его собственному мнению). Лучший друг дельфинов и осьминогов, абсолютный чемпион по кринжу."},

    # Редкие (Шанс 30%)
    {"name": "🏃‍♂️ Поезд-А (A-Train)", "rarity": "Редкий ⚡", "chance": 30, "desc": "Самый быстрый человек в мире. Главное — не стоять у него на пути, когда он подсел на дозу Сыворотки V."},
    {"name": "🩺 Хьюи Кэмпбелл (Hughie)", "rarity": "Редкий 👕", "chance": 30, "desc": "Обычный парень в винтажной футболке, который случайно ввязался в войну с богами. Постоянно в чужой крови и экзистенциальном ужасе."},
    {"name": "🇫🇷 Французик (Frenchie)", "rarity": "Редкий 🧪", "chance": 30, "desc": "Мастер на все руки: от химии до тактического взлома. Называет Кимико своей 'mon cœur' и постоянно спорит с Бутчером."},
    {"name": "💼 Стэн Эдгар (Stan Edgar)", "rarity": "Редкий 💼", "chance": 30, "desc": "Бывший глава корпорации Vought. Обычный человек без суперсил, но единственный, чей ледяной взгляд и стальной голос заставляют Хоумлендера потеть от страха."},
    {"name": "🦧 Райан (Ryan Butcher)", "rarity": "Редкий 👦", "chance": 30, "desc": "Сын Хоумлендера и Бекки Бутчер. Обладает скрытым потенциалом стать сильнее отца, но пока просто пытается разобраться, на чьей он стороне."},

    # Обычные (Шанс 50%)
    {"name": "🥛 Молоко Матери (Mother's Milk)", "rarity": "Обычный 🧼", "chance": 50, "desc": "Голос разума в команде Бутчера. Страдает ОКР, фанатеет по рэпу старой школы, ценит порядок и чистоту."},
    {"name": "🏢 Тодд (Todd)", "rarity": "Обычный 🤡", "chance": 50, "desc": "Муж бывшей жены ММ. Яростный фанат Хоумлендера, готовый оправдать любое военное преступление своего кумира. Максимально раздражающий тип."},
    {"name": "🏹 Прозрачный (Translucent)", "rarity": "Обычный 💎", "chance": 50, "desc": "Супергерой с невидимой алмазной кожей. Любил шпионить в туалетах. Запомнился всем тем, *как именно* Пацаны смогли его победить."},
    {"name": "🔥 Факел (Lamplighter)", "rarity": "Обычный 🕯️", "chance": 50, "desc": "Бывший член Семёрки, управляющий огнем. Работает охранником в секретной психбольнице Воут."}
]

user_collections = {}

def pull_card():
    population = CHARACTERS
    weights = [char["chance"] for char in population]
    chosen = random.choices(population, weights=weights, k=1)[0]
    return chosen

# --- ОБРАБОТЧИКИ КОМАНД ---

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "👊 **Добро пожаловать во вселенную «Пацанов»!** 👊\n\n"
        "Здесь заправляет безжалостная корпорация Vought. "
        "Готов собрать свою ультимативную команду из героев Семёрки или Пацанов Бутчера?\n\n"
        "Жми кнопку ниже, чтобы применить дозу Compound V!"
    )
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("🃏 Испытать удачу (Vought)"), types.KeyboardButton("💼 Моя база суперов"))
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.text == "🃏 Испытать удачу (Vought)")
def draw_card_handler(message):
    chat_id = message.chat.id
    character = pull_card()
    name = character["name"]
    rarity = character["rarity"]
    desc = character["desc"]
    
    if chat_id not in user_collections:
        user_collections[chat_id] = {}
        
    if name in user_collections[chat_id]:
        user_collections[chat_id][name] += 1
        dup_text = f"_(У тебя в запасе их уже: {user_collections[chat_id][name]})_"
    else:
        user_collections[chat_id][name] = 1
        dup_text = "🔥 *Новый оперативник зачислен в твой отряд!*"

    response = (
        f"🚨 **Сканирование Vought обнаружило объект!** 🚨\n"
        f"----------------------------------------\n"
        f"👤 **Имя:** {name}\n"
        f"💎 **Ранг:** {rarity}\n"
        f"📜 **Досье:** {desc}\n"
        f"----------------------------------------\n"
        f"{dup_text}"
    )
    bot.send_message(chat_id, response, parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.text == "💼 Моя база суперов")
def show_collection(message):
    chat_id = message.chat.id
    collection = user_collections.get(chat_id, {})
    
    if not collection:
        bot.send_message(chat_id, "Твой отряд пуст. Примени сыворотку V! 🃏")
        return
        
    text = "💼 **Досье твоего личного отряда:**\n\n"
    total_unique = len(CHARACTERS)
    user_unique = len(collection)
    
    text += f"📊 Завербовано персонажей: {user_unique} из {total_unique}\n"
    text += "----------------------------------------\n"
    
    for char_name, count in sorted(collection.items()):
        rarity = next((c["rarity"] for c in CHARACTERS if c["name"] == char_name), "")
        text += f"• {char_name} [{rarity}] — x{count}\n"
        
    bot.send_message(chat_id, text, parse_mode="Markdown")

if __name__ == '__main__':
    print("Бот запущен...")
    bot.infinity_polling()

# --- КОСТЫЛЬ ДЛЯ БЕСПЛАТНОГО ХОСТИНГА RENDER ---
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Бот Пацанов активен и работает!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

if __name__ == '__main__':
    keep_alive() # Запускает мини-веб-сервер в фоне
    print("Бот запущен...")
    bot.infinity_polling()
