import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# === بيانات البوت ===
TOKEN = "8270195922:AAGDVz_mL8FOJta3NnnNSZTm1m-5guzba4Y"
ADMIN_ID = 6597567561

# === إعداد اللوج ===
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# تخزين اللغة المختارة لكل مستخدم
user_languages = {}


# === /start ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("🇸🇦 العربية", callback_data="lang_ar"),
            InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = "اهلا بك في بوت بلاك دارك 👋\nالرجاء اختيار اللغه\n\nWelcome to Black Dark Bot 👋\nPlease choose your language"

    await update.message.reply_text(text, reply_markup=reply_markup)


# === اختيار اللغة ===
async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "lang_ar":
        user_languages[query.from_user.id] = "ar"
        keyboard = [
            [InlineKeyboardButton("🚨 إرسال مشكله", callback_data="send_issue")],
            [InlineKeyboardButton("💡 إرسال اقتراح", callback_data="send_suggestion")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("✅ تم اختيار اللغة: العربية", reply_markup=reply_markup)

    elif query.data == "lang_en":
        user_languages[query.from_user.id] = "en"
        keyboard = [
            [InlineKeyboardButton("🚨 Send Issue", callback_data="send_issue")],
            [InlineKeyboardButton("💡 Send Suggestion", callback_data="send_suggestion")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("✅ Language selected: English", reply_markup=reply_markup)


# === عند الضغط على زر (مشكلة أو اقتراح) ===
async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = user_languages.get(query.from_user.id, "ar")

    if query.data == "send_issue":
        if lang == "ar":
            await query.edit_message_text("✍️ اكتب مشكلتك وسنقوم بمراجعتها.")
        else:
            await query.edit_message_text("✍️ Please type your issue and we will review it.")

    elif query.data == "send_suggestion":
        if lang == "ar":
            await query.edit_message_text("💡 اكتب اقتراحك وسنقوم بمراجعته.")
        else:
            await query.edit_message_text("💡 Please type your suggestion and we will review it.")


# === استقبال الرسائل من المستخدم ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    lang = user_languages.get(user_id, "ar")

    # إرسال الرسالة إلى الأدمن
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"📩 رسالة جديدة من {update.message.from_user.first_name} ({user_id}):\n\n{update.message.text}"
    )

    # الرد على المستخدم
    if lang == "ar":
        await update.message.reply_text("✅ تم استلام رسالتك، شكرًا لتواصلك.")
    else:
        await update.message.reply_text("✅ Your message has been received, thank you.")


# === Main ===
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(set_language, pattern="^lang_"))
    app.add_handler(CallbackQueryHandler(menu_handler, pattern="^(send_issue|send_suggestion)$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ البوت شغال ...")
    app.run_polling()


if __name__ == "__main__":
    main()
