import os
import random
import json
import time
from threading import Thread
from telebot import types
import telebot
from flask import Flask

# --- НАСТРОЙКИ ---
TOKEN = '8692486059:AAEtXHVYTVaCnRyAHxLEnfMg05CBlc35zLo'
bot = telebot.TeleBot(TOKEN)
DB_FILE = "players_backup.json"
players_data = {}

# --- БАЗЫ ---
CHARACTERS = {
    "Неуязвимый": {"rarity": "🔮 Секретный", "price": 9999},
    "Homelander": {"rarity": "⭐ Легендарный", "price": 500},
    "Soldier Boy": {"rarity": "⭐ Легендарный", "price": 500},
    "Starlight": {"rarity": "✨ Эпический", "price": 300},
    "A-Train": {"rarity": "🔹 Редкий", "price": 150},
    "The Deep": {"rarity": "🟢 Обычный", "price": 50},
    "Black Noir": {"rarity": "✨ Эпический", "price": 300},
    "Queen Maeve": {"rarity": "✨ Эпический", "price": 300},
    "William Butcher": {"rarity": "⭐ Легендарный", "price": 500},
    "Frenchie": {"rarity": "🔹 Редкий", "price": 150},
    "Kimiko": {"rarity": "🔹 Редкий", "price": 150},
    "Hughie": {"rarity": "🟢 Обычный", "price": 50},
    "Mother's Milk": {"rarity": "🔹 Редкий", "price": 150},
    "Stormfront": {"rarity": "⭐ Легендарный", "price": 500},
    "Victoria Neuman": {"rarity": "✨ Эпический", "price": 300},
    "Stan Edgar": {"rarity": "⭐ Легендарный", "price": 500},
    "Ryan Butcher": {"rarity": "⭐ Легендарный", "price": 500},
    "Lamplighter": {"rarity": "✨ Эпический", "price": 300},
    "Tek-Knight": {"rarity": "✨ Эпический", "price": 300},
    "Sister Sage": {"rarity": "✨ Эпический", "price": 300},
    "Firecracker": {"rarity": "✨ Эпический", "price": 300},
    "Translucent": {"rarity": "🔹 Редкий", "price": 150},
    "Mesmer": {"rarity": "🔹 Редкий", "price": 150},
    "Popclaw": {"rarity": "🔹 Редкий", "price": 150},
    "Shockwave": {"rarity": "🔹 Редкий", "price": 150},
    "Gunpowder": {"rarity": "🔹 Редкий", "price": 150},
    "Blue Hawk": {"rarity": "🔹 Редкий", "price": 150},
    "Supersonic": {"rarity": "🔹 Редкий", "price": 150},
    "Blindspot": {"rarity": "🔹 Редкий", "price": 150},
    "Naqib": {"rarity": "🔹 Редкий", "price": 150},
    "Love Sausage": {"rarity": "🔹 Редкий", "price": 150},
    "Golden Boy": {"rarity": "✨ Эпический", "price": 300},
    "Marie Moreau": {"rarity": "✨ Эпический", "price": 300},
    "Andre Anderson": {"rarity": "✨ Эпический", "price": 300},
    "Jordan Li": {"rarity": "✨ Эпический", "price": 300},
    "Emma Meyer": {"rarity": "🔹 Редкий", "price": 150},
    "Sam Riordan": {"rarity": "⭐ Легендарный", "price": 500},
    "Cate Dunlap": {"rarity": "⭐ Легендарный", "price": 500},
    "Crimson Countess": {"rarity": "✨ Эпический", "price": 300},
    "Mind-Storm": {"rarity": "⭐ Легендарный", "price": 500},
    "Zoe Neuman": {"rarity": "✨ Эпический", "price": 300},
    "Ezekiel": {"rarity": "✨ Эпический", "price": 300},
    "Ashley Barrett": {"rarity": "🟢 Обычный", "price": 50},
    "Becca Butcher": {"rarity": "🟢 Обычный", "price": 50},
    "Grace Mallory": {"rarity": "🟢 Обычный", "price": 50},
    "Todd": {"rarity": "🟢 Обычный", "price": 50},
    "Nathan Franklin": {"rarity": "🟢 Обычный", "price": 50},
    "Donna January": {"rarity": "🟢 Обычный", "price": 50},
    "Cherie": {"rarity": "🟢 Обычный", "price": 50},
    "Hugh Campbell Sr.": {"rarity": "🟢 Обычный", "price": 50},
    "Black Noir II": {"rarity": "⭐ Легендарный", "price": 500}
}

OUTFITS = {
    "🎀 Костюм горничной": {"rarity": "🔮 Мифический", "buff": "Удача +10%, кулдаун -45м, скидка 15%"},
    "👗 Костюм Старлайт": {"rarity": "✨ Эпический", "buff": "Снижает кулдаун гачи на 1 час"},
    "🧥 Плащ Бутчера": {"rarity": "🔹 Редкий", "buff": "Бонус к ежедневке +100 VB"},
    "🧢 Кепка Vought": {"rarity": "🟢 Обычный", "buff": "Стиль +1"}
}

# --- ФУНКЦИИ ---
def load_data():
    global players_data
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                players_data = {int(k): v for k, v in json.load(f).items()}
        except: players_data = {}

def save_data():
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(players_data, f, ensure_ascii=False, indent=4)

def get_player(user_id):
    if user_id not in players_data:
        players_data[user_id] = {"vbucks": 1000, "inventory": [], "outfits": [], "equipped": None, "last_gacha": 0, "last_bonus": 0}
    return players_data[user_id]

# --- ОБРАБОТЧИКИ ---
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🎰 Гача героев", "👗 Гача костюмов", "🎁 Ежедневка")
    markup.add("👤 Мой Профиль")
    bot.send_message(message.chat.id, "🏢 Vought International: система инициализирована.", reply_markup=markup)

@bot.message_handler(func=lambda m: True)
def handle_text(message):
    player = get_player(message.from_user.id)
    
    if message.text == "🎰 Гача героев":
        # Логика кулдауна с учетом костюмов
        cooldown = 10800
        if player["equipped"] == "👗 Костюм Старлайт": cooldown = 7200
        elif player["equipped"] == "🎀 Костюм горничной": cooldown = 8100
        
        if time.time() - player["last_gacha"] >= cooldown:
            char_name = random.choice(list(CHARACTERS.keys()))
            char_info = CHARACTERS[char_name]
            player["inventory"].append(char_name)
            player["last_gacha"] = time.time()
            save_data()
            bot.send_message(message.chat.id, f"✅ Получен: **{char_name}** ({char_info['rarity']})")
        else:
            bot.send_message(message.chat.id, "⏳ Конвейер на перезарядке.")

    elif message.text == "👗 Гача костюмов":
        if player["vbucks"] >= 300:
            player["vbucks"] -= 300
            rand = random.random()
            if rand < 0.05: outfit = "🎀 Костюм горничной"
            elif rand < 0.25: outfit = "👗 Костюм Старлайт"
            elif rand < 0.55: outfit = "🧥 Плащ Бутчера"
            else: outfit = "🧢 Кепка Vought"
            player["outfits"].append(outfit)
            save_data()
            bot.send_message(message.chat.id, f"👗 Выпал костюм: **{outfit}**")
        else: bot.send_message(message.chat.id, "❌ Недостаточно средств.")

    elif message.text == "🎁 Ежедневка":
        if time.time() - player["last_bonus"] >= 86400:
            bonus = 350 if player["equipped"] == "🧥 Плащ Бутчера" else 250
            player["vbucks"] += bonus
            player["last_bonus"] = time.time()
            save_data()
            bot.send_message(message.chat.id, f"✅ Бонус: {bonus} VB!")
        else: bot.send_message(message.chat.id, "❌ Рано.")

    elif message.text == "👤 Мой Профиль":
        rarity_counts = {}
        for char in player["inventory"]:
            r = CHARACTERS[char]["rarity"]
            rarity_counts[r] = rarity_counts.get(r, 0) + 1
        
        text = (f"👤 **ДОСЬЕ СОТРУДНИКА**\n"
                f"💰 Баланс: {player['vbucks']} VB\n"
                f"👗 Надет: {player['equipped'] or 'Нет'}\n"
                f"📊 Героев: {len(player['inventory'])}\n"
                f"🎒 Костюмы: {', '.join(player['outfits'])}")
        bot.send_message(message.chat.id, text, parse_mode="Markdown")

if __name__ == '__main__':
    load_data()
    Thread(target=lambda: Flask('').run(host='0.0.0.0', port=8080)).start()
    bot.infinity_polling()
