import logging
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# ================= إعدادات أساسية =================
TOKEN = "ضع_التوكن_هنا"
DEVELOPER_ID = 6597567561  # رقمك

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# نخزن لغة كل مستخدم
user_languages = {}
# نخزن الرسائل المؤقتة (مشكلة/اقتراح/صورة فوز)
user_states = {}

# ================= القوائم =================
def language_menu():
    keyboard = [
        [
            InlineKeyboardButton("العربية", callback_data="lang_ar"),
            InlineKeyboardButton("English", callback_data="lang_en")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

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

def confirm_menu(lang="ar", mode="issue"):
    if lang == "ar":
        text = "✅ إرسال المشكلة" if mode == "issue" else \
               "✅ إرسال الاقتراح" if mode == "suggestion" else \
               "✅ إرسال الصورة"
    else:
        text = "✅ Send Issue" if mode == "issue" else \
               "✅ Send Suggestion" if mode == "suggestion" else \
               "✅ Send Screenshot"
    keyboard = [[InlineKeyboardButton(text, callback_data=f"send_{mode}")]]
    return InlineKeyboardMarkup(keyboard)

# ================= أوامر البداية =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "👋 أهلا بك في بوت بلاك دارك\n"
        "الرجاء اختيار اللغة\n\n"
        "👋 Welcome to Black Dark Bot\n"
        "Please select your language"
    )
    await update.message.reply_text(welcome_text, reply_markup=language_menu())

# ================= اختيارات =================
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    # اختيار اللغة
    if query.data == "lang_ar":
        user_languages[user_id] = "ar"
        await query.edit_message_text("✅ تم اختيار اللغة العربية", reply_markup=main_menu("ar"))
    elif query.data == "lang_en":
        user_languages[user_id] = "en"
        await query.edit_message_text("✅ English language selected", reply_markup=main_menu("en"))

    # القوائم
    elif query.data in ["issue", "suggestion", "win"]:
        lang = user_languages.get(user_id, "ar")
        user_states[user_id] = {"mode": query.data, "messages": []}
        if query.data == "issue":
            text = "📝 يرجى إرسال المشكلة أو مقطع فيديو يوضحها 👇" if lang == "ar" else \
                   "📝 Please send the issue or a video showing it 👇"
        elif query.data == "suggestion":
            text = "💡 اكتب اقتراحك وسنقوم بمراجعته 👇" if lang == "ar" else \
                   "💡 Please type your suggestion 👇"
        else:
            text = "🥳 أرسل صورة فوزك 🎉 وسنحتفظ بها 👇" if lang == "ar" else \
                   "🥳 Send your winning screenshot 🎉 👇"

        await query.edit_message_text(text, reply_markup=confirm_menu(lang, query.data))

    # إرسال البيانات للمطور
    elif query.data.startswith("send_"):
        mode = query.data.replace("send_", "")
        state = user_states.get(user_id)
        lang = user_languages.get(user_id, "ar")
        if state and state["messages"]:
            user = query.from_user
            header = f"📩 رسالة جديدة من @{user.username or user.first_name}\n"
            header += f"النوع: {mode}\n\n" if lang == "ar" else f"Type: {mode}\n\n"
            for msg in state["messages"]:
                await context.bot.forward_message(DEVELOPER_ID, user_id, msg.message_id)
            await context.bot.send_message(DEVELOPER_ID, header)

            if lang == "ar":
                await query.edit_message_text("✅ تم إرسال رسالتك بنجاح وسيتم مراجعتها قريباً")
            else:
                await query.edit_message_text("✅ Your message has been sent successfully and will be reviewed soon")

            del user_states[user_id]
        else:
            if lang == "ar":
                await query.edit_message_text("⚠️ لم ترسل أي محتوى بعد!")
            else:
                await query.edit_message_text("⚠️ You haven't sent any content yet!")

# ================= حفظ رسائل المستخدم =================
async def save_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id in user_states:
        user_states[user_id]["messages"].append(update.message)

# ================= تشغيل البوت =================
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, save_messages))

    app.run_polling()

if __name__ == "__main__":
    main()
