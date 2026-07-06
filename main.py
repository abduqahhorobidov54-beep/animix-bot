import telebot
from telebot import types
import json
import os
import hashlib
from flask import Flask
from threading import Thread

# ----------------- 1. SOZLAMALAR -----------------
# ⚠️ TOKENingizni shu yerga yozing
BOT_TOKEN = "8980539059:AAE4UdU4bXjv3Cp00a-WrhitnUKMwgbFwp4"  

# ⚠️ O'z Telegram ID raqamingizni shu yerga yozing
SUPER_ADMIN = 6052679916  

# ⚠️ Kanalingiz username'ini shu yerga yozing
KANAL_USERNAME = "@anme_X"  

bot = telebot.TeleBot(BOT_TOKEN)

ANIME_FILE = "anime_db.json"
ADMIN_FILE = "admins_db.json"

# ----------------- 2. MA'LUMOTLAR BAZASI -----------------
def load_json(filename, default_value):
    try:
        if not os.path.exists(filename) or os.stat(filename).st_size == 0:
            return default_value
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return default_value

def save_json(filename, data):
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Faylga yozishda xato: {e}")

anime_db = load_json(ANIME_FILE, {})
admins_list = load_json(ADMIN_FILE, [SUPER_ADMIN])

if SUPER_ADMIN not in admins_list:
    admins_list.append(SUPER_ADMIN)

def save_anime():
    global anime_db
    save_json(ANIME_FILE, anime_db)

def save_admins():
    global admins_list
    save_json(ADMIN_FILE, admins_list)

user_states = {}

BOT_INFO = bot.get_me()
BOT_USER = BOT_INFO.username

# ----------------- 3. KLAVIATURALAR -----------------
def get_main_menu(user_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(types.KeyboardButton("📚 Anime"), types.KeyboardButton("🔍 Qidirish"))
    markup.row(types.KeyboardButton("🆕 Yangi"), types.KeyboardButton("🔥 Mashhur"))
    markup.row(types.KeyboardButton("ℹ️ Yordam"))
    if user_id in admins_list or user_id == SUPER_ADMIN:
        markup.row(types.KeyboardButton("👑 Admin Panel"))
    return markup

def get_admin_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(types.KeyboardButton("➕ Anime qo'shish"), types.KeyboardButton("➕ Qism qo'shish"))
    markup.row(types.KeyboardButton("👤 Admin qo'shish"), types.KeyboardButton("❌ Admin o'chirish"))
    markup.row(types.KeyboardButton("📊 Statistika"), types.KeyboardButton("⬅️ Bosh menyu"))
    return markup

# ----------------- 4. BOT MANTIQI -----------------

@bot.channel_post_handler(content_types=['photo'])
def handle_channel_post(message):
    global anime_db
    if message.chat.username and f"@{message.chat.username}".lower() == KANAL_USERNAME.lower():
        caption = message.caption
        if not caption: return
        
        lines = [l.strip() for l in caption.split("\n") if l.strip()]
        if not lines: return
        
        raw_name = lines[0]
        name = raw_name.replace("│", "").replace("┌", "").replace("┐", "").replace("├", "").replace("─", "").strip()
        
        genre = "Anime"
        for line in lines:
            if "janr" in line.lower():
                if ":" in line: genre = line.split(":", 1)[1].strip()
                elif "-" in line: genre = line.split("-", 1)[1].strip()

        if name:
            anime_key = hashlib.md5(name.lower().encode('utf-8')).hexdigest()[:10]
            poster_id = message.photo[-1].file_id
            
            if anime_key not in anime_db:
                anime_db[anime_key] = {
                    "name": name,
                    "poster": poster_id,
                    "desc": caption,
                    "genre": genre,
                    "seasons": {}
                }
                save_anime()
            
            link = f"https://t.me/{BOT_USER}?start=show_{anime_key}"
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton(text="🍿 Tomosha qilish", url=link))
            
            try:
                bot.edit_message_caption(
                    chat_id=message.chat.id,
                    message_id=message.message_id,
                    caption=caption,
                    reply_markup=markup
                )
            except Exception as e:
                print(f"Kanal postini tahrirlashda xato: {e}")

@bot.message_handler(commands=['start'])
def start_cmd(message):
    user_id = message.chat.id
    text_args = message.text.split()
    
    if len(text_args) > 1 and text_args[1].startswith("show_"):
        anime_key = text_args[1].replace("show_", "")
        anime = anime_db.get(anime_key)
        if anime:
            text = f"🎬 <b>{anime['name']}</b>\n\n🎭 Janr: {anime['genre']}\n📝 Tavsif: {anime['desc']}\n\n📁 <b>Fasllar ro'yxati:</b>"
            markup = types.InlineKeyboardMarkup()
            
            if "seasons" in anime and anime["seasons"]:
                for s_name in anime["seasons"].keys():
                    markup.add(types.InlineKeyboardButton(text=f"📂 {s_name}", callback_data=f"se_{anime_key}_{s_name}"))
            else:
                markup.add(types.InlineKeyboardButton(text="📂 1-fasl (Hozircha bo'sh)", callback_data=f"se_{anime_key}_1-fasl"))
                
            markup.add(types.InlineKeyboardButton(text="⬅️ Bosh menyuga", callback_data="u_list"))
            bot.send_photo(user_id, photo=anime["poster"], caption=text, reply_markup=markup, parse_mode="HTML")
            return
        else:
            bot.send_message(user_id, "❌ Anime topilmadi yoki baza tozalangan.")
            return
            
    if user_id in user_states: del user_states[user_id]
    bot.send_message(user_id, "👋 <b>AniMix</b> botga xush kelibsiz!", reply_markup=get_main_menu(user_id), parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text == "⬅️ Bosh menyu")
def back_menu(message):
    start_cmd(message)

@bot.message_handler(func=lambda m: m.text == "👑 Admin Panel")
def admin_panel(message):
    if message.chat.id in admins_list or message.chat.id == SUPER_ADMIN:
        bot.send_message(message.chat.id, "👑 Admin paneli:", reply_markup=get_admin_menu())

@bot.message_handler(func=lambda m: m.text == "📊 Statistika")
def show_stats(message):
    if message.chat.id in admins_list or message.chat.id == SUPER_ADMIN:
        bot.send_message(message.chat.id, f"📊 Jami animelar: {len(anime_db)} ta")

@bot.message_handler(func=lambda m: m.text == "🔍 Qidirish")
def search_start(message):
    user_states[message.chat.id] = {"step": "searching"}
    bot.send_message(message.chat.id, "🔍 Qidirayotgan anime nomini kiriting:")

@bot.message_handler(func=lambda m: m.text == "🆕 Yangi")
def show_new_anime(message):
    if not anime_db: return
    markup = types.InlineKeyboardMarkup()
    for k in list(anime_db.keys())[-5:]:
        markup.add(types.InlineKeyboardButton(text=anime_db[k]["name"], callback_data=f"show_{k}"))
    bot.send_message(message.chat.id, "🆕 Yangi animelar:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "🔥 Mashhur")
def show_popular_anime(message):
    if not anime_db: return
    markup = types.InlineKeyboardMarkup()
    for k in list(anime_db.keys())[:5]:
        markup.add(types.InlineKeyboardButton(text=anime_db[k]["name"], callback_data=f"show_{k}"))
    bot.send_message(message.chat.id, "🔥 Mashhur animelar:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "ℹ️ Yordam")
def help_cmd(message):
    bot.send_message(message.chat.id, "ℹ️ Bot orqali kanaldagi animelarni fasl va qismlarga bo'lingan holda tomosha qilishingiz mumkin.")

@bot.message_handler(func=lambda m: m.text == "👤 Admin qo'shish")
def add_admin_start(message):
    if message.chat.id == SUPER_ADMIN:
        user_states[message.chat.id] = {"step": "add_admin"}
        bot.send_message(message.chat.id, "Yangi admin ID raqamini yozing:")

@bot.message_handler(func=lambda m: m.text == "❌ Admin o'chirish")
def del_admin_start(message):
    if message.chat.id == SUPER_ADMIN:
        user_states[message.chat.id] = {"step": "del_admin"}
        bot.send_message(message.chat.id, "O'chiriladigan admin ID raqamini yozing:")

@bot.message_handler(func=lambda m: m.text == "➕ Anime qo'shish")
def add_anime_start(message):
    if message.chat.id in admins_list or message.chat.id == SUPER_ADMIN:
        user_states[message.chat.id] = {"step": "anime_name"}
        bot.send_message(message.chat.id, "📝 Anime nomini kiriting:")

@bot.message_handler(func=lambda m: m.text == "➕ Qism qo'shish")
def add_ep_start(message):
    if message.chat.id in admins_list or message.chat.id == SUPER_ADMIN:
        if not anime_db:
            bot.send_message(message.chat.id, "⚠️ Avval anime qo'shishingiz kerak!")
            return
        markup = types.InlineKeyboardMarkup()
        for k, v in anime_db.items():
            markup.add(types.InlineKeyboardButton(text=v["name"], callback_data=f"ad_ep_{k}"))
        bot.send_message(message.chat.id, "Qaysi animega qism qo'shmoqchisiz? Tanlang:", reply_markup=markup)

@bot.callback_query_handler(func=lambda c: c.data.startswith("ad_ep_"))
def add_ep_select_anime(call):
    anime_key = call.data.replace("ad_ep_", "")
    user_states[call.message.chat.id] = {"step": "season_name", "anime_key": anime_key}
    bot.send_message(call.message.chat.id, "📁 Fasl nomini kiriting (Masalan: 1-fasl):")

@bot.message_handler(content_types=['text', 'photo', 'video'])
def handle_inputs(message):
    global anime_db
    user_id = message.chat.id
    if user_id not in user_states: return
    
    state = user_states[user_id]
    step = state["step"]
    
    if step == "searching" and message.content_type == 'text':
        query = message.text.lower()
        results = {k: v for k, v in anime_db.items() if query in v["name"].lower()}
        if results:
            markup = types.InlineKeyboardMarkup()
            for k, v in results.items():
                markup.add(types.InlineKeyboardButton(text=v["name"], callback_data=f"show_{k}"))
            bot.send_message(user_id, "🔍 Natijalar:", reply_markup=markup)
        else:
            bot.send_message(user_id, "❌ Topilmadi.")
        del user_states[user_id]

    elif step == "add_admin" and message.content_type == 'text':
        try:
            new_id = int(message.text)
            if new_id not in admins_list:
                admins_list.append(new_id)
                save_admins()
                bot.send_message(user_id, "✅ Admin qo'shildi!")
        except: pass
        del user_states[user_id]

    elif step == "anime_name" and message.content_type == 'text':
        state["name"] = message.text
        state["step"] = "anime_poster"
        bot.send_message(user_id, "🖼 Poster (rasm) yuboring:")

    elif step == "anime_poster" and message.content_type == 'photo':
        state["poster"] = message.photo[-1].file_id
        state["step"] = "anime_desc"
        bot.send_message(user_id, "📝 Tavsif (opisaniya) yozing:")

    elif step == "anime_desc" and message.content_type == 'text':
        state["desc"] = message.text
        state["step"] = "anime_genre"
        bot.send_message(user_id, "🎭 Janrini kiriting:")

    elif step == "anime_genre" and message.content_type == 'text':
        anime_key = hashlib.md5(state["name"].lower().encode('utf-8')).hexdigest()[:10]
        anime_db[anime_key] = {
            "name": state["name"], "poster": state["poster"],
            "desc": state["desc"], "genre": message.text, "seasons": {}
        }
        save_anime()
        bot.send_message(user_id, "🎉 Anime muvaffaqiyatli saqlandi!")
        del user_states[user_id]

    elif step == "season_name" and message.content_type == 'text':
        state["season_name"] = message.text
        state["step"] = "ep_name"
        bot.send_message(user_id, "🍿 Qism raqamini yoki nomini kiriting (Masalan: 1-qism):")

    elif step == "ep_name" and message.content_type == 'text':
        state["ep_name"] = message.text
        state["step"] = "ep_video"
        bot.send_message(user_id, "🎬 Videoni yuboring:")

    elif step == "ep_video" and message.content_type == 'video':
        ak, sn, en = state["anime_key"], state["season_name"], state["ep_name"]
        if ak in anime_db:
            if "seasons" not in anime_db[ak]: anime_db[ak]["seasons"] = {}
            if sn not in anime_db[ak]["seasons"]: anime_db[ak]["seasons"][sn] = {}
            anime_db[ak]["seasons"][sn][en] = message.video.file_id
            save_anime()
            bot.send_message(user_id, f"🚀 {sn}ga {en} muvaffaqiyatli yuklandi!")
        del user_states[user_id]

@bot.message_handler(func=lambda m: m.text == "📚 Anime")
def user_anime_list(message):
    if not anime_db:
        bot.send_message(message.chat.id, "⚠️ Hozircha bazada animelar yo'q.")
        return
    markup = types.InlineKeyboardMarkup()
    for k, v in anime_db.items():
        markup.add(types.InlineKeyboardButton(text=v["name"], callback_data=f"show_{k}"))
    bot.send_message(message.chat.id, "🎬 Animeni tanlang:", reply_markup=markup)

@bot.callback_query_handler(func=lambda c: c.data.startswith("show_"))
def user_show_anime(call):
    anime_key = call.data.replace("show_", "")
    anime = anime_db.get(anime_key)
    if not anime: return
    text = f"🎬 <b>{anime['name']}</b>\n\n🎭 Janr: {anime['genre']}\n📝 Tavsif: {anime['desc']}\n\n📁 Fasllar:"
    markup = types.InlineKeyboardMarkup()
    if "seasons" in anime and anime["seasons"]:
        for s_name in anime["seasons"].keys():
            markup.add(types.InlineKeyboardButton(text=f"📂 {s_name}", callback_data=f"se_{anime_key}_{s_name}"))
    else:
        markup.add(types.InlineKeyboardButton(text="📂 1-fasl (Hozircha bo'sh)", callback_data=f"se_{anime_key}_1-fasl"))
    markup.add(types.InlineKeyboardButton(text="⬅️ Orqaga", callback_data="u_list"))
    try: bot.delete_message(call.message.chat.id, call.message.message_id)
    except: pass
    bot.send_photo(call.message.chat.id, photo=anime["poster"], caption=text, reply_markup=markup, parse_mode="HTML")

@bot.callback_query_handler(func=lambda c: c.data == "u_list")
def back_to_user_list(call):
    try: bot.delete_message(call.message.chat.id, call.message.message_id)
    except: pass
    user_anime_list(call.message)

@bot.callback_query_handler(func=lambda c: c.data.startswith("se_"))
def user_show_season(call):
    parts = call.data.split("_")
    ak = parts[1]
    sn = "_".join(parts[2:])
    
    markup = types.InlineKeyboardMarkup(row_width=4)
    buttons = []
    
    if ak in anime_db and "seasons" in anime_db[ak] and sn in anime_db[ak]["seasons"]:
        episodes = anime_db[ak]["seasons"][sn]
        for ep_name in sorted(episodes.keys()):
            clean_ep = ep_name.replace("-qism", "").strip()
            buttons.append(types.InlineKeyboardButton(text=clean_ep, callback_data=f"play_{ak}_{sn}_{ep_name}"))
            
    if buttons:
        markup.add(*buttons)
        text = f"🍿 <b>{anime_db[ak]['name']}</b> - {sn} qismlari:"
    else:
        text = f"🍿 <b>{anime_db[ak]['name']}</b> - {sn}\n\n⚠️ <i>Ushbu faslga hali qismlar yuklanmagan.</i>"
        
    markup.add(types.InlineKeyboardButton(text="⬅️ Fasllarga qaytish", callback_data=f"show_{ak}"))
    try: bot.delete_message(call.message.chat.id, call.message.message_id)
    except: pass
    bot.send_message(call.message.chat.id, text, reply_markup=markup, parse_mode="HTML")

@bot.callback_query_handler(func=lambda c: c.data.startswith("play_"))
def user_play_video(call):
    parts = call.data.split("_")
    ak, sn, en = parts[1], parts[2], parts[3]
    if ak in anime_db and sn in anime_db[ak]["seasons"] and en in anime_db[ak]["seasons"][sn]:
        video_id = anime_db[ak]["seasons"][sn][en]
        bot.send_video(call.message.chat.id, video=video_id, caption=f"🎬 {anime_db[ak]['name']}\n🍿 {sn} | {en}")
    bot.answer_callback_query(call.id)

# ----------------- 5. 24/7 VEB-SERVER (FLASK) -----------------
app = Flask('')

@app.route('/')
def home():
    return "Bot 24/7 faol holatda!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

if __name__ == '__main__':
    print("Bot yoqyapti...")
    keep_alive()  # Veb-serverni parallel rejimda ishga tushirish
    bot.infinity_polling(skip_pending=True)
