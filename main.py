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

# --- БАЗЫ ДАННЫХ ---
CHARACTERS = {
    "Неуязвимый": {"rarity": "🔮 Секретный", "price": 9999},
    "Homelander": {"rarity": "⭐ Легендарный", "price": 500},
    "Soldier Boy": {"rarity": "⭐ Легендарный", "price": 500},
    "Starlight": {"rarity": "✨ Эпический", "price": 300},
    "A-Train": {"rarity": "🔹 Редкий", "price": 150},
    "Black Noir": {"rarity": "✨ Эпический", "price": 300},
    "William Butcher": {"rarity": "⭐ Легендарный", "price": 500},
    "Stormfront": {"rarity": "⭐ Легендарный", "price": 500},
    "The Deep": {"rarity": "🟢 Обычный", "price": 50}
    # (добавьте остальных героев по аналогии)
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

# --- ОБРАБОТЧИКИ ---
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🎰 Гача героев", "👗 Гача костюмов", "🎁 Ежедневка")
    markup.add("👤 Мой Профиль")
    bot.send_message(message.chat.id, "🏢 **Vought International: Система активна.**\nДобро пожаловать, сотрудник.", parse_mode="Markdown", reply_markup=markup)

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
    
    if message.text == "🎰 Гача героев":
        cooldown = 7200 if player["equipped"] == "👗 Костюм Старлайт" else 10800
        if time.time() - player["last_gacha"] >= cooldown:
            char = random.choice(list(CHARACTERS.keys()))
            player["inventory"].append(char)
            player["last_gacha"] = time.time()
            save_data()
            bot.send_message(message.chat.id, f"🎰 **Vought запускает конвейер!**\n\n🎉 Тебе выпадает: **{char}**\n💎 Редкость: `{CHARACTERS[char]['rarity']}`", parse_mode="Markdown")
        else:
            bot.send_message(message.chat.id, "⏳ **Конвейер Vought перегружен!**\nПопробуйте позже.", parse_mode="Markdown")

    elif message.text == "👗 Гача костюмов":
        if time.time() - player.get("last_outfit_gacha", 0) >= 7200:
            if player["vbucks"] >= 300:
                player["vbucks"] -= 300
                player["last_outfit_gacha"] = time.time()
                outfit = random.choice(list(OUTFITS.keys()))
                player["outfits"].append(outfit)
                save_data()
                bot.send_message(message.chat.id, f"👗 **Vought Fashion:**\nВы получили: **{outfit}**!", parse_mode="Markdown")
            else:
                bot.send_message(message.chat.id, "❌ **Недостаточно средств!**")
        else:
            bot.send_message(message.chat.id, "⏳ **Конвейер моды на техобслуживании!**", parse_mode="Markdown")

    elif message.text == "👤 Мой Профиль":
        inv = "\n".join([f"• {c}" for c in set(player["inventory"])])
        text = (
            f"👤 **Личное дело сотрудника Vought**\n\n"
            f"💰 Баланс: `{player['vbucks']} V-Bucks`\n"
            f"👗 Надет: `{player['equipped'] or 'Нет'}`\n\n"
            f"🃏 **Коллекция:**\n{inv if inv else 'Пусто'}\n"
            f"💡 *Чтобы надеть костюм: /equip Название*"
        )
        bot.send_message(message.chat.id, text, parse_mode="Markdown")

if __name__ == '__main__':
    load_data()
    Thread(target=lambda: Flask('').run(host='0.0.0.0', port=8080)).start()
    bot.infinity_polling()
