import telebot
from telebot import types
import json
import os
from flask import Flask
from threading import Thread

# =================================================================
# 💾 UMURBOD O'CHMAYDIGAN 22 TA ANIME MA'LUMOTLARI OMBORI
# =================================================================
KOD_ICHIDAGI_ANIMELER = {
    "sirlar_hukmdori": {
        "name": "Sirlar hukmdori",
        "genre": "Sirlilik, Fentezi, Sarguzasht, Triller",
        "desc": "Sirli va gumanoid mavjudotlar, qadimiy afsunlar va sehrli kuchlar dunyosiga xush kelibsiz. Bosh qahramon o'z o'limidan so'ng mutlaqo g'ayritabiiy va sirlarga boy parallel o'tmish olamida uyg'onadi.",
        "poster": "AgACAgIAAxkBAAIDMm...", 
        "seasons": {}
    },
    "qoshni_farishta": {
        "name": "Qoshni farishta",
        "genre": "Romantika, Maktab, Kundalik hayot, Komediya",
        "desc": "Maktabning eng go'zal va aqlli qizi — 'Farishta' laqabli qiz va uning mutlaqo oddiy, tartibsiz yashaydigan qo'shni yigiti o'rtasidagi kutilmagan va iliq munosabatlar haqida go'zal hikoya.",
        "poster": "AgACAgIAAxkBAAIDM2...",
        "seasons": {}
    },
    "ozga_dunyoda_fermerlik_hayotim": {
        "name": "O'zga dunyoda fermerlik hayotim",
        "genre": "Isekai, Fentezi, Kundalik hayot, Harem",
        "desc": "Og'ir xastalikdan so'ng vafot etgan bosh qahramon Xudo tomonidan boshqa dunyoga yuboriladi. Unga sehrli dehqonchilik quroli beriladi va u o'zining orzusidagi tinch, farovon fermerlik hayotini qurishni boshlaydi.",
        "poster": "AgACAgIAAxkBAAIDNG...",
        "seasons": {}
    },
    "uch_mikadona_opa_singillari": {
        "name": "Uch Mikadona Opa-singillari",
        "genre": "Komediya, Romantika, Harem",
        "desc": "Kutilmaganda boy va nufuzli Mikadona oilasining uch nafar bir-biridan go'zal, ammo fe'l-atvori turlicha bo'lgan opa-singillari bilan bir uyda yashashga majbur bo'lgan yigitning qiziqarli sarguzashtlari.",
        "poster": "AgACAgIAAxkBAAIDNW...",
        "seasons": {}
    },
    "hushboy_gul_viqor_bilan_gullaydi": {
        "name": "Hushboy gul viqor bilan gullaydi",
        "genre": "Tarixiy, Drama, Romantika, Fentezi",
        "desc": "Go'zal imperatorlik saroyi munosabatlari, fitnalar va chinakam sevgi qissasi. O'z viqori va nafosati bilan ajralib turadigan qahramonning qiyinchiliklarni yengib o'tish yo'li.",
        "poster": "AgACAgIAAxkBAAIDNm...",
        "seasons": {}
    },
    "mening_baxtli_turmushim": {
        "name": "Mening baxtli turmushim",
        "genre": "Tarixiy, Romantika, Fentezi, Drama",
        "desc": "Oila a'zolari tomonidan kamsitilib, baxtsiz o'sgan qiz shafqatsiz deb nom chiqargan harbiy qo'mondonga turmushga beriladi. Ammo bu turmush unga hayotidagi eng haqiqiy baxt va sevgini taqdim etadi.",
        "poster": "AgACAgIAAxkBAAIDN2...",
        "seasons": {}
    },
    "omadsizning_qayta_tugulishi": {
        "name": "Omadsizning qayta tug'ilishi",
        "genre": "Isekai, Fentezi, Sarguzasht, Komediya, Ekshn",
        "desc": "Hayotda omadi chopmagan bosh qahramon kutilmaganda fojia tufayli vafot etadi. Biroq u sehr-jodu va xavf-xatarlarga boy mutlaqo boshqa bir sehrli dunyoda qayta tug'iladi.",
        "poster": "AgACAgIAAxkBAAIDO0...",
        "seasons": {}
    },
    "franksdagi_sevgilim": {
        "name": "Franksdagi sevgilim",
        "genre": "Mexa, Fantastika, Drama, Romantika, Ekshn",
        "desc": "Vayron bo'lgan kelajak dunyosida bolalar 'Franks' deb nomlangan ulkan robotlarni boshqarib, maxluqlarga qarshi jang qilishadi. Zero Two ismli sirli qiz va yosh uchuvchining taqdiri zanjiri.",
        "poster": "AgACAgIAAxkBAAIDO0...",
        "seasons": {}
    },
    "hotinimning_his_tuygulari_yoq": {
        "name": "Xotinimning his-tuyg'ulari yo'q",
        "genre": "Komediya, Fantastika, Kundalik hayot, Romantika",
        "desc": "Uydagi ishlarga ko'maklashish uchun sotib olingan android-robot qiz va uning egasi o'rtasidagi gajibona munosabatlar. Robotlarda haqiqatan ham his-tuyg'u bo'lishi mumkinmi?",
        "poster": "AgACAgIAAxkBAAIDP0...",
        "seasons": {}
    },
    "salom_dunyo": {
        "name": "Salom dunyo",
        "genre": "Kiberpank, Fantastika, Romantika, Drama",
        "desc": "Kelajakdan kelgan o'zining katta yoshli varianti bilan uchrashgan yigit, sevgan qizini mudhish avariyadan qutqarib qolish uchun virtual reallik va xotiralar olamida kurash boshlaydi.",
        "poster": "AgACAgIAAxkBAAIDQ0...",
        "seasons": {}
    },
    "pufak": {
        "name": "Pufak",
        "genre": "Fantastika, Sport, Drama, Sarguzasht",
        "desc": "Gravitatsiya qonunlari buzilgan va sirli pufaklar qurshovida qolgan Tokio shahrida yoshlar parkur musobaqalarini o'tkazishadi. Noyob qobiliyatli yigit va sirli qizning uchrashuvi.",
        "poster": "AgACAgIAAxkBAAIDR0...",
        "seasons": {}
    },
    "hayotdan_diskvalifikatsiya_qilingan": {
        "name": "Hayotdan diskvalifikatsiya qilingan",
        "genre": "Isekai, Qora komediya, Parodiya, Fentezi",
        "desc": "O'z joniga qasd qilmoqchi bo'lgan mashhur yozuvchi kutilmaganda boshqa fentezi dunyoga ko'chib o'tadi. Bosh qahramonlar dunyoni qutqarishni o'ylasa, u faqat sokin o'lim izlaydi.",
        "poster": "AgACAgIAAxkBAAIDS0...",
        "seasons": {}
    },
    "sevgida_yutqizgan_qizlar_namuncha_kop": {
        "name": "Sevgida yutqizgan qizlar namuncha ko'p",
        "genre": "Komediya, Maktab, Romantika",
        "desc": "O'zi yoqtirgan yigitlaridan rad javobini olgan, 'baxtsiz' qizlar klubi va ularning munosabatlarini chetdan kuzatib, yordam berishga majbur bo'lgan oddiy sinfdosh yigit hikoyasi.",
        "poster": "AgACAgIAAxkBAAIDT0...",
        "seasons": {}
    },
    "ochkoz_berserk": {
        "name": "Ochko'z berserk",
        "genre": "Ekshn, To'q fentezi, Sarguzasht",
        "desc": "Ushbu dunyoda mahorat va qobiliyatlar hamma narsani hal qiladi. Doimo ochlik his qiladigan va 'Ochko'zlik' la'natiga duchor bo'lgan qahramonning qudratli jangchiga aylanish yo'li.",
        "poster": "AgACAgIAAxkBAAIDU0...",
        "seasons": {}
    },
    "jodugarlar_jangi": {
        "name": "Jodugarlar jangi",
        "genre": "Ekshn, Sehr-jodu, Jangari, Fentezi",
        "desc": "Eng kuchli va daxshatli jodugarlar o'zlarining oliy istaklarini amalga oshirish va dunyoda tengsiz ekanliklarini isbotlash uchun o'lim guruhlarida shafqatsiz turnirda to'qnash kelishadi.",
        "poster": "AgACAgIAAxkBAAIDV0...",
        "seasons": {}
    },
    "jodugarlar_jangi_film": {
        "name": "Jodugarlar jangi film",
        "genre": "Ekshn, Sehr-jodu, Fentezi, To'liq metrajli",
        "desc": "Jodugarlar jangi olamining eng muhim voqealari, yashirin o'tmish sirlari va eng daxshatli jang sahnalarini o'z ichiga olgan maxsus to'liq metrajli film.",
        "poster": "AgACAgIAAxkBAAIDW0...",
        "seasons": {}
    },
    "tokyo_qasoskorlari": {
        "name": "Tokyo qasoskorlari",
        "genre": "Ekshn, Drama, Vaqt bo'ylab sayohat, Shonen",
        "desc": "Hayoti alg'ov-dalg'ov bo'lgan Takemichi kutilmaganda 12 yil o'tmishga qaytib qoladi. U o'zining maktab davridagi sevgilisini kelajakda shafqatsiz guruh qo'lidan qutqarish uchun Tokio mafiyasining eng cho'qqisiga chiqishga qaror qiladi.",
        "poster": "AgACAgIAAxkBAAIDX0...",
        "seasons": {}
    },
    "mening_qotillik_darajam_qahramonnikidan_oshib_ketdi": {
        "name": "Mening qotillik darajam qahramonnikidan oshib ketdi",
        "genre": "Isekai, Ekshn, Sehr-jodu, Sarguzasht",
        "desc": "Butun bir sinf xonasi boshqa dunyoga qahramon sifatida chaqiriladi. Ammo qotil klassini olgan yigitning kuch-qudrati kutilmaganda asosiy qahramonnikidan ham daxshatli darajada oshib ketdi.",
        "poster": "AgACAgIAAxkBAAIDY0...",
        "seasons": {}
    },
    "yoqimli_kompaniya": {
        "name": "Yoqimli kompaniya",
        "genre": "Kundalik hayot, Komediya, Do'stlik",
        "desc": "Katta shaharda birgalikda ishlaydigan va vaqt o'tkazadigan bir guruh quvnoq va samimiy do'stlarning hayoti, yumorga boy suhbatlari va qiziqarli sarguzashtlari.",
        "poster": "AgACAgIAAxkBAAIDZ0...",
        "seasons": {}
    },
    "oy_sayohati": {
        "name": "Oy sayohati",
        "genre": "Isekai, Fentezi, Sarguzasht, Komediya",
        "desc": "Bosh qahramon tushunarsiz sababga ko'ra boshqa olamga chaqiriladi va u yerda o'z kuchlarini sinab ko'radi.",
        "poster": "AgACAgIAAxkBAAIDa0...",
        "seasons": {}
    },
    "songi_serafim": {
        "name": "So'ngi serafim",
        "genre": "Post-apokalipsis, Vampirlar, Ekshn, Shonen",
        "desc": "Sirli virus tufayli yer yuzida faqat bolalar tirik qoladi va ular vampirlar yerosti dunyosiga qul qilinadi. Qonxo'rlardan qochib qutulgan Yuuichirou insoniyat armiyasiga qo'shilib, qasos olishga ont ichadi.",
        "poster": "AgACAgIAAxkBAAIDb0...",
        "seasons": {}
    },
    "sanatkorlarning_yuksalishi": {
        "name": "Sanatkorlarning yuksalishi",
        "genre": "Drama, Musiqa, Ilhomlantiruvchi, Kundalik hayot",
        "desc": "O'z iqtidori va san'atga bo'lgan cheksiz muhabbati orqali eng quyi pog'onalardan buyuklik sari intilgan yosh ijodkorlarning mashaqqatli va ilhomga boy hayot yo'li.",
        "poster": "AgACAgIAAxkBAAIDc0...",
        "seasons": {}
    }
}

# ----------------- 2. SOZLAMALAR -----------------
# 💾 Skrinshotingizdan olingan haqiqiy ma'lumotlar avtomatik kiritildi
BOT_TOKEN = "8980539059:AAE4UdU4bXjv3Cp00a-WrhitnUKMwgbFwp4"  
SUPER_ADMIN = 6052679916  
KANAL_USERNAME = "@anme_X"  

bot = telebot.TeleBot(BOT_TOKEN)
ADMIN_FILE = "admins_db.json"

def load_json(filename, default_value):
    try:
        if not os.path.exists(filename) or os.stat(filename).st_size == 0:
            return default_value
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return default_value

admins_list = load_json(ADMIN_FILE, [SUPER_ADMIN])
if SUPER_ADMIN not in admins_list:
    admins_list.append(SUPER_ADMIN)

user_states = {}

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
    markup.row(types.KeyboardButton("👤 Admin qo'shish"), types.KeyboardButton("📊 Statistika"))
    markup.row(types.KeyboardButton("⬅️ Bosh menyu"))
    return markup

# ----------------- 4. BOT MANTIQI (MUKAMMAL QIDIRUV) -----------------
def clean_text(text):
    """Matn ichidagi har xil belgilarni qidiruv muammosiz ishlashi uchun tozalash"""
    if not text: return ""
    return text.lower().replace("'", "").replace("`", "").replace("’", "").replace("‘", "").replace("o'", "o").replace("g'", "g").replace("-", " ").strip()

@bot.message_handler(commands=['start'])
def start_cmd(message):
    user_id = message.chat.id
    text_args = message.text.split()
    
    if len(text_args) > 1 and text_args[1].startswith("show_"):
        anime_key = text_args[1].replace("show_", "")
        anime = KOD_ICHIDAGI_ANIMELER.get(anime_key)
        if anime:
            text = f"🎬 <b>{anime['name']}</b>\n\n🎭 Janr: {anime['genre']}\n📝 Tavsif: {anime['desc']}\n\n📁 <b>Fasllar ro'yxati:</b>"
            markup = types.InlineKeyboardMarkup()
            
            if "seasons" in anime and anime["seasons"]:
                for s_name in anime["seasons"].keys():
                    markup.add(types.InlineKeyboardButton(text=f"📂 {s_name}", callback_data=f"se_{anime_key}_{s_name}"))
            else:
                markup.add(types.InlineKeyboardButton(text="📂 1-fasl (Hozircha bo'sh)", callback_data=f"se_{anime_key}_1-fasl"))
                
            markup.add(types.InlineKeyboardButton(text="⬅️ Bosh menyuga", callback_data="u_list"))
            try:
                bot.send_photo(user_id, photo=anime["poster"], caption=text, reply_markup=markup, parse_mode="HTML")
            except:
                bot.send_message(user_id, text, reply_markup=markup, parse_mode="HTML")
            return
        else:
            bot.send_message(user_id, "❌ Anime topilmadi.")
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
        bot.send_message(message.chat.id, f"📊 Jami animelar: {len(KOD_ICHIDAGI_ANIMELER)} ta")

@bot.message_handler(func=lambda m: m.text == "🔍 Qidirish")
def search_start(message):
    user_states[message.chat.id] = {"step": "searching"}
    bot.send_message(message.chat.id, "🔍 Qidirayotgan anime nomini kiriting:")

@bot.message_handler(func=lambda m: m.text == "🆕 Yangi")
def show_new_anime(message):
    if not KOD_ICHIDAGI_ANIMELER: return
    markup = types.InlineKeyboardMarkup()
    keys = list(KOD_ICHIDAGI_ANIMELER.keys())
    for k in keys[-5:]:
        markup.add(types.InlineKeyboardButton(text=KOD_ICHIDAGI_ANIMELER[k]["name"], callback_data=f"show_{k}"))
    bot.send_message(message.chat.id, "🆕 Yangi qo'shilgan animelar:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "🔥 Mashhur")
def show_popular_anime(message):
    if not KOD_ICHIDAGI_ANIMELER: return
    markup = types.InlineKeyboardMarkup()
    keys = list(KOD_ICHIDAGI_ANIMELER.keys())
    for k in keys[:5]:
        markup.add(types.InlineKeyboardButton(text=KOD_ICHIDAGI_ANIMELER[k]["name"], callback_data=f"show_{k}"))
    bot.send_message(message.chat.id, "🔥 Mashhur animelar:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "ℹ️ Yordam")
def help_cmd(message):
    bot.send_message(message.chat.id, "ℹ️ Bot orqali kanaldagi animelarni fasl va qismlarga bo'lingan holda tomosha qilishingiz mumkin.")

@bot.message_handler(func=lambda m: m.text == "👤 Admin qo'shish")
def add_admin_start(message):
    if message.chat.id == SUPER_ADMIN:
        user_states[message.chat.id] = {"step": "add_admin"}
        bot.send_message(message.chat.id, "Yangi admin ID raqamini yozing:")

@bot.message_handler(content_types=['text'])
def handle_inputs(message):
    user_id = message.chat.id
    if user_id not in user_states: return
    
    state = user_states[user_id]
    step = state["step"]
    
    if step == "searching":
        query = clean_text(message.text)
        # Endi "Omad", "omadsizning", "qoshni" barcha usullarda qidiruv mukammal ishlaydi!
        results = {k: v for k, v in KOD_ICHIDAGI_ANIMELER.items() if query in clean_text(v["name"])}
        
        if results:
            markup = types.InlineKeyboardMarkup()
            for k, v in results.items():
                markup.add(types.InlineKeyboardButton(text=v["name"], callback_data=f"show_{k}"))
            bot.send_message(user_id, "🔍 Topilgan natijalar:", reply_markup=markup)
        else:
            bot.send_message(user_id, "❌ Hech narsa topilmadi. Iltimos nomini to'g'ri yozganingizni tekshiring.")
        del user_states[user_id]

    elif step == "add_admin":
        try:
            new_id = int(message.text)
            if new_id not in admins_list:
                admins_list.append(new_id)
                with open(ADMIN_FILE, "w") as f:
                    json.dump(admins_list, f)
                bot.send_message(user_id, "✅ Yangi admin ro'yxatga qo'shildi!")
        except: pass
        del user_states[user_id]

@bot.message_handler(func=lambda m: m.text == "📚 Anime")
def user_anime_list(message):
    if not KOD_ICHIDAGI_ANIMELER:
        bot.send_message(message.chat.id, "⚠️ Hozircha bazada animelar mavjud emas.")
        return
    markup = types.InlineKeyboardMarkup()
    for k, v in KOD_ICHIDAGI_ANIMELER.items():
        markup.add(types.InlineKeyboardButton(text=v["name"], callback_data=f"show_{k}"))
    bot.send_message(message.chat.id, "📚 Jamlanma — Kerakli animeni tanlang:", reply_markup=markup)

@bot.callback_query_handler(func=lambda c: c.data.startswith("show_"))
def user_show_anime(call):
    anime_key = call.data.replace("show_", "")
    anime = KOD_ICHIDAGI_ANIMELER.get(anime_key)
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
    try:
        bot.send_photo(call.message.chat.id, photo=anime["poster"], caption=text, reply_markup=markup, parse_mode="HTML")
    except:
        bot.send_message(call.message.chat.id, text, reply_markup=markup, parse_mode="HTML")

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
    
    if ak in KOD_ICHIDAGI_ANIMELER and "seasons" in KOD_ICHIDAGI_ANIMELER[ak] and sn in KOD_ICHIDAGI_ANIMELER[ak]["seasons"]:
        episodes = KOD_ICHIDAGI_ANIMELER[ak]["seasons"][sn]
        for ep_name in sorted(episodes.keys()):
            clean_ep = ep_name.replace("-qism", "").strip()
            buttons.append(types.InlineKeyboardButton(text=clean_ep, callback_data=f"play_{ak}_{sn}_{ep_name}"))
            
    if buttons:
        markup.add(*buttons)
        text = f"🍿 <b>{KOD_ICHIDAGI_ANIMELER[ak]['name']}</b> - {sn} qismlari:"
    else:
        text = f"🍿 <b>{KOD_ICHIDAGI_ANIMELER[ak]['name']}</b> - {sn}\n\n⚠️ <i>Ushbu faslga hali qismlar yuklanmagan.</i>"
        
    markup.add(types.InlineKeyboardButton(text="⬅️ Fasllarga qaytish", callback_data=f"show_{ak}"))
    try: bot.delete_message(call.message.chat.id, call.message.message_id)
    except: pass
    bot.send_message(call.message.chat.id, text, reply_markup=markup, parse_mode="HTML")

@bot.callback_query_handler(func=lambda c: c.data.startswith("play_"))
def user_play_video(call):
    parts = call.data.split("_")
    ak, sn, en = parts[1], parts[2], parts[3]
    if ak in KOD_ICHIDAGI_ANIMELER and sn in KOD_ICHIDAGI_ANIMELER[ak]["seasons"] and en in KOD_ICHIDAGI_ANIMELER[ak]["seasons"][sn]:
        video_id = KOD_ICHIDAGI_ANIMELER[ak]["seasons"][sn][en]
        try:
            bot.send_video(call.message.chat.id, video=video_id, caption=f"🎬 {KOD_ICHIDAGI_ANIMELER[ak]['name']}\n🍿 {sn} | {en}")
        except Exception as e:
            bot.send_message(call.message.chat.id, f"❌ Videoni yuborishda xato: {e}")
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
    keep_alive()
    bot.infinity_polling(skip_pending=True)

