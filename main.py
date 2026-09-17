import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from datetime import datetime
import pytz

# STARTUP SOZLAMALARI
ADMIN_ID = "7923092518"  # Sizning shaxsiy Telegram ID raqamingiz ulandi!
TOKEN = os.environ.get('BOT_TOKEN', 'Sizning_Bot_Tokeni')

bot = telebot.TeleBot(TOKEN)
toshkent_tz = pytz.timezone('Asia/Tashkent')
START_TIME = datetime.now(toshkent_tz)

# FOYDALANUVCHILAR BAZASI (Statistika uchun)
users_db = {}

# 1. ASOSIY 3 TA MENYU TUGMALARI
def main_menu_keyboard(user_id):
    markup = InlineKeyboardMarkup(row_width=1)
    # Mini App havolasi (keyingi qadamda GitHub Pages yoqqanimizda aniq ishlaydi)
    mini_app_url = "https://github.io"
    
    markup.add(
        InlineKeyboardButton("📱 Apex Fin Mini App", web_app=WebAppInfo(url=mini_app_url)),
        InlineKeyboardButton("📊 Mening holatim", callback_data="mening_holatim"),
        InlineKeyboardButton("✉️ Admin bilan aloqa (Podderjka)", callback_data="admin_aloqa")
    )
    
    # Faqat sizga (Adminingizga) ko'rinadigan yashirin Statistika paneli
    if str(user_id) == str(ADMIN_ID):
        markup.add(InlineKeyboardButton("⚙️ Admin Panel (Statistika)", callback_data="admin_panel"))
        
    return markup

# 2. /START BUYRUG'I
@bot.message_handler(commands=['start'])
def send_welcome(message):
    try:
        user_id = message.from_user.id
        user_name = message.from_user.first_name
        
        # Ro'yxatdan o'tkazish (Statistika hisoblanishi uchun)
        if user_id not in users_db:
            users_db[user_id] = {
                "name": user_name,
                "balance": 10000000,
                "xaridlar": []
            }
            
        welcome_text = (
            f"👋 *Salom, {user_name}!*\n\n"
            f"🌐 *Apex Terminal Demo* aksiyalar monitoringi tizimiga xush kelibsiz.\n\n"
            f"Kerakli bo'limni tanlang: 👇"
        )
        bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=main_menu_keyboard(user_id))
    except Exception: pass

# 3. TUGMALAR ISHLOVCHISI (CALLBACK)
@bot.callback_query_handler(func=lambda call: True)
def callback_listener(call):
    try:
        user_id = call.from_user.id
        bot.answer_callback_query(call.id)
        
        # 1-Menyu: Mening holatim
        if call.data == "mening_holatim":
            user_data = users_db.get(user_id, {"balance": 10000000, "xaridlar": []})
            balans = user_data["balance"]
            
            holat_text = (
                "📊 *Sizning hozirgi moliyaviy holatingiz:*\n"
                "===================================\n"
                f"💰 Virtual balans: `{balans:,} so'm`\n"
                "🛍️ Oxirgi xaridlar: `Hozircha xaridlar mavjud emas`\n"
                "📉 Umumiy foyda/zarar: `0%`\n"
                "===================================\n"
                "ℹ️ _Mini App orqali aksiya savdo tizimi tez orada ishga tushadi._"
            ).replace(",", " ")
            
            back_markup = InlineKeyboardMarkup()
            back_markup.add(InlineKeyboardButton("⬅️ Orqaga", callback_data="bosh_menyu"))
            bot.edit_message_text(holat_text, call.message.chat.id, call.message.message_id, parse_mode="Markdown", reply_markup=back_markup)
            
        # 2-Menyu: Admin bilan aloqa
        elif call.data == "admin_aloqa":
            feedback_text = (
                "✉️ *Admin bilan aloqa (Qo'llab-quvvatlash tizimi)*\n\n"
                "Bot bo'yicha takliflaringiz bo'lsa, pastdagi tugmani bosing va izoh qoldiring. 👇"
            )
            feedback_markup = InlineKeyboardMarkup()
            feedback_markup.add(
                InlineKeyboardButton("✍️ Izoh qoldirish", callback_data="yozish_admin"),
                InlineKeyboardButton("⬅️ Orqaga", callback_data="bosh_menyu")
            )
            bot.edit_message_text(feedback_text, call.message.chat.id, call.message.message_id, parse_mode="Markdown", reply_markup=feedback_markup)
            
        elif call.data == "yozish_admin":
            msg = bot.send_message(call.message.chat.id, "📝 *Iltimos, o'z izohingizni matn ko'rinishida yozib yuboring:*", parse_mode="Markdown")
            bot.register_next_step_handler(msg, forward_to_admin)
            
        # 3-Menyu: Admin Panel (Siz so'ragan Statistika)
        elif call.data == "admin_panel":
            if str(user_id) != str(ADMIN_ID): return
            hozir = datetime.now(toshkent_tz)
            farq = hozir - START_TIME
            kun, soat, daqiqa = farq.days, farq.seconds // 3600, (farq.seconds % 3600) // 60
            
            admin_text = (
                "⚙️ *APEX TERMINAL — ADMIN PANEL*\n"
                "===================================\n"
                f"👥 Jami foydalanuvchilar: `{len(users_db)} ta`\n"
                f"⏳ Server ishlash vaqti: `{kun} kun, {soat} soat, {daqiqa} daqiqa`\n"
                "===================================\n"
                "📊 _Tizim yangi yuklamalarga tayyor!_"
            )
            back_markup = InlineKeyboardMarkup()
            back_markup.add(InlineKeyboardButton("⬅️ Orqaga", callback_data="bosh_menyu"))
            bot.edit_message_text(admin_text, call.message.chat.id, call.message.message_id, parse_mode="Markdown", reply_markup=back_markup)
            
        elif call.data == "bosh_menyu":
            bot.edit_message_text("📊 Kerakli bo'limni tanlang:", call.message.chat.id, call.message.message_id, reply_markup=main_menu_keyboard(user_id))
            
    except Exception: pass

# 4. IZOHLARNI ADMINGA YUBORISH
def forward_to_admin(message):
    try:
        user_text = message.text
        user_id = message.from_user.id
        user_name = message.from_user.first_name
        
        if not user_text:
            bot.send_message(message.chat.id, "❌ Faqat matn kiriting!", reply_markup=main_menu_keyboard(user_id))
            return

        admin_message = (
            f"🔔 *YANGI IZOH / FEEDBACK!*\n"
            f"===================================\n"
            f"👤 Kimdan: {user_name}\n"
            f"🆔 ID: `{user_id}`\n"
            f"📝 Xabar: _{user_text}_\n"
            f"==================================="
        )
        bot.send_message(ADMIN_ID, admin_message, parse_mode="Markdown")
        bot.send_message(message.chat.id, "✅ *Rahmat! Izohingiz adminga muvaffaqiyatli yetkazildi.*", parse_mode="Markdown", reply_markup=main_menu_keyboard(user_id))
    except Exception: pass
