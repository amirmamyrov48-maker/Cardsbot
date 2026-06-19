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

# --- ПОЛНАЯ БАЗА ---
CHARACTERS = {
    "Неуязвимый": {"rarity": "🔮 Секретный", "price": 9999}, "Homelander": {"rarity": "⭐ Легендарный", "price": 500},
    "Soldier Boy": {"rarity": "⭐ Легендарный", "price": 500}, "Starlight": {"rarity": "✨ Эпический", "price": 300},
    "A-Train": {"rarity": "🔹 Редкий", "price": 150}, "The Deep": {"rarity": "🟢 Обычный", "price": 50},
    "Black Noir": {"rarity": "✨ Эпический", "price": 300}, "Queen Maeve": {"rarity": "✨ Эпический", "price": 300},
    "William Butcher": {"rarity": "⭐ Легендарный", "price": 500}, "Frenchie": {"rarity": "🔹 Редкий", "price": 150},
    "Kimiko": {"rarity": "🔹 Редкий", "price": 150}, "Hughie": {"rarity": "🟢 Обычный", "price": 50},
    "Mother's Milk": {"rarity": "🔹 Редкий", "price": 150}, "Stormfront": {"rarity": "⭐ Легендарный", "price": 500}
}

OUTFITS = {
    "🎀 Костюм горничной": {"rarity": "🔮 Мифический", "buff": "Удача +10%, кулдаун -45м, скидка 15%"},
    "👗 Костюм Старлайт": {"rarity": "✨ Эпический", "buff": "Снижает кулдаун гачи на 1 час"},
    "🧥 Плащ Бутчера": {"rarity": "🔹 Редкий", "buff": "Бонус к ежедневке +100 VB"},
    "🧢 Кепка Vought": {"rarity": "🟢 Обычный", "buff": "Стиль +1"}
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
        players_data[user_id] = {
            "vbucks": 1000, "inventory": [], "outfits": [], "equipped": None, 
            "last_gacha": 0, "last_bonus": 0, "last_outfit_gacha": 0
        }
    return players_data[user_id]

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🎰 Гача героев", "👗 Гача костюмов", "🎁 Ежедневка")
    markup.add("👤 Мой Профиль")
    bot.send_message(message.chat.id, "🏢 **Vought International: Система активна.**", parse_mode="Markdown", reply_markup=markup)

@bot.message_handler(commands=['equip'])
def equip(message):
    player = get_player(message.from_user.id)
    outfit = message.text.replace('/equip ', '').strip()
    if outfit in player["outfits"]:
        player["equipped"] = outfit
        save_data()
        bot.send_message(message.chat.id, f"✅ **Костюм применен:** `{outfit}`", parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, "❌ **Ошибка:** У вас нет такого костюма.")

@bot.message_handler(func=lambda m: True)
def handle_text(message):
    player = get_player(message.from_user.id)
    
    # 1. ЕЖЕДНЕВКА (исправлено)
    if message.text == "🎁 Ежедневка":
        if time.time() - player["last_bonus"] >= 86400:
            bonus = 350 if player["equipped"] == "🧥 Плащ Бутчера" else 250
            player["vbucks"] += bonus
            player["last_bonus"] = time.time()
            save_data()
            bot.send_message(message.chat.id, f"✅ **Бонус получен:** {bonus} V-Bucks!")
        else:
            remaining = 86400 - (time.time() - player["last_bonus"])
            h = int(remaining // 3600)
            bot.send_message(message.chat.id, f"❌ **Рано!** Возвращайтесь через {h} ч.")

    # 2. ГАЧА ГЕРОЕВ
    elif message.text == "🎰 Гача героев":
        cooldown = 7200 if player["equipped"] == "👗 Костюм Старлайт" else 10800
        if player["equipped"] == "🎀 Костюм горничной": cooldown -= 2700
        
        if time.time() - player["last_gacha"] >= cooldown:
            char = random.choice(list(CHARACTERS.keys()))
            player["inventory"].append(char)
            player["last_gacha"] = time.time()
            save_data()
            bot.send_message(message.chat.id, f"🎰 **Vought запускает конвейер!**\n\n🎉 Выпал: **{char}**", parse_mode="Markdown")
        else:
            bot.send_message(message.chat.id, "⏳ **Конвейер Vought перегружен!**")

    # 3. ГАЧА КОСТЮМОВ
    elif message.text == "👗 Гача костюмов":
        cost = int(300 * 0.85) if player["equipped"] == "🎀 Костюм горничной" else 300
        if time.time() - player.get("last_outfit_gacha", 0) >= 7200:
            if player["vbucks"] >= cost:
                player["vbucks"] -= cost
                player["last_outfit_gacha"] = time.time()
                outfit = random.choice(list(OUTFITS.keys()))
                player["outfits"].append(outfit)
                save_data()
                bot.send_message(message.chat.id, f"👗 **Vought Fashion:**\nВы получили: **{outfit}**!", parse_mode="Markdown")
            else:
                bot.send_message(message.chat.id, f"❌ **Недостаточно средств!** Нужно {cost} VB.")
        else:
            bot.send_message(message.chat.id, "⏳ **Конвейер моды на техобслуживании!**")

    # 4. ПРОФИЛЬ
    elif message.text == "👤 Мой Профиль":
        inv = "\n".join([f"• {c}" for c in set(player["inventory"])])
        text = (f"👤 **Личное дело сотрудника Vought**\n\n"
                f"💰 Баланс: `{player['vbucks']} V-Bucks`\n"
                f"👗 Надет: `{player['equipped'] or 'Нет'}`\n\n"
                f"🃏 **Коллекция:**\n{inv if inv else 'Пусто'}")
        bot.send_message(message.chat.id, text, parse_mode="Markdown")

if __name__ == '__main__':
    load_data()
    Thread(target=lambda: Flask('').run(host='0.0.0.0', port=8080)).start()
    bot.infinity_polling()
