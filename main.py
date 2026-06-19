import os
import random
import time
from threading import Thread
import telebot
from telebot import types
from flask import Flask

# --- 1. НАСТРОЙКА БОТА И ПЕРЕМЕННЫХ ---
TOKEN = os.environ.get('BOT_TOKEN') or 'ТВОЙ_ТОКЕН_ОТ_BOTFATHER'
bot = telebot.TeleBot(TOKEN)

# Настройка кулдауна (3 часа = 10800 секунд)
COOLDOWN_TIME = 10800
COMPOUND_V_PRICE = 500

# Расширенная база данных персонажей из «Пацанов»
CHARACTERS = {
    # ⭐ Легендарные
    "Homelander": {"rarity": "⭐ Легендарный", "price": 500},
    "Soldier Boy": {"rarity": "⭐ Легендарный", "price": 500},
    "William Butcher": {"rarity": "⭐ Легендарный", "price": 500},
    
    # ✨ Эпические
    "Starlight": {"rarity": "✨ Эпический", "price": 300},
    "Queen Maeve": {"rarity": "✨ Эпический", "price": 300},
    "Black Noir": {"rarity": "✨ Эпический", "price": 300},
    "Victoria Neuman": {"rarity": "✨ Эпический", "price": 300},
    
    # 🔹 Редкие
    "A-Train": {"rarity": "🔹 Редкий", "price": 150},
    "Kimiko Miyashiro": {"rarity": "🔹 Редкий", "price": 150},
    "Mother's Milk": {"rarity": "🔹 Редкий", "price": 150},
    "Stormfront": {"rarity": "🔹 Редкий", "price": 150},
    "Translucent": {"rarity": "🔹 Редкий", "price": 150},
    
    # 🟢 Обычные
    "The Deep": {"rarity": "🟢 Обычный", "price": 50},
    "Hughie Campbell": {"rarity": "🟢 Обычный", "price": 50},
    "Frenchie": {"rarity": "🟢 Обычный", "price": 50},
    "Todd": {"rarity": "🟢 Обычный", "price": 50}
}

# Внутренняя база данных игроков (в памяти сервера)
players_data = {}

def get_or_create_player(user_id):
    if user_id not in players_data:
        players_data[user_id] = {
            "vbucks": 0,
            "inventory": [],
            "compound_v": 0,    
            "last_gacha_time": 0  
        }
    return players_data[user_id]


# --- 2. ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ГАЧИ ---
def give_gacha_reward(message, player):
    """Внутренняя функция для выдачи персонажа"""
    char_name = random.choice(list(CHARACTERS.keys()))
    char_info = CHARACTERS[char_name]
    
    player["inventory"].append(char_name)
    
    response = (
        f"🎰 **Воугт запускает конвейер!**\n\n"
        f"🎉 Тебе выпадает персонаж: **{char_name}**\n"
        f"💎 Редкость: `{char_info['rarity']}`\n"
        f"💰 Цена продажи: {char_info['price']} V-Bucks\n\n"
        f"🃏 Карточка добавлена в твой профиль!"
    )
    bot.send_message(message.chat.id, response, parse_mode="Markdown")


def send_profile_message(chat_id, player):
    """Внутренняя функция для сборки и отправки профиля"""
    vbucks = player["vbucks"]
    comp_v = player.get("compound_v", 0)
    
    if player["inventory"]:
        counts = {}
        for card in player["inventory"]:
            counts[card] = counts.get(card, 0) + 1
        cards_text = "\n".join([f"• {name} x{count}" for name, count in counts.items()])
    else:
        cards_text = "У тебя пока нет карточек."
        
    text = (
        f"👤 **Личное дело сотрудника Vought**\n\n"
        f"💰 **Баланс:** {vbucks} V-Bucks\n"
        f"🧪 **Запасы Препарата V:** {comp_v} шт.\n\n"
        f"🃏 **Твоя коллекция:**\n{cards_text}\n\n"
        f"💡 *Чтобы продать карту, напиши:* `/sell Имя`"
    )
    bot.send_message(chat_id, text, parse_mode="Markdown")


# --- 3. ОБРАБОТКА КОМАНД И КНОПОК ---

# Главное меню при старте
@bot.message_handler(commands=['start'])
def send_welcome(message):
    get_or_create_player(message.from_user.id)
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_gacha = types.KeyboardButton("🎰 Крутить Гачу")
    btn_profile = types.KeyboardButton("👤 Мой Профиль Vought")
    btn_shop = types.KeyboardButton("🧪 Купить Препарат V (500 VB)")
    markup.add(btn_gacha, btn_profile)
    markup.add(btn_shop)
    
    text = (
        "👋 Приветствуем в Vought International!\n\n"
        "Здесь ты можешь выбивать карточки суперов и членов отряда «Пацанов», "
        "копить их или продавать за V-Bucks корпорации!\n\n"
        "Используй кнопки ниже для управления 👇"
    )
    bot.send_message(message.chat.id, text, reply_markup=markup)


# Команда просмотра профиля текстом (/profile)
@bot.message_handler(commands=['profile'])
def command_profile(message):
    player = get_or_create_player(message.from_user.id)
    send_profile_message(message.chat.id, player)


# Обработка текстовых кнопок меню
@bot.message_handler(content_types=['text'])
def handle_menu(message):
    player = get_or_create_player(message.from_user.id)
    
    # КРУТИТЬ ГАЧУ
    if message.text == "🎰 Крутить Гачу":
        current_time = time.time()
        time_passed = current_time - player["last_gacha_time"]
        
        # Проверяем кулдаун
        if time_passed < COOLDOWN_TIME:
            time_left = int(COOLDOWN_TIME - time_passed)
            hours = time_left // 3600
            minutes = (time_left % 3600) // 60
            time_text = f"**{hours} ч. {minutes} мин.**" if hours > 0 else f"**{minutes} мин.**"
            
            # Предлагаем заюзать Препарат V, если он есть
            if player["compound_v"] > 0:
                inline_markup = types.InlineKeyboardMarkup()
                btn_use_v = types.InlineKeyboardButton("🧪 Использовать Препарат V", callback_data="use_v")
                inline_markup.add(btn_use_v)
                
                bot.send_message(
                    message.chat.id, 
                    f"⏳ **Конвейер перегружен!** Ожидание: {time_text}.\n\n"
                    f"💡 Но у тебя есть **Препарат V ({player['compound_v']} шт.)**! Уколись, чтобы обнулить кулдаун прямо сейчас 👇",
                    reply_markup=inline_markup,
                    parse_mode="Markdown"
                )
            else:
                bot.send_message(
                    message.chat.id, 
                    f"⏳ **Конвейер Vought перегружен!**\nСледующая бесплатная крутка будет доступна через {time_text}.\n"
                    f"💡 Ты можешь купить Препарат V в магазине, чтобы не ждать!",
                    parse_mode="Markdown"
                )
            return
            
        # Обычная бесплатная крутка
        player["last_gacha_time"] = current_time
        give_gacha_reward(message, player)
        
    # НАЖАТИЕ КНОПКИ ПРОФИЛЯ
    elif message.text == "👤 Мой Профиль Vought":
        send_profile_message(message.chat.id, player)

    # МАГАЗИН: ПОКУПКА ПРЕПАРАТА V
    elif message.text == "🧪 Купить Препарат V (500 VB)":
        if player["vbucks"] < COMPOUND_V_PRICE:
            bot.send_message(
                message.chat.id, 
                f"❌ **Недостаточно средств!**\nПрепарат V стоит **{COMPOUND_V_PRICE} V-Bucks**.\n"
                f"Твой текущий баланс: {player['vbucks']} V-Bucks. Продай ненужных суперов!"
            )
            return
            
        player["vbucks"] -= COMPOUND_V_PRICE
        player["compound_v"] = player.get("compound_v", 0) + 1
        
        bot.send_message(
            message.chat.id,
            f"🧪 **Сделка под покровительством Хоумлендера!**\n"
            f"Ты успешно приобрёл 1 дозу Препарата V за **{COMPOUND_V_PRICE} V-Bucks**.\n"
            f"Теперь у тебя: {player['compound_v']} шт.\n"
            f"Баланс: {player['vbucks']} V-Bucks."
        )


# --- 4. ОБРАБОТКА НАЖАТИЯ ИНЛАЙН КНОПКИ (ИСПОЛЬЗОВАНИЕ ПРЕПАРАТА) ---
@bot.callback_query_handler(func=lambda call: call.data == "use_v")
def callback_use_v(call):
    player = get_or_create_player(call.from_user.id)
    
    if player.get("compound_v", 0) <= 0:
        bot.answer_callback_query(call.id, "❌ У тебя закончился Препарат V!")
        return
        
    player["compound_v"] -= 1
    player["last_gacha_time"] = time.time()
    
    bot.answer_callback_query(call.id, "🧪 Препарат V введён! Силы восстановлены!")
    bot.edit_message_text(
        chat_id=call.message.chat.id, 
        message_id=call.message.message_id, 
        text="💉 *Эффект Препарата V подействовал! Кулдаун сброшен!*", 
        parse_mode="Markdown"
    )
    
    give_gacha_reward(call.message, player)


# Команда продажи карт
@bot.message_handler(commands=['sell'])
def sell_character(message):
    player = get_or_create_player(message.from_user.id)
    
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        bot.send_message(message.chat.id, "❌ Укажи имя. Пример: `/sell A-Train`", parse_mode="Markdown")
        return
        
    char_name = args[1].strip()
    
    real_name = None
    for key in CHARACTERS.keys():
        if key.lower() == char_name.lower():
            real_name = key
            break
            
    if not real_name:
        bot.send_message(message.chat.id, "❌ Такого персонажа нет в базе данных Vought.")
        return
        
    if real_name not in player["inventory"]:
        bot.send_message(message.chat.id, f"❌ У тебя в инвентаре нет карточки {real_name}.")
        return
        
    price = CHARACTERS[real_name]["price"]
    player["inventory"].remove(real_name) 
    player["vbucks"] += price             
    
    bot.send_message(
        message.chat.id, 
        f"💵 Успешная сделка! Ты продал {real_name} за **{price} V-Bucks**.\n"
        f"Твой текущий баланс: **{player['vbucks']} V-Bucks**.",
        parse_mode="Markdown"
    )


# --- 5. КОСТЫЛЬ ДЛЯ БЕСПЛАТНОГО ХОСТИНГА RENDER (FLASK WEB-SERVER) ---
app = Flask('')

@app.route('/')
def home():
    return "Бот Пацанов активен, веб-сервер симулирует жизнь!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()


# --- 6. ЗАПУСК ВСЕЙ СИСТЕМЫ ---
if __name__ == '__main__':
    keep_alive() 
    print("Робот Vought успешно запущен в облаке...")
    bot.infinity_polling()
