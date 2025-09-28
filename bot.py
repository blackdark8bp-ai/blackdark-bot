import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ================== الإعدادات ==================
BOT_TOKEN = "8270195922:AAGDVz_mL8FOJta3NnnNSZTm1m-5guzba4Y"
DEVELOPER_ID = 6597567561  # مكان تجميع المشاكل/الاقتراحات/الصور

# ================== اللوج ==================
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# ================== التخزين المؤقت ==================
user_language = {}  # user_id -> "ar" or "en"
user_state = {}     # user_id -> {"mode": "issue/suggestion/win", "messages": []}

# ================== /start ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("العربية", callback_data="lang_ar"),
            InlineKeyboardButton("English", callback_data="lang_en"),
        ]
    ]
    text = "اهلا بك في بوت بلاك دارك 👋\nWelcome to Black Dark Bot 👋\n\nالرجاء اختيار اللغة:\nPlease choose your language:"
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

# ================== القائمة الرئيسية ==================
def main_menu(lang="ar"):
    if lang == "ar":
        keyboard = [
            [
                InlineKeyboardButton("📩 إرسال المشكلة", callback_data="issue"),
                InlineKeyboardButton("💡 إرسال اقتراحات", callback_data="suggestion"),
                InlineKeyboardButton("🥳 إرسال صور الفوز", callback_data="win"),
            ]
        ]
        return "اختر من القائمة:", InlineKeyboardMarkup(keyboard)
    else:
        keyboard = [
            [
                InlineKeyboardButton("📩 Send Issue", callback_data="issue"),
                InlineKeyboardButton("💡 Send Suggestion", callback_data="suggestion"),
                InlineKeyboardButton("🥳 Send Winning Pic", callback_data="win"),
            ]
        ]
        return "Choose from the menu:", InlineKeyboardMarkup(keyboard)

# ================== اختيار اللغة ==================
async def choose_lang(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = query.data.split("_")[1]
    user_language[query.from_user.id] = lang

    text, keyboard = main_menu(lang)
    try:
        await query.edit_message_text(text, reply_markup=keyboard)
    except:
        pass  # يتجاهل خطأ "Message is not modified"

# ================== التعامل مع الأزرار ==================
async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    lang = user_language.get(user_id, "ar")

    if query.data == "issue":
        user_state[user_id] = {"mode": "issue", "messages": []}
        if lang == "ar":
            text = "يرجى إرسال المشكلة أو مقطع فيديو يوضحها 👇\n\nبعد الانتهاء اضغط زر ✅ إرسال المشكلة"
            keyboard = [[InlineKeyboardButton("✅ إرسال المشكلة", callback_data="send")],
                        [InlineKeyboardButton("🔙 رجوع", callback_data="back")]]
        else:
            text = "Please send your issue or a video explaining it 👇\n\nWhen finished, press ✅ Send Issue"
            keyboard = [[InlineKeyboardButton("✅ Send Issue", callback_data="send")],
                        [InlineKeyboardButton("🔙 Back", callback_data="back")]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == "suggestion":
        user_state[user_id] = {"mode": "suggestion", "messages": []}
        if lang == "ar":
            text = "اكتب اقتراحك وسنقوم بمراجعته 👇\n\nبعد الانتهاء اضغط زر ✅ إرسال الاقتراح"
            keyboard = [[InlineKeyboardButton("✅ إرسال الاقتراح", callback_data="send")],
                        [InlineKeyboardButton("🔙 رجوع", callback_data="back")]]
        else:
            text = "Please type your suggestion 👇\n\nWhen finished, press ✅ Send Suggestion"
            keyboard = [[InlineKeyboardButton("✅ Send Suggestion", callback_data="send")],
                        [InlineKeyboardButton("🔙 Back", callback_data="back")]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == "win":
        user_state[user_id] = {"mode": "win", "messages": []}
        if lang == "ar":
            text = "أرسل صورة فوزك 🎉 وسنحتفظ بها ضمن قائمة الإنجازات 👇\n\nبعد الانتهاء اضغط زر ✅ إرسال الصورة"
            keyboard = [[InlineKeyboardButton("✅ إرسال الصورة", callback_data="send")],
                        [InlineKeyboardButton("🔙 رجوع", callback_data="back")]]
        else:
            text = "Send your winning screenshot 🎉 We’ll add it to the achievements 👇\n\nWhen finished, press ✅ Send Pic"
            keyboard = [[InlineKeyboardButton("✅ Send Pic", callback_data="send")],
                        [InlineKeyboardButton("🔙 Back", callback_data="back")]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == "send":
        state = user_state.get(user_id)
        if not state or not state["messages"]:
            return
        msgs = state["messages"]
        mode = state["mode"]

        # تجهيز النص
        if lang == "ar":
            confirm = "✅ تم إرسال طلبك للمطور بنجاح."
        else:
            confirm = "✅ Your request has been sent to the developer."

        # إرسال للمطور
        user = query.from_user
        header = f"📩 New {mode} from {user.first_name} (@{user.username}):\n\n"
        await context.bot.send_message(DEVELOPER_ID, header)
        for m in msgs:
            if m["type"] == "text":
                await context.bot.send_message(DEVELOPER_ID, m["data"])
            elif m["type"] == "photo":
                await context.bot.send_photo(DEVELOPER_ID, m["data"])
            elif m["type"] == "video":
                await context.bot.send_video(DEVELOPER_ID, m["data"])

        await query.edit_message_text(confirm)
        user_state[user_id] = {"mode": None, "messages": []}

    elif query.data == "back":
        text, keyboard = main_menu(lang)
        try:
            await query.edit_message_text(text, reply_markup=keyboard)
        except:
            pass

# ================== استقبال الرسائل ==================
async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    state = user_state.get(user_id)
    if not state or not state["mode"]:
        return

    if update.message.text:
        state["messages"].append({"type": "text", "data": update.message.text})
    elif update.message.photo:
        photo = update.message.photo[-1].file_id
        state["messages"].append({"type": "photo", "data": photo})
    elif update.message.video:
        state["messages"].append({"type": "video", "data": update.message.video.file_id})

# ================== تشغيل البوت ==================
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(choose_lang, pattern="^lang_"))
    app.add_handler(CallbackQueryHandler(menu_handler))
    app.add_handler(MessageHandler(filters.ALL, handle_messages))
    app.run_polling()

if __name__ == "__main__":
    main()
