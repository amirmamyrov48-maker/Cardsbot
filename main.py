import os
import random
import json
from threading import Thread
from telebot import types
import telebot
from flask import Flask

# --- НАСТРОЙКИ ---
TOKEN = '8692486059:AAEtXHVYTVaCnRyAHxLEnfMg05CBlc35zLo'
bot = telebot.TeleBot(TOKEN)
DB_FILE = "players_backup.json"
players_data = {}

# --- БАЗА ПЕРСОНАЖЕЙ (50 + Секретный) ---
# НИКАКИХ ССЫЛОК ИЛИ КАРТИНОК В БАЗЕ НЕТ
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

# --- ФУНКЦИИ ---
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
        players_data[user_id] = {"vbucks": 100, "inventory": []}
    return players_data[user_id]

# --- ОБРАБОТЧИКИ ---
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🎰 Крутить Гачу", "👤 Мой Профиль")
    bot.send_message(message.chat.id, "🏢 Добро пожаловать в Vought!", reply_markup=markup)

@bot.message_handler(func=lambda m: True)
def handle_text(message):
    player = get_player(message.from_user.id)
    
    if message.text == "🎰 Крутить Гачу":
        if random.random() < 0.01:
            char_name = "Неуязвимый"
        else:
            char_name = random.choice([name for name in CHARACTERS.keys() if name != "Неуязвимый"])
            
        player["inventory"].append(char_name)
        save_data()
        # Только текст!
        bot.send_message(message.chat.id, f"🎉 Тебе выпал: **{char_name}** ({CHARACTERS[char_name]['rarity']})")
    
    elif message.text == "👤 Мой Профиль":
        # Только текст!
        bot.send_message(message.chat.id, f"💰 VB: {player['vbucks']}\n🃏 Карт в коллекции: {len(player['inventory'])}")

# --- ЗАПУСК ---
if __name__ == '__main__':
    load_data()
    Thread(target=lambda: Flask('').run(host='0.0.0.0', port=8080)).start()
    bot.infinity_polling()
