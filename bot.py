import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, ConversationHandler

# --- إعدادات البوت ---
TOKEN = "8270195922:AAGDVz_mL8FOJta3NnnNSZTm1m-5guzba4Y"
DEV_ID = 6597567561

# --- التتبع ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- ثوابت ---
LANGUAGE, MAIN_MENU, ISSUE, SUGGESTION, WIN = range(5)
user_language = {}

# --- أزرار ---
def language_keyboard():
    return ReplyKeyboardMarkup(
        [[KeyboardButton("العربية"), KeyboardButton("English")]],
        resize_keyboard=True, one_time_keyboard=True
    )

def main_menu_keyboard(lang):
    if lang == "ar":
        buttons = [
            [KeyboardButton("📩 إرسال المشكلة")],
            [KeyboardButton("💡 إرسال اقتراحات")],
            [KeyboardButton("🥳 إرسال صور الفوز")],
        ]
    else:
        buttons = [
            [KeyboardButton("📩 Send Issue")],
            [KeyboardButton("💡 Send Suggestion")],
            [KeyboardButton("🥳 Send Win Screenshot")],
        ]
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)

def confirm_keyboard(lang):
    if lang == "ar":
        return ReplyKeyboardMarkup([[KeyboardButton("✅ إرسال")], [KeyboardButton("🔙 رجوع")]], resize_keyboard=True)
    else:
        return ReplyKeyboardMarkup([[KeyboardButton("✅ Send")], [KeyboardButton("🔙 Back")]], resize_keyboard=True)

# --- دوال البداية ---
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "اهلا بك في بوت بلاك دارك\nWelcome to Black Dark Bot",
        reply_markup=language_keyboard()
    )
    return LANGUAGE

async def set_language(update: Update, context: CallbackContext):
    lang_choice = update.message.text
    if lang_choice == "العربية":
        user_language[update.effective_user.id] = "ar"
        await update.message.reply_text("مرحباً! اختر من القائمة 👇", reply_markup=main_menu_keyboard("ar"))
    else:
        user_language[update.effective_user.id] = "en"
        await update.message.reply_text("Welcome! Choose from the menu 👇", reply_markup=main_menu_keyboard("en"))
    return MAIN_MENU

# --- معالجة الأزرار الرئيسية ---
async def main_menu(update: Update, context: CallbackContext):
    lang = user_language.get(update.effective_user.id, "ar")
    text = update.message.text

    if text in ["📩 إرسال المشكلة", "📩 Send Issue"]:
        if lang == "ar":
            await update.message.reply_text("يرجى إرسال المشكلة أو مقطع فيديو يوضحها 👇", reply_markup=confirm_keyboard("ar"))
        else:
            await update.message.reply_text("Please send the issue or a video showing it 👇", reply_markup=confirm_keyboard("en"))
        return ISSUE

    elif text in ["💡 إرسال اقتراحات", "💡 Send Suggestion"]:
        if lang == "ar":
            await update.message.reply_text("اكتب اقتراحك وسنقوم بمراجعته 👇", reply_markup=confirm_keyboard("ar"))
        else:
            await update.message.reply_text("Please type your suggestion 👇", reply_markup=confirm_keyboard("en"))
        return SUGGESTION

    elif text in ["🥳 إرسال صور الفوز", "🥳 Send Win Screenshot"]:
        if lang == "ar":
            await update.message.reply_text("أرسل صورة فوزك 🎉", reply_markup=confirm_keyboard("ar"))
        else:
            await update.message.reply_text("Send your winning screenshot 🎉", reply_markup=confirm_keyboard("en"))
        return WIN

    return MAIN_MENU

# --- استقبال المشاكل ---
async def receive_issue(update: Update, context: CallbackContext):
    lang = user_language.get(update.effective_user.id, "ar")
    if update.message.text in ["✅ إرسال", "✅ Send"]:
        if lang == "ar":
            await update.message.reply_text("تم إرسال مشكلتك للمطور ✅", reply_markup=main_menu_keyboard("ar"))
        else:
            await update.message.reply_text("Your issue has been sent ✅", reply_markup=main_menu_keyboard("en"))
        await context.bot.send_message(
            DEV_ID,
            f"📩 مشكلة جديدة من {update.effective_user.full_name} (@{update.effective_user.username}):\n{context.user_data.get('issue','')}"
        )
        context.user_data.clear()
        return MAIN_MENU
    else:
        context.user_data['issue'] = update.message.text
        return ISSUE

# --- استقبال الاقتراحات ---
async def receive_suggestion(update: Update, context: CallbackContext):
    lang = user_language.get(update.effective_user.id, "ar")
    if update.message.text in ["✅ إرسال", "✅ Send"]:
        if lang == "ar":
            await update.message.reply_text("تم إرسال اقتراحك ✅", reply_markup=main_menu_keyboard("ar"))
        else:
            await update.message.reply_text("Your suggestion has been sent ✅", reply_markup=main_menu_keyboard("en"))
        await context.bot.send_message(
            DEV_ID,
            f"💡 اقتراح جديد من {update.effective_user.full_name} (@{update.effective_user.username}):\n{context.user_data.get('suggestion','')}"
        )
        context.user_data.clear()
        return MAIN_MENU
    else:
        context.user_data['suggestion'] = update.message.text
        return SUGGESTION

# --- استقبال صور الفوز ---
async def receive_win(update: Update, context: CallbackContext):
    lang = user_language.get(update.effective_user.id, "ar")
    if update.message.text in ["✅ إرسال", "✅ Send"]:
        if lang == "ar":
            await update.message.reply_text("تم إرسال صورة فوزك ✅", reply_markup=main_menu_keyboard("ar"))
        else:
            await update.message.reply_text("Your win screenshot has been sent ✅", reply_markup=main_menu_keyboard("en"))
        await context.bot.send_message(
            DEV_ID,
            f"🥳 صورة فوز جديدة من {update.effective_user.full_name} (@{update.effective_user.username})"
        )
        context.user_data.clear()
        return MAIN_MENU
    else:
        context.user_data['win'] = "screenshot sent"
        return WIN

# --- تشغيل البوت ---
def main():
    app = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            LANGUAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_language)],
            MAIN_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu)],
            ISSUE: [MessageHandler(filters.ALL & ~filters.COMMAND, receive_issue)],
            SUGGESTION: [MessageHandler(filters.ALL & ~filters.COMMAND, receive_suggestion)],
            WIN: [MessageHandler(filters.ALL & ~filters.COMMAND, receive_win)],
        },
        fallbacks=[CommandHandler("start", start)],
    )

    app.add_handler(conv_handler)
    app.run_polling()

if __name__ == "__main__":
    main()
