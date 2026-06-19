import os
import random
import json
import time
from threading import Thread
from difflib import get_close_matches
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
    "Неуязвимый": {"rarity": "🔮 Секретный", "price": 9999}, "Homelander": {"rarity": "⭐ Легендарный", "price": 500},
    "Soldier Boy": {"rarity": "⭐ Легендарный", "price": 500}, "Starlight": {"rarity": "✨ Эпический", "price": 300},
    "A-Train": {"rarity": "🔹 Редкий", "price": 150}, "The Deep": {"rarity": "🟢 Обычный", "price": 50},
    "Black Noir": {"rarity": "✨ Эпический", "price": 300}, "Queen Maeve": {"rarity": "✨ Эпический", "price": 300},
    "William Butcher": {"rarity": "⭐ Легендарный", "price": 500}, "Frenchie": {"rarity": "🔹 Редкий", "price": 150},
    "Kimiko": {"rarity": "🔹 Редкий", "price": 150}, "Hughie": {"rarity": "🟢 Обычный", "price": 50}
}

OUTFITS = {
    "🎀 Костюм горничной": {"buff": "Удача +10%, гача -45м, скидка 15%"},
    "👗 Костюм Старлайт": {"buff": "Кулдаун гачи -1 час"},
    "🧥 Плащ Бутчера": {"buff": "Ежедневка +100 VB"},
    "🧢 Кепка Vought": {"buff": "Базовый"},
    "⚔️ Костюм Солдатика": {"buff": "Шанс редких +5%"},
    "🕶️ Очки Блэк Нуара": {"buff": "Скидка на героев 10%"},
    "🔱 Костюм Подводного": {"buff": "+50 VB при крутке"},
    "⚡ Костюм Поезда-А": {"buff": "Кулдаун гачи -15 мин"},
    "🔥 Костюм Штормфронт": {"buff": "Ежедневка +20%"},
    "🦸‍♂️ Костюм Хоумлендера": {"buff": "Удача на легендарки +15%"}
}

BOOSTS = {
    "⚡ Ускоритель гачи (1ч)": {"price": 100, "duration": 3600, "type": "gacha_speed"},
    "🍀 Зелье удачи (30м)": {"price": 200, "duration": 1800, "type": "luck_boost"}
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
            "last_gacha": 0, "last_bonus": 0, "last_outfit_gacha": 0, "active_boosts": {}
        }
    return players_data[user_id]

def get_time_left(seconds):
    h, m = int(seconds // 3600), int((seconds % 3600) // 60)
    return f"{h} ч. {m} мин."

# --- ОБРАБОТЧИКИ ---
@bot.message_handler(commands=['start', 'equip'])
def handle_commands(message):
    if message.text.startswith('/equip'):
        player = get_player(message.from_user.id)
        user_input = message.text.replace('/equip', '').strip()
        matches = get_close_matches(user_input, player["outfits"], n=1, cutoff=0.3)
        if matches:
            player["equipped"] = matches[0]
            save_data()
            bot.send_message(message.chat.id, f"✅ **Костюм применен:** `{matches[0]}`")
        else:
            bot.send_message(message.chat.id, "❌ Костюм не найден в инвентаре.")
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("🎰 Гача героев", "👗 Гача костюмов", "🏪 Магазин бустов", "🎁 Ежедневка", "👤 Мой Профиль")
        bot.send_message(message.chat.id, "🏢 **Vought International: Система активна.**", parse_mode="Markdown", reply_markup=markup)

@bot.message_handler(func=lambda m: True)
def handle_text(message):
    player = get_player(message.from_user.id)
    
    if message.text == "🎁 Ежедневка":
        if time.time() - player["last_bonus"] >= 86400:
            bonus = 250 + (100 if player["equipped"] == "🧥 Плащ Бутчера" else 0)
            bonus += int(bonus * 0.20) if player["equipped"] == "🔥 Костюм Штормфронт" else 0
            player["vbucks"] += bonus
            player["last_bonus"] = time.time()
            save_data()
            bot.send_message(message.chat.id, f"✅ **Бонус:** +{bonus} VB!")
        else:
            bot.send_message(message.chat.id, f"❌ Рано! До бонуса: `{get_time_left(86400 - (time.time() - player['last_bonus']))}`", parse_mode="Markdown")

    elif message.text == "🎰 Гача героев":
        cooldown = 10800
        if player["equipped"] == "👗 Костюм Старлайт": cooldown = 7200
        elif player["equipped"] == "🎀 Костюм горничной": cooldown = 8100
        elif player["equipped"] == "⚡ Костюм Поезда-А": cooldown -= 900
        
        diff = time.time() - player["last_gacha"]
        if diff >= cooldown:
            char = random.choice(list(CHARACTERS.keys()))
            player["inventory"].append(char)
            player["last_gacha"] = time.time()
            save_data()
            bot.send_message(message.chat.id, f"🎰 **Выпал:** **{char}**\n💎 Редкость: `{CHARACTERS[char]['rarity']}`", parse_mode="Markdown")
        else:
            bot.send_message(message.chat.id, f"⏳ **Перегрузка:** ждать `{get_time_left(cooldown - diff)}`", parse_mode="Markdown")

    elif message.text == "👗 Гача костюмов":
        cost = int(300 * 0.85) if player["equipped"] == "🎀 Костюм горничной" else 300
        if time.time() - player.get("last_outfit_gacha", 0) >= 7200:
            if player["vbucks"] >= cost:
                player["vbucks"] -= cost
                player["last_outfit_gacha"] = time.time()
                outfit = random.choice(list(OUTFITS.keys()))
                player["outfits"].append(outfit)
                save_data()
                bot.send_message(message.chat.id, f"👗 **Вы получили:** {outfit}!")
            else:
                bot.send_message(message.chat.id, "❌ Недостаточно средств.")
        else:
            bot.send_message(message.chat.id, f"⏳ **Занято:** ждать `{get_time_left(7200 - (time.time() - player.get('last_outfit_gacha', 0)))}`", parse_mode="Markdown")

    elif message.text == "🏪 Магазин бустов":
        text = "🏪 **Бусты:**\n" + "\n".join([f"• `{k}` — {v['price']} VB" for k, v in BOOSTS.items()])
        bot.send_message(message.chat.id, text + "\n💡 `/buy [Название]`", parse_mode="Markdown")

    elif message.text.startswith("/buy "):
        b_name = message.text.replace("/buy ", "").strip()
        matches = get_close_matches(b_name, list(BOOSTS.keys()))
        if matches:
            b = BOOSTS[matches[0]]
            if player["vbucks"] >= b["price"]:
                player["vbucks"] -= b["price"]
                player["active_boosts"][matches[0]] = time.time() + b["duration"]
                save_data()
                bot.send_message(message.chat.id, f"✅ Куплен: {matches[0]}")
            else: bot.send_message(message.chat.id, "❌ Недостаточно средств.")

    elif message.text == "👤 Мой Профиль":
        inv = ", ".join(list(set(player["inventory"]))[:10])
        boosts = "\n".join([f"• {b}" for b, t in player.get("active_boosts", {}).items() if t > time.time()])
        text = f"👤 **Профиль**\n💰 VB: `{player['vbucks']}`\n👗 Костюм: `{player['equipped'] or 'Нет'}`\n\n🃏 **Коллекция:** {inv}...\n✨ **Бусты:**\n{boosts or 'Нет'}"
        bot.send_message(message.chat.id, text, parse_mode="Markdown")

if __name__ == '__main__':
    load_data()
    Thread(target=lambda: Flask('').run(host='0.0.0.0', port=8080)).start()
    bot.infinity_polling()
