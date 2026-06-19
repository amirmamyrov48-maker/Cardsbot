import os
import random
import time
import json
from threading import Thread
from telebot import types
import telebot
from flask import Flask

# --- 1. НАСТРОЙКА БОТА И ПЕРЕМЕННЫХ ---
TOKEN = os.environ.get('BOT_TOKEN') or 'ТВОЙ_ТОКЕН_ОТ_BOTFATHER'
bot = telebot.TeleBot(TOKEN)

COOLDOWN_TIME = 10800  # Стандартный кулдаун: 3 часа

# Путь к простому JSON-файлу
DB_FILE = "players_backup.json"

# Сюда будут загружаться данные
players_data = {}

# 🃏 БАЗА ДАННЫХ ПЕРСОНАЖЕЙ
CHARACTERS = {
    "Homelander": {"rarity": "⭐ Легендарный", "price": 500, "url": "https://images.unsplash.com/photo-1620336655055-088d06e36bf0?q=80&w=500"},
    "William Butcher": {"rarity": "⭐ Легендарный", "price": 500, "url": "https://images.unsplash.com/photo-1559893088-c0787ebfc084?q=80&w=500"},
    "Soldier Boy": {"rarity": "⭐ Легендарный", "price": 500, "url": "https://images.unsplash.com/photo-1569003339405-ea396a5a8a90?q=80&w=500"},
    "Ryan Butcher": {"rarity": "⭐ Легендарный", "price": 500, "url": "https://images.unsplash.com/photo-1608889174637-3c44f6326f20?q=80&w=500"},
    "Mind-Storm": {"rarity": "⭐ Легендарный", "price": 500, "url": "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?q=80&w=500"},
    "Stan Edgar": {"rarity": "⭐ Легендарный", "price": 500, "url": "https://images.unsplash.com/photo-1507679799987-c73779587ccf?q=80&w=500"},
    "Starlight": {"rarity": "✨ Эпический", "price": 300, "url": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?q=80&w=500"},
    "Queen Maeve": {"rarity": "✨ Эпический", "price": 300, "url": "https://images.unsplash.com/photo-1579783902614-a3fb3927b6a5?q=80&w=500"},
    "Black Noir": {"rarity": "✨ Эпический", "price": 300, "url": "https://images.unsplash.com/photo-1509248961158-e54f6934749c?q=80&w=500"},
    "Victoria Neuman": {"rarity": "✨ Эпический", "price": 300, "url": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?q=80&w=500"},
    "Sister Sage": {"rarity": "✨ Эпический", "price": 300, "url": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?q=80&w=500"},
    "Firecracker": {"rarity": "✨ Эпический", "price": 300, "url": "https://images.unsplash.com/photo-1614613535308-eb5fbd3d2c17?q=80&w=500"},
    "Lamplighter": {"rarity": "✨ Эпический", "price": 300, "url": "https://images.unsplash.com/photo-1595062584113-e09a3fc9a9a3?q=80&w=500"},
    "Tek-Knight": {"rarity": "✨ Эпический", "price": 300, "url": "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?q=80&w=500"},
    "A-Train": {"rarity": "🔹 Редкий", "price": 150, "url": "https://images.unsplash.com/photo-1476480862126-209bfaa8edc8?q=80&w=500"},
    "Kimiko Miyashiro": {"rarity": "🔹 Редкий", "price": 150, "url": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?q=80&w=500"},
    "Mother's Milk": {"rarity": "🔹 Редкий", "price": 150, "url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?q=80&w=500"},
    "Frenchie": {"rarity": "🔹 Редкий", "price": 150, "url": "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?q=80&w=500"},
    "Stormfront": {"rarity": "🔹 Редкий", "price": 150, "url": "https://images.unsplash.com/photo-1614850523459-c2f4c699c52e?q=80&w=500"},
    "Translucent": {"rarity": "🔹 Редкий", "price": 150, "url": "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?q=80&w=500"},
    "Gunpowder": {"rarity": "🔹 Редкий", "price": 150, "url": "https://images.unsplash.com/photo-1591115765373-520b7098f6db?q=80&w=500"},
    "Termite": {"rarity": "🔹 Редкий", "price": 150, "url": "https://images.unsplash.com/photo-1601049676099-e7ed07d825b0?q=80&w=500"},
    "Blindspot": {"rarity": "🔹 Редкий", "price": 150, "url": "https://images.unsplash.com/photo-1509967419530-da38b4704bc6?q=80&w=500"},
    "The Deep": {"rarity": "🟢 Обычный", "price": 50, "url": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?q=80&w=500"},
    "Hughie Campbell": {"rarity": "🟢 Обычный", "price": 50, "url": "https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?q=80&w=500"},
    "Todd": {"rarity": "🟢 Обычный", "price": 50, "url": "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?q=80&w=500"},
    "Popclaw": {"rarity": "🟢 Обычный", "price": 50, "url": "https://images.unsplash.com/photo-1619380061814-58f03707f082?q=80&w=500"},
    "Mesmer": {"rarity": "🟢 Обычный", "price": 50, "url": "https://images.unsplash.com/photo-1552058544-f2b08422138a?q=80&w=500"},
    "Lovebird": {"rarity": "🟢 Обычный", "price": 50, "url": "https://images.unsplash.com/photo-1524504388940-b1c1722653e1?q=80&w=500"},
    "Supersonic": {"rarity": "🟢 Обычный", "price": 50, "url": "https://images.unsplash.com/photo-1481214110143-ed630356e1bb?q=80&w=500"},
    "Hugh Campbell Sr.": {"rarity": "🟢 Обычный", "price": 50, "url": "https://images.unsplash.com/photo-1492562080023-ab3db95bfbce?q=80&w=500"},
    "Ashley Barrett": {"rarity": "🟢 Обычный", "price": 50, "url": "https://images.unsplash.com/photo-1548142813-c348350df52b?q=80&w=500"}
}

SHOP_ITEMS = {
    "compound_v": {"name": "🧪 Препарат V", "price": 500, "desc": "Обнуляет кулдаун конвейера гачи."},
    "homelander_milk": {"name": "🥛 Молоко Хоумлендера", "price": 150, "desc": "Бафф удачи!"},
    "timothy": {"name": "🐙 Осьминог Тимоти", "price": 250, "desc": "Питомец."},
    "atrain_energy": {"name": "👊 Энергетик A-Train", "price": 400, "desc": "Снижает кулдаун гачи."}
}

# --- 1.1 ФУНКЦИИ ДЛЯ РАБОТЫ С ФАЙЛОМ JSON ---
def load_data():
    global players_data
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                # Превращаем ключи обратно в числа (id пользователей)
                string_data = json.load(f)
                players_data = {int(k): v for k, v in string_data.items()}
                print("Данные успешно загружены!")
        except Exception as e:
            print(f"Ошибка загрузки данных: {e}")
            players_data = {}
    else:
        players_data = {}

def save_data():
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(players_data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Ошибка при сохранении данных: {e}")

def get_or_create_player(user_id, username="Аноним"):
    if user_id not in players_data:
        players_data[user_id] = {
            "username": username,
            "vbucks": 0,
            "inventory": [],
            "items": [],            
            "compound_v": 0,    
            "last_gacha_time": 0,
            "speed_charges": 0,      
            "has_milk_buff": False   
        }
        save_data()
    else:
        if username and username != "Аноним":
            players_data[user_id]["username"] = username
    return players_data[user_id]

# --- 2. ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ГАЧИ ---
def give_gacha_reward(message, player):
    if player.get("has_milk_buff", False):
        filtered_chars = {k: v for k, v in CHARACTERS.items() if "🟢 Обычный" not in v["rarity"]}
        char_name = random.choice(list(filtered_chars.keys()))
        player["has_milk_buff"] = False  
        bonus_text = "🥛 **Эффект молока сработал!**\n"
    else:
        char_name = random.choice(list(CHARACTERS.keys()))
        bonus_text = ""
        
    char_info = CHARACTERS[char_name]
    player["inventory"].append(char_name)
    
    charge_text = ""
    if player.get("speed_charges", 0) > 0:
        player["speed_charges"] -= 1
        charge_text = f"👊 *Потрачен 1 заряд суперскорости А-Трэйна.*\n"
        
    sell_price = char_info['price']
    if char_name == "The Deep" and "timothy" in player.get("items", []):
        sell_price = 100
        
    response = (
        f"🎰 **Воугт запускает конвейер!**\n\n"
        f"{bonus_text}{charge_text}"
        f"🎉 Персонаж: **{char_name}**\n"
        f"💎 Редкость: `{char_info['rarity']}`\n"
        f"💰 Цена продажи: {sell_price} V-Bucks\n\n"
        f"🃏 Карточка добавлена!"
    )
    
    save_data() # Сохраняем в файл после крутки
    
    try:
        bot.send_photo(message.chat.id, char_info["url"], caption=response, parse_mode="Markdown")
    except Exception as e:
        bot.send_message(message.chat.id, response + "\n\n⚠️ (Ошибка изображения)", parse_mode="Markdown")

def send_profile_message(chat_id, player):
    vbucks = player["vbucks"]
    comp_v = player.get("compound_v", 0)
    speed_charges = player.get("speed_charges", 0)
    
    if player["inventory"]:
        counts = {}
        for card in player["inventory"]:
            counts[card] = counts.get(card, 0) + 1
        cards_text = "\n".join([f"• {name} x{count}" for name, count in counts.items()])
    else:
        cards_text = "У тебя пока нет карточек."
        
    items_list = []
    if comp_v > 0: items_list.append(f"🧪 Препарат V ({comp_v} шт.)")
    if player.get("has_milk_buff", False): items_list.append("🥛 Молоко Хоумлендера")
    if "timothy" in player.get("items", []): items_list.append("🐙 Осьминог Тимоти")
    if speed_charges > 0: items_list.append(f"👊 Зарядов скорости: {speed_charges}")
        
    items_text = "\n".join([f"• {i}" for i in items_list]) if items_list else "Пусто"
        
    text = (
        f"👤 **Личное дело сотрудника Vought**\n\n"
        f"💰 **Баланс:** {vbucks} V-Bucks\n\n"
        f"⚙️ **Твоё снаряжение:**\n{items_text}\n\n"
        f"🃏 **Твоя коллекция:**\n{cards_text}\n\n"
        f"💡 *Чтобы продать карты, нажми кнопку ниже или введи:* `/sell`"
    )
    bot.send_message(chat_id, text, parse_mode="Markdown")

# --- 3. ОБРАБОТКА КОМАНД ---

@bot.message_handler(commands=['start'])
def send_welcome(message):
    name = message.from_user.first_name or "Сотрудник"
    get_or_create_player(message.from_user.id, username=name)
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("🎰 Крутить Гачу"), types.KeyboardButton("👤 Мой Профиль Vought"))
    markup.add(types.KeyboardButton("🏪 Магазин Vought"), types.KeyboardButton("📊 Топ Олигархов Vought"))
    
    text = (
        "👋 Приветствуем в Vought International!\n\n"
        "Выбивай карточки суперов, покупай апгрейды и попади в топ самых богатых игроков!\n"
        "Используй меню ниже 👇"
    )
    bot.send_message(message.chat.id, text, reply_markup=markup)

# СЕКРЕТНАЯ КОМАНДА ДЛЯ АДМИНА — СКАЧАТЬ БЭКАП БАЗЫ ДАННЫХ В ЛЮБОЙ МОМЕНТ
@bot.message_handler(commands=['download_db'])
def download_db(message):
    # Замени цифру ниже на свой реальный ID в Телеграме, чтобы никто другой не мог скачать данные!
    if message.from_user.id == message.from_user.id: # Сюда можно вписать свой ID
        save_data()
        if os.path.exists(DB_FILE):
            with open(DB_FILE, "rb") as f:
                bot.send_document(message.chat.id, f, caption="📦 Актуальный бэкап игроков бота.")
        else:
            bot.send_message(message.chat.id, "Файл базы данных ещё не создан.")

@bot.message_handler(commands=['profile'])
def command_profile(message):
    name = message.from_user.first_name or "Сотрудник"
    player = get_or_create_player(message.from_user.id, username=name)
    send_profile_message(message.chat.id, player)

@bot.message_handler(commands=['top'])
def command_top(message):
    if not players_data:
        bot.send_message(message.chat.id, "📊 Список лидеров пуст.")
        return

    sorted_players = sorted(players_data.items(), key=lambda x: x[1].get("vbucks", 0), reverse=True)
    leaderboard = []
    for index, (user_id, data) in enumerate(sorted_players[:10]):
        username = data.get("username", "Аноним")
        balance = data.get("vbucks", 0)
        
        if index == 0: medal = "🥇"
        elif index == 1: medal = "🥈"
        elif index == 2: medal = "🥉"
        else: medal = f"{index + 1}."
            
        leaderboard.append(f"{medal} **{username}** — `{balance}` VB")
        
    response = "📊 **Топ-10 Самых Богатых Людей Vought**\n\n" + "\n".join(leaderboard)
    bot.send_message(message.chat.id, response, parse_mode="Markdown")

@bot.message_handler(commands=['sell'])
def sell_menu(message):
    # Исправляем ручной ввод: теперь команда /sell выводит удобные инлайн-кнопки
    name = message.from_user.first_name or "Сотрудник"
    player = get_or_create_player(message.from_user.id, username=name)
    if not player["inventory"]:
        bot.send_message(message.chat.id, "❌ Твой инвентарь пуст!")
        return
        
    counts = {}
    for card in player["inventory"]:
        counts[card] = counts.get(card, 0) + 1
        
    markup = types.InlineKeyboardMarkup()
    for card_name, count in counts.items():
        price = 100 if card_name == "The Deep" and "timothy" in player.get("items", []) else CHARACTERS[card_name]["price"]
        btn = types.InlineKeyboardButton(text=f"❌ {card_name} (x{count}) — {price} VB", callback_data=f"sell_{card_name}")
        markup.add(btn)
        
    bot.send_message(message.chat.id, "💵 **Аукцион Vought**\nНажми на карту на кнопке, чтобы её продать:", reply_markup=markup)

@bot.message_handler(content_types=['text'])
def handle_menu(message):
    name = message.from_user.first_name or "Сотрудник"
    player = get_or_create_player(message.from_user.id, username=name)
    
    if message.text == "🎰 Крутить Гачу":
        current_time = time.time()
        time_passed = current_time - player["last_gacha_time"]
        actual_cooldown = 3600 if player.get("speed_charges", 0) > 0 else COOLDOWN_TIME
        
        if time_passed < actual_cooldown:
            time_left = int(actual_cooldown - time_passed)
            minutes = (time_left % 3600) // 60
            bot.send_message(message.chat.id, f"⏳ **Конвейер Vought перегружен!**\nПопробуй через **{minutes} мин.**")
            return
            
        player["last_gacha_time"] = current_time
        give_gacha_reward(message, player)
        
    elif message.text == "👤 Мой Профиль Vought":
        send_profile_message(message.chat.id, player)

    elif message.text == "📊 Топ Олигархов Vought":
        command_top(message)

    elif message.text == "🏪 Магазин Vought":
        markup = types.InlineKeyboardMarkup()
        for item_id, info in SHOP_ITEMS.items():
            markup.add(types.InlineKeyboardButton(text=f"{info['name']} — {info['price']} VB", callback_data=f"buy_{item_id}"))
        bot.send_message(message.chat.id, "🏪 **Добро пожаловать в Магазин Vought International!**", reply_markup=markup)

# --- 4. ОБРАБОТКА ИНЛАЙН КНОПОК ---
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    name = call.from_user.first_name or "Сотрудник"
    player = get_or_create_player(call.from_user.id, username=name)
    
    if call.data.startswith("sell_"):
        real_name = call.data.replace("sell_", "")
        if real_name not in player["inventory"]:
            bot.answer_callback_query(call.id, "❌ Карточки больше нет!")
            return
            
        price = 100 if real_name == "The Deep" and "timothy" in player.get("items", []) else CHARACTERS[real_name]["price"]
        player["inventory"].remove(real_name)
        player["vbucks"] += price
        bot.answer_callback_query(call.id, f"💵 +{price} V-Bucks!")
        save_data()
        
        # Обновляем инлайн-меню после продажи
        counts = {}
        for card in player["inventory"]: counts[card] = counts.get(card, 0) + 1
        if not player["inventory"]:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="💵 **Все карточки распроданы!**")
        else:
            new_markup = types.InlineKeyboardMarkup()
            for n, c in counts.items():
                p = 100 if n == "The Deep" and "timothy" in player.get("items", []) else CHARACTERS[n]["price"]
                new_markup.add(types.InlineKeyboardButton(text=f"❌ {n} (x{c}) — {p} VB", callback_data=f"sell_{n}"))
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"✅ Продан персонаж {real_name}!", reply_markup=new_markup)

    elif call.data.startswith("buy_"):
        item_id = call.data.replace("buy_", "")
        item_info = SHOP_ITEMS[item_id]
        
        if player["vbucks"] < item_info["price"]:
            bot.answer_callback_query(call.id, "❌ Не хватает V-Bucks!")
            return
            
        player["vbucks"] -= item_info["price"]
        if item_id == "compound_v": player["compound_v"] += 1
        elif item_id == "homelander_milk": player["has_milk_buff"] = True
        elif item_id == "atrain_energy": player["speed_charges"] = 2  
        elif item_id == "timothy": player["items"].append("timothy")
            
        save_data()
        bot.answer_callback_query(call.id, f"🛍️ Куплено: {item_info['name']}!")
        bot.send_message(call.message.chat.id, f"✅ Куплено: {item_info['name']}. Остаток: {player['vbucks']} VB.")

# --- 5. ВЕБ-СЕРВЕР ДЛЯ ПОДДЕРЖКИ ЖИЗНИ БОТА ---
app = Flask('')

@app.route('/')
def home():
    return "Бот активен и сохраняет игроков в JSON файл!"

def run():
    app.run(host='0.0.0.0', port=8080)

if __name__ == '__main__':
    load_data()  # Загружаем игроков из файла при запуске бота
    Thread(target=run).start()
    print("Бот Воут запущен...")
    bot.infinity_polling()
