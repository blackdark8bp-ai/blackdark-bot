import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# بياناتك
BOT_TOKEN = "8270195922:AAGDVz_mL8FOJta3NnnNSZTm1m-5guzba4Y"
DEV_ID = 6597567561

# Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ذاكرة مؤقتة
user_data = {}

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🇸🇦 العربية", callback_data="lang_ar")],
        [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = "👋 أهلاً بك في بوت بلاك دارك\nPlease choose your language 👇"
    await update.message.reply_text(text, reply_markup=reply_markup)

# قائمة رئيسية
def main_menu(lang="ar"):
    if lang == "ar":
        keyboard = [
            [InlineKeyboardButton("📩 إرسال المشكلة", callback_data="issue")],
            [InlineKeyboardButton("💡 إرسال اقتراحات", callback_data="suggestion")],
            [InlineKeyboardButton("🥳 إرسال صور الفوز", callback_data="win")]
        ]
    else:
        keyboard = [
            [InlineKeyboardButton("📩 Send Issue", callback_data="issue")],
            [InlineKeyboardButton("💡 Send Suggestion", callback_data="suggestion")],
            [InlineKeyboardButton("🥳 Send Win Screenshot", callback_data="win")]
        ]
    return InlineKeyboardMarkup(keyboard)

# رجوع
def back_button(lang="ar"):
    if lang == "ar":
        return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 الرجوع", callback_data="back")]])
    else:
        return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="back")]])

# التعامل مع الأزرار
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    choice = query.data
    user_id = query.from_user.id

    # اختيار اللغة
    if choice == "lang_ar":
        user_data[user_id] = {"lang": "ar", "mode": None, "messages": []}
        await query.edit_message_text("مرحباً بك! اختر من القائمة 👇", reply_markup=main_menu("ar"))
    elif choice == "lang_en":
        user_data[user_id] = {"lang": "en", "mode": None, "messages": []}
        await query.edit_message_text("Welcome! Choose from the menu 👇", reply_markup=main_menu("en"))

    # مشكلة
    elif choice == "issue":
        lang = user_data[user_id]["lang"]
        user_data[user_id]["mode"] = "issue"
        user_data[user_id]["messages"] = []
        text = "يرجى إرسال مشكلتك 👇" if lang == "ar" else "Please send your issue 👇"
        keyboard = [
            [InlineKeyboardButton("✅ إرسال المشكلة", callback_data="send_issue")],
            [InlineKeyboardButton("🔙 الرجوع", callback_data="back")]
        ]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

    # اقتراح
    elif choice == "suggestion":
        lang = user_data[user_id]["lang"]
        user_data[user_id]["mode"] = "suggestion"
        user_data[user_id]["messages"] = []
        text = "اكتب اقتراحك 👇" if lang == "ar" else "Please type your suggestion 👇"
        keyboard = [
            [InlineKeyboardButton("✅ إرسال الاقتراح", callback_data="send_suggestion")],
            [InlineKeyboardButton("🔙 الرجوع", callback_data="back")]
        ]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

    # صورة فوز
    elif choice == "win":
        lang = user_data[user_id]["lang"]
        user_data[user_id]["mode"] = "win"
        user_data[user_id]["messages"] = []
        text = "أرسل صورة فوزك 🎉" if lang == "ar" else "Send your winning screenshot 🎉"
        keyboard = [
            [InlineKeyboardButton("✅ إرسال الصورة", callback_data="send_win")],
            [InlineKeyboardButton("🔙 الرجوع", callback_data="back")]
        ]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

    # رجوع
    elif choice == "back":
        lang = user_data.get(user_id, {}).get("lang", "ar")
        msg = "مرحباً بك! اختر من القائمة 👇" if lang == "ar" else "Welcome! Choose from the menu 👇"
        await query.edit_message_text(msg, reply_markup=main_menu(lang))

    # إرسال نهائي
    elif choice.startswith("send_"):
        lang = user_data[user_id]["lang"]
        mode = user_data[user_id]["mode"]
        messages = user_data[user_id]["messages"]

        if not messages:
            msg = "❌ لم ترسل أي شيء!" if lang == "ar" else "❌ You didn’t send anything!"
            await query.edit_message_text(msg, reply_markup=back_button(lang))
            return

        # إرسال للمطور
        user = query.from_user
        header = f"📩 New {mode} from {user.first_name} (@{user.username})\n\n"
        await context.bot.send_message(chat_id=DEV_ID, text=header)

        for m in messages:
            if m["type"] == "text":
                await context.bot.send_message(chat_id=DEV_ID, text=m["content"])
            elif m["type"] == "photo":
                await context.bot.send_photo(chat_id=DEV_ID, photo=m["content"])
            elif m["type"] == "video":
                await context.bot.send_video(chat_id=DEV_ID, video=m["content"])

        # رد للمستخدم
        confirm = {
            "issue": ("تم إرسال مشكلتك ✅", "Your issue has been sent ✅"),
            "suggestion": ("تم إرسال اقتراحك ✅", "Your suggestion has been sent ✅"),
            "win": ("تم إرسال صورتك ✅", "Your screenshot has been sent ✅"),
        }

        ar_msg, en_msg = confirm[mode]
        await query.edit_message_text(ar_msg if lang == "ar" else en_msg, reply_markup=main_menu(lang))

        user_data[user_id]["mode"] = None
        user_data[user_id]["messages"] = []

# استقبال رسائل المستخدم (نص/صورة/فيديو)
async def collect_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in user_data or not user_data[user_id].get("mode"):
        return

    if update.message.text:
        user_data[user_id]["messages"].append({"type": "text", "content": update.message.text})
    elif update.message.photo:
        file_id = update.message.photo[-1].file_id
        user_data[user_id]["messages"].append({"type": "photo", "content": file_id})
    elif update.message.video:
        file_id = update.message.video.file_id
        user_data[user_id]["messages"].append({"type": "video", "content": file_id})

# تشغيل البوت
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.ALL, collect_messages))
    app.run_polling()

if __name__ == "__main__":
    main()
