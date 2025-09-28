from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# بياناتك
TOKEN = "8270195922:AAGDVz_mL8FOJta3NnnNSZTm1m-5guzba4Y"
DEV_ID = 6597567561

# تخزين بيانات المستخدم (اللغة + الحالة + الرسائل)
user_data = {}

# ------------------- الأوامر الأساسية -------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("العربية", callback_data="lang_ar"),
         InlineKeyboardButton("English", callback_data="lang_en")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "👋 اهلاً بك في بوت Black Dark\nWelcome to Black Dark Bot 👋\n\n"
        "الرجاء اختيار اللغة / Please select a language:",
        reply_markup=reply_markup
    )

# ------------------- اختيار اللغة -------------------

async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat.id

    # تعيين اللغة
    if query.data == "lang_ar":
        user_data[chat_id] = {"lang": "ar", "state": None, "buffer": []}
        text = "✅ تم اختيار اللغة العربية.\n\nاختر من القائمة:"
    else:
        user_data[chat_id] = {"lang": "en", "state": None, "buffer": []}
        text = "✅ English selected.\n\nPlease choose from the menu:"

    await show_main_menu(query, text)

# ------------------- القائمة الرئيسية -------------------

async def show_main_menu(query, text):
    keyboard = [
        [InlineKeyboardButton("📩 إرسال المشكلة", callback_data="problem"),
         InlineKeyboardButton("💡 إرسال اقتراحات", callback_data="suggestion")],
        [InlineKeyboardButton("🥳 إرسال صور الفوز", callback_data="win")]
    ]
    await query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard))

# ------------------- معالجة الأزرار -------------------

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat.id
    lang = user_data.get(chat_id, {}).get("lang", "ar")

    if query.data == "problem":
        user_data[chat_id]["state"] = "problem"
        user_data[chat_id]["buffer"] = []
        msg = "يرجى إرسال المشكلة أو مقطع فيديو يوضحها 👇\n\nبعد الانتهاء اضغط ✅ إرسال المشكلة" if lang == "ar" else \
              "Please send your issue or a clear video 👇\n\nWhen finished, press ✅ Send Problem"
        keyboard = [[InlineKeyboardButton("✅ إرسال المشكلة" if lang=="ar" else "✅ Send Problem", callback_data="send_problem")],
                    [InlineKeyboardButton("🔙 رجوع" if lang=="ar" else "🔙 Back", callback_data="back")]]
        await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == "suggestion":
        user_data[chat_id]["state"] = "suggestion"
        user_data[chat_id]["buffer"] = []
        msg = "اكتب اقتراحك وسنقوم بمراجعته 👇\n\nبعد الانتهاء اضغط ✅ إرسال الاقتراح" if lang == "ar" else \
              "Please type your suggestion 👇\n\nWhen finished, press ✅ Send Suggestion"
        keyboard = [[InlineKeyboardButton("✅ إرسال الاقتراح" if lang=="ar" else "✅ Send Suggestion", callback_data="send_suggestion")],
                    [InlineKeyboardButton("🔙 رجوع" if lang=="ar" else "🔙 Back", callback_data="back")]]
        await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == "win":
        user_data[chat_id]["state"] = "win"
        user_data[chat_id]["buffer"] = []
        msg = "أرسل صورة فوزك 🎉 👇\n\nبعد الانتهاء اضغط ✅ إرسال الصورة" if lang == "ar" else \
              "Send your winning screenshot 🎉 👇\n\nWhen finished, press ✅ Send Screenshot"
        keyboard = [[InlineKeyboardButton("✅ إرسال الصورة" if lang=="ar" else "✅ Send Screenshot", callback_data="send_win")],
                    [InlineKeyboardButton("🔙 رجوع" if lang=="ar" else "🔙 Back", callback_data="back")]]
        await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == "send_problem":
        await forward_to_dev(update, context, chat_id, "problem")

    elif query.data == "send_suggestion":
        await forward_to_dev(update, context, chat_id, "suggestion")

    elif query.data == "send_win":
        await forward_to_dev(update, context, chat_id, "win")

    elif query.data == "back":
        text = "اختر من القائمة:" if lang == "ar" else "Please choose from the menu:"
        await show_main_menu(query, text)

# ------------------- استقبال الرسائل -------------------

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat.id
    if chat_id not in user_data or not user_data[chat_id].get("state"):
        return
    # خزّن الرسائل (نصوص/صور/فيديو)
    user_data[chat_id]["buffer"].append(update.message)

# ------------------- إرسال للـ Dev -------------------

async def forward_to_dev(update, context, chat_id, msg_type):
    lang = user_data[chat_id]["lang"]
    msgs = user_data[chat_id]["buffer"]

    if not msgs:
        txt = "❌ لم يتم إرسال أي محتوى" if lang == "ar" else "❌ No content sent"
        await update.callback_query.edit_message_text(txt)
        return

    # تفاصيل المرسل
    user = msgs[0].from_user
    header = f"📩 نوع الإرسال: {msg_type}\n👤 من: {user.first_name} (@{user.username})\n🆔 ID: {user.id}\n\n"

    # إرسال للمطور
    await context.bot.send_message(DEV_ID, header)
    for m in msgs:
        if m.text:
            await context.bot.send_message(DEV_ID, m.text)
        elif m.photo:
            await context.bot.send_photo(DEV_ID, m.photo[-1].file_id, caption=m.caption or "")
        elif m.video:
            await context.bot.send_video(DEV_ID, m.video.file_id, caption=m.caption or "")

    # تأكيد للمستخدم
    confirm = {
        "problem": ("تم إرسال مشكلتك للمطور بنجاح ✅", "Your issue has been sent successfully ✅"),
        "suggestion": ("تم إرسال اقتراحك للمطور بنجاح ✅", "Your suggestion has been sent successfully ✅"),
        "win": ("تم إرسال صورة فوزك بنجاح 🎉", "Your win screenshot has been sent successfully 🎉")
    }

    text = confirm[msg_type][0] if lang == "ar" else confirm[msg_type][1]
    await update.callback_query.edit_message_text(text)

    # تصفير الحالة
    user_data[chat_id]["state"] = None
    user_data[chat_id]["buffer"] = []

# ------------------- التشغيل -------------------

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(set_language, pattern="^lang_"))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.ALL, handle_message))

    print("✅ Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
