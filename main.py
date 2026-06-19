import os
import random
import time
import json
from threading import Thread
from telebot import types
import telebot
from flask import Flask

# --- НАСТРОЙКИ ---
TOKEN = os.environ.get('8692486059:AAEtXHVYTVaCnRyAHxLEnfMg05CBlc35zLo') or 'ТВОЙ_ТОКЕН_ОТ_BOTFATHER'
ADMIN_ID = 8538994090  # <--- ЗАМЕНИ НА СВОЙ ID
bot = telebot.TeleBot(TOKEN)
DB_FILE = "players_backup.json"
players_data = {}

# --- БАЗА ---
PROMO_CODES = {
    "VOUGHT2026": {"reward_type": "vbucks", "amount": 300, "uses": 50, "claimed_by": []},
    "HILLOWDOLBAEB": {"reward_type": "vbucks", "amount": 500, "uses": 100, "claimed_by": []},
    "KRUTOIMOPS": {"reward_type": "compound_v", "amount": 1, "uses": 100, "claimed_by": []},
    "FREESHOT": {"reward_type": "compound_v", "amount": 1, "uses": 20, "claimed_by": []}
}

CHARACTERS = {
    "Homelander": {"rarity": "⭐ Легендарный", "price": 500},
    "Soldier Boy": {"rarity": "⭐ Легендарный", "price": 500},
    "Starlight": {"rarity": "✨ Эпический", "price": 300},
    "A-Train": {"rarity": "🔹 Редкий", "price": 150},
    "The Deep": {"rarity": "🟢 Обычный", "price": 50},
    # ... здесь можно добавить остальные из списка до 50
}

# --- ФУНКЦИИ БАЗЫ ---
def load_data():
    global players_data
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            players_data = {int(k): v for k, v in json.load(f).items()}

def save_data():
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(players_data, f, ensure_ascii=False, indent=4)

def get_or_create_player(user_id, username="Аноним"):
    if user_id not in players_data:
        players_data[user_id] = {
            "username": username, "vbucks": 100, "inventory": [], 
            "level": 1, "reputation": 0, "compound_v": 0, "items": []
        }
        save_data()
    return players_data[user_id]

# --- ОБРАБОТЧИКИ ---
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🎰 Гача", "📦 Кейс Vought", "📝 Контракты", "👤 Профиль")
    bot.send_message(message.chat.id, "🏢 Vought International приветствует тебя!", reply_markup=markup)

@bot.message_handler(commands=['promo'])
def promo(message):
    args = message.text.split()
    if len(args) < 2: return
    code = args[1].upper()
    player = get_or_create_player(message.from_user.id)
    
    if code in PROMO_CODES and message.from_user.id not in PROMO_CODES[code]["claimed_by"]:
        data = PROMO_CODES[code]
        if data["reward_type"] == "vbucks": player["vbucks"] += data["amount"]
        else: player["compound_v"] += data["amount"]
        data["claimed_by"].append(message.from_user.id)
        save_data()
        bot.reply_to(message, "✅ Промокод активирован!")

# --- АДМИН-ПАНЕЛЬ ---
@bot.message_handler(commands=['give'])
def admin_give(message):
    if message.from_user.id != ADMIN_ID: return
    args = message.text.split()
    if len(args) < 4: return
    target_id, target_type, value = int(args[1]), args[2], args[3]
    player = get_or_create_player(target_id)
    if target_type == "money": player["vbucks"] += int(value)
    elif target_type == "char": player["inventory"].append(value)
    save_data()
    bot.reply_to(message, f"✅ Выдано {value} ({target_type}) игроку {target_id}")

# --- ОСНОВНЫЕ МЕХАНИКИ ---
@bot.message_handler(func=lambda m: m.text in ["🎰 Гача", "📦 Кейс Vought", "📝 Контракты", "👤 Профиль"])
def menu_handler(message):
    player = get_or_create_player(message.from_user.id)
    if message.text == "🎰 Гача":
        char = random.choice(list(CHARACTERS.keys()))
        player["inventory"].append(char)
        bot.send_message(message.chat.id, f"🎉 Тебе выпал: **{char}**!")
    elif message.text == "📦 Кейс Vought":
        if player["vbucks"] >= 200:
            player["vbucks"] -= 200
            char = random.choice(list(CHARACTERS.keys()))
            player["inventory"].append(char)
            bot.send_message(message.chat.id, f"🎁 Кейс открыт! Тебе выпал: {char}")
    elif message.text == "👤 Профиль":
        bot.send_message(message.chat.id, f"💰 Баланс: {player['vbucks']} VB\n🃏 Карт: {len(player['inventory'])}")
    save_data()

# --- ЗАПУСК ---
if __name__ == '__main__':
    load_data()
    Thread(target=lambda: Flask('').run(host='0.0.0.0', port=8080)).start()
    bot.infinity_polling()
