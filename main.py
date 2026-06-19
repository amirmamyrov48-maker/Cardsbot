# Вспомогательная функция для форматирования времени
    def get_time_left(seconds):
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        return f"{h} ч. {m} мин."

    # --- ЛОГИКА ВНУТРИ HANDLE_TEXT ---
    
    # 1. ЕЖЕДНЕВКА
    if message.text == "🎁 Ежедневка":
        if time.time() - player["last_bonus"] >= 86400:
            bonus = 350 if player["equipped"] == "🧥 Плащ Бутчера" else 250
            player["vbucks"] += bonus
            player["last_bonus"] = time.time()
            save_data()
            bot.send_message(message.chat.id, f"✅ **Бонус получен:** {bonus} V-Bucks!")
        else:
            left = 86400 - (time.time() - player["last_bonus"])
            bot.send_message(message.chat.id, f"❌ **Рано!** До следующего бонуса: `{get_time_left(left)}`", parse_mode="Markdown")

    # 2. ГАЧА ГЕРОЕВ
    elif message.text == "🎰 Гача героев":
        cooldown = 7200 if player["equipped"] == "👗 Костюм Старлайт" else 10800
        if player["equipped"] == "🎀 Костюм горничной": cooldown -= 2700
        
        diff = time.time() - player["last_gacha"]
        if diff >= cooldown:
            char = random.choice(list(CHARACTERS.keys()))
            player["inventory"].append(char)
            player["last_gacha"] = time.time()
            save_data()
            bot.send_message(message.chat.id, f"🎰 **Vought запускает конвейер!**\n\n🎉 Выпал: **{char}**", parse_mode="Markdown")
        else:
            bot.send_message(message.chat.id, f"⏳ **Конвейер Vought перегружен!**\nОсталось ждать: `{get_time_left(cooldown - diff)}`", parse_mode="Markdown")

    # 3. ГАЧА КОСТЮМОВ
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
                bot.send_message(message.chat.id, f"👗 **Vought Fashion:**\nВы получили: **{outfit}**!", parse_mode="Markdown")
            else:
                bot.send_message(message.chat.id, f"❌ **Недостаточно средств!** Нужно {cost} VB.")
        else:
            bot.send_message(message.chat.id, f"⏳ **Конвейер моды занят!**\nОсталось ждать: `{get_time_left(7200 - diff)}`", parse_mode="Markdown")
