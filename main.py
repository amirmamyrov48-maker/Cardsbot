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

# --- ПОЛНАЯ БАЗА ПЕРСОНАЖЕЙ ---
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

SHOP_ITEMS = {
    "V_Serum": {"name": "🧪 Сыворотка V", "price": 500},
    "Starlight_Suit": {"name": "👗 Костюм Старлайт", "price": 600},
    "Compound_V_Inject": {"name": "💉 Инъектор с Препаратом V", "price": 750}
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
        players_data[user_id] = {"vbucks": 1000, "inventory": [], "items": [], "last_bonus": 0, "last_gacha": 0}
    return players_data[user_id]

# --- ОБРАБОТЧИКИ ---
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🎰 Крутить Гачу", "🏪 Магазин", "🎁 Ежедневка")
    markup.add("👤 Мой Профиль")
    bot.send_message(message.chat.id, "🏢 Vought International: полный список персонажей загружен!", reply_markup=markup)

@bot.message_handler(func=lambda m: True)
def handle_text(message):
    player = get_player(message.from_user.id)
    
    if message.text == "🎰 Крутить Гачу":
        if time.time() - player["last_gacha"] >= 7200:
            char_name = random.choice(list(CHARACTERS.keys()))
            player["inventory"].append(char_name)
            player["last_gacha"] = time.time()
            save_data()
            bot.send_message(message.chat.id, f"🎉 Тебе выпал: **{char_name}**", parse_mode="Markdown")
        else:
            bot.send_message(message.chat.id, "⏳ Конвейер на перезарядке.")

    elif message.text == "🏪 Магазин":
        markup = types.InlineKeyboardMarkup()
        for i_id, info in SHOP_ITEMS.items():
            markup.add(types.InlineKeyboardButton(f"{info['name']} ({info['price']} VB)", callback_data=f"buy_{i_id}"))
        bot.send_message(message.chat.id, "🏪 Магазин товаров:", reply_markup=markup)

    elif message.text == "👤 Мой Профиль":
        markup = types.InlineKeyboardMarkup()
        if "👗 Костюм Старлайт" in player["items"]:
            markup.add(types.InlineKeyboardButton("👃 Понюхать костюм", callback_data="sniff_suit"))
        bot.send_message(message.chat.id, f"💰 Баланс: {player['vbucks']} VB\n🎒 Предметы: {', '.join(player['items']) if player['items'] else 'Пусто'}", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_"))
def buy_item(call):
    player = get_player(call.from_user.id)
    i_id = call.data.split("_")[1]
    item = SHOP_ITEMS[i_id]
    if player["vbucks"] >= item["price"]:
        player["vbucks"] -= item["price"]
        player["items"].append(item["name"])
        save_data()
        bot.answer_callback_query(call.id, "✅ Куплено!")
    else:
        bot.answer_callback_query(call.id, "❌ Недостаточно средств!")

@bot.callback_query_handler(func=lambda call: call.data == "sniff_suit")
def sniff_suit(call):
    bot.answer_callback_query(call.id, "👃 Пахнет героиней и справедливостью!")

if __name__ == '__main__':
    load_data()
    Thread(target=lambda: Flask('').run(host='0.0.0.0', port=8080)).start()
    bot.infinity_polling()
