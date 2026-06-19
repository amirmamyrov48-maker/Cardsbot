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

# --- БАЗА ПЕРСОНАЖЕЙ (ПОЛНАЯ) ---
CHARACTERS = {
    "Неуязвимый": {"rarity": "🔮 Секретный", "price": 9999}, "Homelander": {"rarity": "⭐ Легендарный", "price": 500},
    "Soldier Boy": {"rarity": "⭐ Легендарный", "price": 500}, "Starlight": {"rarity": "✨ Эпический", "price": 300},
    "A-Train": {"rarity": "🔹 Редкий", "price": 150}, "The Deep": {"rarity": "🟢 Обычный", "price": 50},
    "Black Noir": {"rarity": "✨ Эпический", "price": 300}, "Queen Maeve": {"rarity": "✨ Эпический", "price": 300},
    "William Butcher": {"rarity": "⭐ Легендарный", "price": 500}, "Frenchie": {"rarity": "🔹 Редкий", "price": 150},
    "Kimiko": {"rarity": "🔹 Редкий", "price": 150}, "Hughie": {"rarity": "🟢 Обычный", "price": 50}
}

OUTFITS = {
    "🎀 Костюм горничной": {"rarity": "🔮 Мифический"},
    "👗 Костюм Старлайт": {"rarity": "✨ Эпический"},
    "🧥 Плащ Бутчера": {"rarity": "🔹 Редкий"},
    "🧢 Кепка Vought": {"rarity": "🟢 Обычный"}
}

def load_data():
    global players_data
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            players_data = {int(k): v for k, v in json.load(f).items()}

def save_data():
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(players_data, f, ensure_ascii=False, indent=4)

def get_player(user_id):
    if user_id not in players_data:
        players_data[user_id] = {"vbucks": 1000, "inventory": [], "outfits": [], "equipped": None, "last_gacha": 0, "last_bonus": 0, "last_outfit_gacha": 0}
    return players_data[user_id]

def get_time_left(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    return f"{h} ч. {m} мин."

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🎰 Гача героев", "👗 Гача костюмов", "🎁 Ежедневка")
    markup.add("👤 Мой Профиль")
    bot.send_message(message.chat.id, "🏢 **Vought International: Система инициализирована.**", parse_mode="Markdown", reply_markup=markup)

@bot.message_handler(func=lambda m: True)
def handle_text(message):
    player = get_player(message.from_user.id)
    
    if message.text == "🎁 Ежедневка":
        if time.time() - player["last_bonus"] >= 86400:
            bonus = 350 if player["equipped"] == "🧥 Плащ Бутчера" else 250
            player["vbucks"] += bonus
            player["last_bonus"] = time.time()
            save_data()
            bot.send_message(message.chat.id, f"✅ **Бонус:** +{bonus} V-Bucks!")
        else:
            left = 86400 - (time.time() - player["last_bonus"])
            bot.send_message(message.chat.id, f"❌ **Рано!** До бонуса: `{get_time_left(left)}`", parse_mode="Markdown")

    elif message.text == "🎰 Гача героев":
        cooldown = 10800
        if player["equipped"] == "👗 Костюм Старлайт": cooldown = 7200
        elif player["equipped"] == "🎀 Костюм горничной": cooldown = 8100
        
        diff = time.time() - player["last_gacha"]
        if diff >= cooldown:
            char = random.choice(list(CHARACTERS.keys()))
            player["inventory"].append(char)
            player["last_gacha"] = time.time()
            save_data()
            bot.send_message(message.chat.id, f"🎰 **Конвейер:** 🎉 Выпал: **{char}**", parse_mode="Markdown")
        else:
            bot.send_message(message.chat.id, f"⏳ **Перегрузка:** ждать `{get_time_left(cooldown - diff)}`", parse_mode="Markdown")

    elif message.text == "👗 Гача костюмов":
        cost = int(300 * 0.85) if player["equipped"] == "🎀 Костюм горничной" else 300
        diff = time.time() - player.get("last_outfit_gacha", 0)
        if diff >= 7200:
            if player["vbucks"] >= cost:
                player["vbucks"] -= cost
                player["last_outfit_gacha"] = time.time()
                outfit = random.choice(list(OUTFITS.keys()))
                player["outfits"].append(outfit)
                save_data()
                bot.send_message(message.chat.id, f"👗 **Fashion:** Вы получили **{outfit}**!", parse_mode="Markdown")
            else:
                bot.send_message(message.chat.id, f"❌ **Средств:** {cost} VB.")
        else:
            bot.send_message(message.chat.id, f"⏳ **Занято:** ждать `{get_time_left(7200 - diff)}`", parse_mode="Markdown")

    elif message.text == "👤 Мой Профиль":
        inv = "\n".join([f"• {c}" for c in set(player["inventory"])])
        text = (f"👤 **Личное дело**\n💰 Баланс: `{player['vbucks']}`\n👗 Надет: `{player['equipped'] or 'Нет'}`\n\n🃏 **Коллекция:**\n{inv or 'Пусто'}")
        bot.send_message(message.chat.id, text, parse_mode="Markdown")

if __name__ == '__main__':
    load_data()
    Thread(target=lambda: Flask('').run(host='0.0.0.0', port=8080)).start()
    bot.infinity_polling()
