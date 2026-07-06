import telebot
from telebot import types
import json
import os
from flask import Flask
from threading import Thread
from pymongo import MongoClient

# =================================================================
# 🌐 MONGODB BULUTLI BAZA ULANISHI (UMURBOD O'CHMAYDIGAN TIZIM)
# =================================================================
# ⚠️ <db_password> o'rniga o'z parolingizni yozib joylashtiring!
MONGO_URI = "mongodb://abduqahhorobidov54_db_user:<GcSWl3sGYF48FcfM>@ac-8rzjjyf-shard-00-00.bw5nrmr.mongodb.net:27017,ac-8rzjjyf-shard-00-01.bw5nrmr.mongodb.net:27017,ac-8rzjjyf-shard-00-02.bw5nrmr.mongodb.net:27017/?ssl=true&replicaSet=atlas-6b7gbk-shard-0&authSource=admin&appName=Cluster0&compressors=zlib"

try:
    client = MongoClient(MONGO_URI)
    db = client["animix_database"]
    anime_collection = db["anime_data"]
    admin_collection = db["admins_data"]
    print("✅ MongoDB bazasiga muvaffaqiyatli ulandi!")
except Exception as e:
    print(f"❌ MongoDB ulanishida xatolik: {e}")

# =================================================================
# 💾 22 TA ASOSIY ANIME MA'LUMOTLARI BAZASI
# =================================================================
KOD_ICHIDAGI_ANIMELER = {
    "sirlar_hukmdori": {"name": "Sirlar hukmdori", "genre": "Sirlilik, Fentezi, Sarguzasht, Triller", "desc": "Sirli va gumanoid mavjudotlar, qadimiy afsunlar va sehrli kuchlar dunyosiga xush kelibsiz. Bosh qahramon o'z o'limidan so'ng parallel o'tmish olamida uyg'onadi.", "poster": "AgACAgIAAxkBAAIDMm...", "seasons": {}},
    "qoshni_farishta": {"name": "Qoshni farishta", "genre": "Romantika, Maktab, Kundalik hayot, Komediya", "desc": "Maktabning eng go'zal va aqlli qizi — 'Farishta' laqabli qiz va uning mutlaqo oddiy, tartibsiz yashaydigan qo'shni yigiti hikoyasi.", "poster": "AgACAgIAAxkBAAIDM2...", "seasons": {}},
    "ozga_dunyoda_fermerlik_hayotim": {"name": "O'zga dunyoda fermerlik hayotim", "genre": "Isekai, Fentezi, Kundalik hayot, Harem", "desc": "Og'ir xastalikdan so'ng vafot etgan bosh qahramon Xudo tomonidan boshqa dunyoga yuboriladi.", "poster": "AgACAgIAAxkBAAIDNG...", "seasons": {}},
    "uch_mikadona_opa_singillari": {"name": "Uch Mikadona Opa-singillari", "genre": "Komediya, Romantika, Harem", "desc": "Kutilmaganda boy va nufuzli Mikadona oilasining uch nafar bir-biridan go'zal opa-singillari bilan bir uyda yashashga majbur bo'lgan yigit.", "poster": "AgACAgIAAxkBAAIDNW...", "seasons": {}},
    "hushboy_gul_viqor_bilan_gullaydi": {"name": "Hushboy gul viqor bilan gullaydi", "genre": "Tarixiy, Drama, Romantika, Fentezi", "desc": "Go'zal imperatorlik saroyi munosabatlari, fitnalar va chinakam sevgi qissasi.", "poster": "AgACAgIAAxkBAAIDNm...", "seasons": {}},
    "mening_baxtli_turmushim": {"name": "Mening baxtli turmushim", "genre": "Tarixiy, Romantika, Fentezi, Drama", "desc": "Oila a'zolari tomonidan kamsitilib, baxtsiz o'sgan qiz shafqatsiz deb nom chiqargan harbiy qo'mondonga turmushga beriladi.", "poster": "AgACAgIAAxkBAAIDN2...", "seasons": {}},
    "omadsizning_qayta_tugulishi": {"name": "Omadsizning qayta tug'ilishi", "genre": "Isekai, Fentezi, Sarguzasht, Komediya, Ekshn", "desc": "Hayotda omadi chopmagan bosh qahramon kutilmaganda fojia tufayli vafot etadi. Biroq u sehrli dunyoda qayta tug'iladi.", "poster": "AgACAgIAAxkBAAIDO0...", "seasons": {}},
    "franksdagi_sevgilim": {"name": "Franksdagi sevgilim", "genre": "Mexa, Fantastika, Drama, Romantika, Ekshn", "desc": "Vayron bo'lgan kelajak dunyosida bolalar 'Franks' deb nomlangan ulkan robotlarni boshqarib, maxluqlarga qarshi jang qilishadi.", "poster": "AgACAgIAAxkBAAIDO0...", "seasons": {}},
    "hotinimning_his_tuygulari_yoq": {"name": "Xotinimning his-tuyg'ulari yo'q", "genre": "Komediya, Fantastika, Kundalik hayot, Romantika", "desc": "Uydagi ishlarga ko'maklashish uchun sotib olingan android-robot qiz va uning egasi o'rtasidagi munosabatlar.", "poster": "AgACAgIAAxkBAAIDP0...", "seasons": {}},
    "salom_dunyo": {"name": "Salom dunyo", "genre": "Kiberpank, Fantastika, Romantika, Drama", "desc": "Kelajakdan kelgan o'zining katta yoshli varianti bilan uchrashgan yigit, sevgan qizini mudhish avariyadan qutqarib qolish uchun kurashadi.", "poster": "AgACAgIAAxkBAAIDQ0...", "seasons": {}},
    "pufak": {"name": "Pufak", "genre": "Fantastika, Sport, Drama, Sarguzasht", "desc": "Gravitatsiya qonunlari buzilgan va sirli pufaklar qurshovida qolgan Tokio shahrida yoshlar parkur musobaqalarini o'tkazishadi.", "poster": "AgACAgIAAxkBAAIDR0...", "seasons": {}},
    "hayotdan_diskvalifikatsiya_qilingan": {"name": "Hayotdan diskvalifikatsiya qilingan", "genre": "Isekai, Qora komediya, Parodiya, Fentezi", "desc": "O'z joniga qasd qilmoqchi bo'lgan mashhur yozuvchi kutilmaganda fentezi dunyoga ko'chib o'tadi.", "poster": "AgACAgIAAxkBAAIDS0...", "seasons": {}},
    "sevgida_yutqizgan_qizlar_namuncha_kop": {"name": "Sevgida yutqizgan qizlar namuncha ko'p", "genre": "Komediya, Maktab, Romantika", "desc": "O'zi yoqtirgan yigitlaridan rad javobini olgan, 'baxtsiz' qizlar klubi va ularga yordam beradigan yigit.", "poster": "AgACAgIAAxkBAAIDT0...", "seasons": {}},
    "ochkoz_berserk": {"name": "Ochko'z berserk", "genre": "Ekshn, To'q fentezi, Sarguzasht", "desc": "Ushbu dunyoda mahorat hamma narsani hal qiladi. Doimo ochlik his qiladigan va 'Ochko'zlik' la'natiga duchor bo'lgan qahramon.", "poster": "AgACAgIAAxkBAAIDU0...", "seasons": {}},
    "jodugarlar_jangi": {"name": "Jodugarlar jangi", "genre": "Ekshn, Sehr-jodu, Jangari, Fentezi", "desc": "Eng kuchli va daxshatli jodugarlar o'zlarining oliy istaklarini amalga oshirish uchun o'lim guruhlarida shafqatsiz turnirda to'qnash kelishadi.", "poster": "AgACAgIAAxkBAAIDV0...", "seasons": {}},
    "jodugarlar_jangi_film": {"name": "Jodugarlar jangi film", "genre": "Ekshn, Sehr-jodu, Fentezi, To'liq metrajli", "desc": "Jodugarlar jangi olamining eng muhim voqealari, yashirin o'tmish sirlarini o'z ichiga olgan maxsus to'liq metrajli film.", "poster": "AgACAgIAAxkBAAIDW0...", "seasons": {}},
    "tokyo_qasoskorlari": {"name": "Tokyo qasoskorlari", "genre": "Ekshn, Drama, Vaqt bo'ylab sayohat, Shonen", "desc": "Hayoti alg'ov-dalg'ov bo'lgan Takemichi kutilmaganda 12 yil o'tmishga qaytib qoladi.", "poster": "AgACAgIAAidx0...", "seasons": {}},
    "mening_qotillik_darajam_qahramonnikidan_oshib_ketdi": {"name": "Mening qotillik darajam qahramonnikidan oshib ketdi", "genre": "Isekai, Ekshn, Sehr-jodu, Sarguzasht", "desc": "Butun bir sinf xonasi boshqa dunyoga chaqiriladi. Oddiygina qotil klassini olgan yigitning kuch-qudrati kutilmaganda oshib ketadi.", "poster": "AgACAgIAAxkBAAIDY0...", "seasons": {}},
    "yoqimli_kompaniya": {"name": "Yoqimli kompaniya", "genre": "Kundalik hayot, Komediya, Do'stlik", "desc": "Katta shaharda birgalikda ishlaydigan va vaqt o'tkazadigan bir guruh quvnoq va samimiy do'stlarning hayoti.", "poster": "AgACAgIAAxkBAAIDZ0...", "seasons": {}},
    "oy_sayohati": {"name": "Oy sayohati", "genre": "Isekai, Fentezi, Sarguzasht, Komediya", "desc": "Bosh qahramon tushunarsiz sababga ko'ra boshqa olamga chaqiriladi va u yerda o'z kuchlarini sinab ko'radi.", "poster": "AgACAgIAAxkBAAIDa0...", "seasons": {}},
    "songi_serafim": {"name": "So'ngi serafim", "genre": "Post-apokalipsis, Vampirlar, Ekshn, Shonen", "desc": "Sirli virus tufayli yer yuzida faqat bolalar tirik qoladi va ular vampirlar yerosti dunyosiga qul qilinadi.", "poster": "AgACAgIAAxkBAAIDb0...", "seasons": {}},
    "sanatkorlarning_yuksalishi": {"name": "Sanatkorlarning yuksalishi", "genre": "Drama, Musiqa, Ilhomlantiruvchi, Kundalik hayot", "desc": "O'z iqtidori va san'atga bo'lgan cheksiz muhabbati orqali eng quyi pog'onalardan buyuklik sari intilgan yosh ijodkorlar.", "poster": "AgACAgIAAxkBAAIDc0...", "seasons": {}}
}

def get_anime_db():
    try:
        data = anime_collection.find_one({"_id": "anime_database_key"})
        if data:
            return data["content"]
        else:
            anime_collection.insert_one({"_id": "anime_database_key", "content": KOD_ICHIDAGI_ANIMELER})
            return KOD_ICHIDAGI_ANIMELER
    except:
        return KOD_ICHIDAGI_ANIMELER

def save_anime_db(data):
    try:
        anime_collection.update_one({"_id": "anime_database_key"}, {"$set": {"content": data}}, upsert=True)
    except Exception as e:
        print(f"Bazada saqlashda xato: {e}")

# ----------------- SOZLAMALAR -----------------
BOT_TOKEN = "8980539059:AAE4UdU4bXjv3Cp00a-WrhitnUKMwgbFwp4"  
SUPER_ADMIN = 6052679916  
KANAL_USERNAME = "@anme_X"  

bot = telebot.TeleBot(BOT_TOKEN)

def load_admins():
    try:
        data = admin_collection.find_one({"_id": "admins_list_key"})
        if data:
            return data["list"]
        else:
            admin_collection.insert_one({"_id": "admins_list_key", "list": [SUPER_ADMIN]})
            return [SUPER_ADMIN]
    except:
        return [SUPER_ADMIN]

admins_list = load_admins()
if SUPER_ADMIN not in admins_list: admins_list.append(SUPER_ADMIN)

user_states = {}

# ----------------- KLAVIATURALAR -----------------
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
    markup.row(types.KeyboardButton("🎬 Animelarni boshqarish"))
    markup.row(types.KeyboardButton("👤 Admin qo'shish"), types.KeyboardButton("📊 Statistika"))
    markup.row(types.KeyboardButton("⬅️ Bosh menyu"))
    return markup

# ----------------- BOT MANTIQI -----------------
def clean_text(text):
    if not text: return ""
    return text.lower().replace("'", "").replace("`", "").replace("’", "").replace("‘", "").replace("o'", "o").replace("g'", "g").replace("-", " ").strip()

@bot.message_handler(commands=['start'])
def start_cmd(message):
    user_id = message.chat.id
    ANIMELER = get_anime_db()
    text_args = message.text.split()
    
    if len(text_args) > 1 and text_args[1].startswith("show_"):
        anime_key = text_args[1].replace("show_", "")
        anime = ANIMELER.get(anime_key)
        if anime:
            text = f"🎬 <b>{anime['name']}</b>\n\n🎭 Janr: {anime['genre']}\n📝 Tavsif: {anime['desc']}\n\n📁 <b>Fasllar ro'yxati:</b>"
            markup = types.InlineKeyboardMarkup()
            if "seasons" in anime and anime["seasons"]:
                for s_name in anime["seasons"].keys():
                    markup.add(types.InlineKeyboardButton(text=f"📂 {s_name}", callback_data=f"se_{anime_key}_{s_name}"))
            else:
                markup.add(types.InlineKeyboardButton(text="📂 1-fasl (Hozircha bo'sh)", callback_data=f"se_{anime_key}_1-fasl"))
            markup.add(types.InlineKeyboardButton(text="⬅️ Bosh menyuga", callback_data="u_list"))
            try: bot.send_photo(user_id, photo=anime["poster"], caption=text, reply_markup=markup, parse_mode="HTML")
            except: bot.send_message(user_id, text, reply_markup=markup, parse_mode="HTML")
            return
            
    if user_id in user_states: del user_states[user_id]
    bot.send_message(user_id, "👋 <b>AniMix</b> botga xush kelibsiz!", reply_markup=get_main_menu(user_id), parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text == "⬅️ Bosh menyu")
def back_menu(message): start_cmd(message)

@bot.message_handler(func=lambda m: m.text == "👑 Admin Panel")
def admin_panel(message):
    if message.chat.id in admins_list or message.chat.id == SUPER_ADMIN:
        bot.send_message(message.chat.id, "👑 Admin paneli:", reply_markup=get_admin_menu())

@bot.message_handler(func=lambda m: m.text == "📊 Statistika")
def show_stats(message):
    if message.chat.id in admins_list or message.chat.id == SUPER_ADMIN:
        ANIMELER = get_anime_db()
        bot.send_message(message.chat.id, f"📊 Jami animelar: {len(ANIMELER)} ta")

@bot.message_handler(func=lambda m: m.text == "🔍 Qidirish")
def search_start(message):
    user_states[message.chat.id] = {"step": "searching"}
    bot.send_message(message.chat.id, "🔍 Qidirayotgan anime nomini kiriting:")

@bot.message_handler(func=lambda m: m.text == "🆕 Yangi")
def show_new_anime(message):
    ANIMELER = get_anime_db()
    if not ANIMELER: return
    markup = types.InlineKeyboardMarkup()
    keys = list(ANIMELER.keys())
    for k in keys[-5:]:
        markup.add(types.InlineKeyboardButton(text=ANIMELER[k]["name"], callback_data=f"show_{k}"))
    bot.send_message(message.chat.id, "🆕 Yangi qo'shilgan animelar:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "🔥 Mashhur")
def show_popular_anime(message):
    ANIMELER = get_anime_db()
    if not ANIMELER: return
    markup = types.InlineKeyboardMarkup()
    keys = list(ANIMELER.keys())
    for k in keys[:5]:
        markup.add(types.InlineKeyboardButton(text=ANIMELER[k]["name"], callback_data=f"show_{k}"))
    bot.send_message(message.chat.id, "🔥 Mashhur animelar:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "ℹ️ Yordam")
def help_cmd(message):
    bot.send_message(message.chat.id, "ℹ️ Bot orqali kanaldagi animelarni fasl va qismlarga bo'lingan holda tomosha qilishingiz mumkin.")

@bot.message_handler(func=lambda m: m.text == "👤 Admin qo'shish")
def add_admin_start(message):
    if message.chat.id == SUPER_ADMIN:
        user_states[message.chat.id] = {"step": "add_admin"}
        bot.send_message(message.chat.id, "Yangi admin ID raqamini yozing:")

@bot.message_handler(func=lambda m: m.text == "🎬 Animelarni boshqarish")
def admin_manage_anime(message):
    if message.chat.id not in admins_list and message.chat.id != SUPER_ADMIN: return
    ANIMELER = get_anime_db()
    markup = types.InlineKeyboardMarkup()
    for k, v in ANIMELER.items():
        markup.add(types.InlineKeyboardButton(text=f"➕ {v['name']}", callback_data=f"ad_sel_{k}"))
    bot.send_message(message.chat.id, "🎬 Qaysi animega yangi qism/fasl qo'shmoqchisiz? Tanlang:", reply_markup=markup)

@bot.callback_query_handler(func=lambda c: c.data.startswith("ad_sel_"))
def admin_selected_anime(call):
    ANIMELER = get_anime_db()
    anime_key = call.data.replace("ad_sel_", "")
    user_states[call.message.chat.id] = {"step": "wait_season", "anime_key": anime_key}
    bot.send_message(call.message.chat.id, f"✍️ <b>{ANIMELER[anime_key]['name']}</b> uchun fasl nomini kiriting:\n(Masalan: <code>1-fasl</code>)")
    bot.answer_callback_query(call.id)

@bot.message_handler(content_types=['text', 'video'])
def handle_all_inputs(message):
    user_id = message.chat.id
    if user_id not in user_states: return
    
    state = user_states[user_id]
    step = state["step"]
    ANIMELER = get_anime_db()
    
    if step == "searching":
        query = clean_text(message.text)
        results = {k: v for k, v in ANIMELER.items() if query in clean_text(v["name"])}
        if results:
            markup = types.InlineKeyboardMarkup()
            for k, v in results.items():
                markup.add(types.InlineKeyboardButton(text=v["name"], callback_data=f"show_{k}"))
            bot.send_message(user_id, "🔍 Topilgan natijalar:", reply_markup=markup)
        else:
            bot.send_message(user_id, "❌ Hech narsa topilmadi.")
        del user_states[user_id]

    elif step == "add_admin":
        try:
            new_id = int(message.text)
            if new_id not in admins_list:
                admins_list.append(new_id)
                admin_collection.update_one({"_id": "admins_list_key"}, {"$set": {"list": admins_list}}, upsert=True)
                bot.send_message(user_id, "✅ Yangi admin ro'yxatga qo'shildi!")
        except: pass
        del user_states[user_id]

    elif step == "wait_season":
        state["season_name"] = message.text.strip()
        state["step"] = "wait_episode"
        bot.send_message(user_id, f"✍️ Endi qism raqamini yoki nomini kiriting:\n(Masalan: <code>1-qism</code>)")

    elif step == "wait_episode":
        state["episode_name"] = message.text.strip()
        state["step"] = "wait_video"
        bot.send_message(user_id, f"📹 Endi menga o'sha videoni yuboring (yoki kanaldan forward qiling):")

    elif step == "wait_video":
        if message.video is not None:
            video_file_id = message.video.file_id
            ak = state["anime_key"]
            sn = state["season_name"]
            en = state["episode_name"]
            
            if "seasons" not in ANIMELER[ak]:
                ANIMELER[ak]["seasons"] = {}
            if sn not in ANIMELER[ak]["seasons"]:
                ANIMELER[ak]["seasons"][sn] = {}
                
            ANIMELER[ak]["seasons"][sn][en] = video_file_id
            save_anime_db(ANIMELER)
            
            bot.send_message(user_id, f"✅ <b>Muvaffaqiyatli qo'shildi va MongoDB-ga saqlandi!</b>\n\n🎬 Anime: {ANIMELER[ak]['name']}\n📂 Fasl: {sn}\n🍿 Qism: {en}", parse_mode="HTML")
            del user_states[user_id]
        else:
            bot.send_message(user_id, "⚠️ Iltimos, faqat video fayl yuboring!")

@bot.message_handler(func=lambda m: m.text == "📚 Anime")
def user_anime_list(message):
    ANIMELER = get_anime_db()
    if not ANIMELER:
        bot.send_message(message.chat.id, "⚠️ Hozircha bazada animelar mavjud emas.")
        return
    markup = types.InlineKeyboardMarkup()
    for k, v in ANIMELER.items():
        markup.add(types.InlineKeyboardButton(text=v["name"], callback_data=f"show_{k}"))
    bot.send_message(message.chat.id, "📚 Jamlanma — Kerakli animeni tanlang:", reply_markup=markup)

@bot.callback_query_handler(func=lambda c: c.data.startswith("show_"))
def user_show_anime(call):
    ANIMELER = get_anime_db()
    anime_key = call.data.replace("show_", "")
    anime = ANIMELER.get(anime_key)
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
    try: bot.send_photo(call.message.chat.id, photo=anime["poster"], caption=text, reply_markup=markup, parse_mode="HTML")
    except: bot.send_message(call.message.chat.id, text, reply_markup=markup, parse_mode="HTML")

@bot.callback_query_handler(func=lambda c: c.data == "u_list")
def back_to_user_list(call):
    try: bot.delete_message(call.message.chat.id, call.message.message_id)
    except: pass
    user_anime_list(call.message)

@bot.callback_query_handler(func=lambda c: c.data.startswith("se_"))
def user_show_season(call):
    ANIMELER = get_anime_db()
    parts = call.data.split("_")
    ak = parts[1]
    sn = "_".join(parts[2:])
    
    markup = types.InlineKeyboardMarkup(row_width=4)
    buttons = []
    
    if ak in ANIMELER and "seasons" in ANIMELER[ak] and sn in ANIMELER[ak]["seasons"]:
        episodes = ANIMELER[ak]["seasons"][sn]
        for ep_name in sorted(episodes.keys()):
            clean_ep = ep_name.replace("-qism", "").strip()
            buttons.append(types.InlineKeyboardButton(text=clean_ep, callback_data=f"play_{ak}_{sn}_{ep_name}"))
            
    if buttons:
        markup.add(*buttons)
        text = f"🍿 <b>{ANIMELER[ak]['name']}</b> - {sn} qismlari:"
    else:
        text = f"🍿 <b>{ANIMELER[ak]['name']}</b> - {sn}\n\n⚠️ <i>Ushbu faslga hali qismlar yuklanmagan.</i>"
        
    markup.add(types.InlineKeyboardButton(text="⬅️ Fasllarga qaytish", callback_data=f"show_{ak}"))
    try: bot.delete_message(call.message.chat.id, call.message.message_id)
    except: pass
    bot.send_message(call.message.chat.id, text, reply_markup=markup, parse_mode="HTML")

@bot.callback_query_handler(func=lambda c: c.data.startswith("play_"))
def user_play_video(call):
    ANIMELER = get_anime_db()
    parts = call.data.split("_")
    ak, sn, en = parts[1], parts[2], parts[3]
    if ak in ANIMELER and sn in ANIMELER[ak]["seasons"] and en in ANIMELER[ak]["seasons"][sn]:
        video_id = ANIMELER[ak]["seasons"][sn][en]
        try:
            bot.send_video(call.message.chat.id, video=video_id, caption=f"🎬 {ANIMELER[ak]['name']}\n🍿 {sn} | {en}")
        except Exception as e:
            bot.send_message(call.message.chat.id, f"❌ Videoni yuborishda xato: {e}")
    bot.answer_callback_query(call.id)

# 24/7 VEB-SERVER (FLASK)
app = Flask('')
@app.route('/')
def home(): return "Bot MongoDB bilan 24/7 faol holatda!"

def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive():
    t = Thread(target=run)
    t.start()

if __name__ == '__main__':
    keep_alive()
    bot.polling(none_stop=True, timeout=60, long_polling_timeout=5)
