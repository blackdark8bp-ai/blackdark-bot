import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application, CommandHandler, MessageHandler, ContextTypes, filters
)

# ============ إعدادات البوت ============
TOKEN = "8270195922:AAGDVz_mL8FOJta3NnnNSZTm1m-5guzba4Y"
ADMIN_ID = 6597567561  # ايدي المطور

# ============ تسجيل الأخطاء ============
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# ============ قوائم الأزرار ============
lang_menu = [["العربية", "English"]]

main_menu_ar = [["📩 إرسال المشكلة", "💡 إرسال اقتراحات", "🥳 إرسال صور الفوز"]]
main_menu_en = [["📩 Report Issue", "💡 Suggestions", "🥳 Winning Screenshots"]]

back_button_ar = [["🔙 الرجوع للقائمة الرئيسية"]]
back_button_en = [["🔙 Back to Main Menu"]]

send_button_ar = [["✅ إرسال المشكلة"], ["🔙 الرجوع للقائمة الرئيسية"]]
send_button_en = [["✅ Send Issue"], ["🔙 Back to Main Menu"]]

# ============ حالة المستخدم ============
user_state = {}  # user_id -> {"lang": "ar/en", "mode": "issue/suggestion/win", "messages": []}

# ============ أوامر البداية ============
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_state[user_id] = {"lang": None, "mode": None, "messages": []}
    await update.message.reply_text(
        "👋 أهلاً بك / Welcome!\n\n"
        "الرجاء اختيار اللغة / Please select your language:",
        reply_markup=ReplyKeyboardMarkup(lang_menu, resize_keyboard=True)
    )

# ============ اختيار اللغة ============
async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    if text == "العربية":
        user_state[user_id]["lang"] = "ar"
        await update.message.reply_text(
            "✅ تم اختيار اللغة العربية.\n"
            "اختر من القائمة 👇",
            reply_markup=ReplyKeyboardMarkup(main_menu_ar, resize_keyboard=True)
        )

    elif text == "English":
        user_state[user_id]["lang"] = "en"
        await update.message.reply_text(
            "✅ English selected.\n"
            "Choose from the menu 👇",
            reply_markup=ReplyKeyboardMarkup(main_menu_en, resize_keyboard=True)
        )

# ============ منطق الأزرار ============
async def handle_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    state = user_state.get(user_id, {"lang": None})

    if state["lang"] is None:
        return

    lang = state["lang"]
    text = update.message.text

    # ===== اللغة العربية =====
    if lang == "ar":
        if text == "📩 إرسال المشكلة":
            user_state[user_id]["mode"] = "issue"
            user_state[user_id]["messages"] = []
            await update.message.reply_text(
                "✍️ يرجى إرسال المشكلة أو مقطع فيديو يوضحها 👇\n\n"
                "بعد الانتهاء من تحديد المشكلة الرجاء الضغط على زر الإرسال ✅",
                reply_markup=ReplyKeyboardMarkup(send_button_ar, resize_keyboard=True)
            )
        elif text == "💡 إرسال اقتراحات":
            user_state[user_id]["mode"] = "suggestion"
            user_state[user_id]["messages"] = []
            await update.message.reply_text(
                "✍️ اكتب اقتراحك هنا 👇",
                reply_markup=ReplyKeyboardMarkup(send_button_ar, resize_keyboard=True)
            )
        elif text == "🥳 إرسال صور الفوز":
            user_state[user_id]["mode"] = "win"
            user_state[user_id]["messages"] = []
            await update.message.reply_text(
                "🎉 أرسل صورة فوزك 👇",
                reply_markup=ReplyKeyboardMarkup(send_button_ar, resize_keyboard=True)
            )
        elif text == "✅ إرسال المشكلة":
            await forward_to_admin(update, context, user_id, "issue", "مشكلـة")
            await update.message.reply_text(
                "✅ تم إرسال مشكلتك للمطور بنجاح، سيتم مراجعتها قريباً",
                reply_markup=ReplyKeyboardMarkup(main_menu_ar, resize_keyboard=True)
            )
        elif text == "✅ إرسال الاقتراح":
            await forward_to_admin(update, context, user_id, "suggestion", "اقتراح")
            await update.message.reply_text(
                "✅ تم إرسال اقتراحك للمطور بنجاح",
                reply_markup=ReplyKeyboardMarkup(main_menu_ar, resize_keyboard=True)
            )
        elif text == "✅ إرسال الصورة":
            await forward_to_admin(update, context, user_id, "win", "صورة فوز")
            await update.message.reply_text(
                "✅ تم إرسال صورة فوزك بنجاح",
                reply_markup=ReplyKeyboardMarkup(main_menu_ar, resize_keyboard=True)
            )
        elif text == "🔙 الرجوع للقائمة الرئيسية":
            await update.message.reply_text(
                "القائمة الرئيسية 👇",
                reply_markup=ReplyKeyboardMarkup(main_menu_ar, resize_keyboard=True)
            )
        else:
            user_state[user_id]["messages"].append(text)

    # ===== English =====
    elif lang == "en":
        if text == "📩 Report Issue":
            user_state[user_id]["mode"] = "issue"
            user_state[user_id]["messages"] = []
            await update.message.reply_text(
                "✍️ Please describe your issue or send a video 👇\n\n"
                "When done, press ✅ Send Issue",
                reply_markup=ReplyKeyboardMarkup(send_button_en, resize_keyboard=True)
            )
        elif text == "💡 Suggestions":
            user_state[user_id]["mode"] = "suggestion"
            user_state[user_id]["messages"] = []
            await update.message.reply_text(
                "✍️ Please type your suggestion 👇",
                reply_markup=ReplyKeyboardMarkup(send_button_en, resize_keyboard=True)
            )
        elif text == "🥳 Winning Screenshots":
            user_state[user_id]["mode"] = "win"
            user_state[user_id]["messages"] = []
            await update.message.reply_text(
                "🎉 Send your winning screenshot 👇",
                reply_markup=ReplyKeyboardMarkup(send_button_en, resize_keyboard=True)
            )
        elif text == "✅ Send Issue":
            await forward_to_admin(update, context, user_id, "issue", "Issue")
            await update.message.reply_text(
                "✅ Your issue has been sent to the developer successfully. It will be reviewed shortly",
                reply_markup=ReplyKeyboardMarkup(main_menu_en, resize_keyboard=True)
            )
        elif text == "✅ Send Suggestion":
            await forward_to_admin(update, context, user_id, "suggestion", "Suggestion")
            await update.message.reply_text(
                "✅ Your suggestion has been sent to the developer successfully",
                reply_markup=ReplyKeyboardMarkup(main_menu_en, resize_keyboard=True)
            )
        elif text == "✅ Send Screenshot":
            await forward_to_admin(update, context, user_id, "win", "Winning Screenshot")
            await update.message.reply_text(
                "✅ Your winning screenshot has been sent successfully",
                reply_markup=ReplyKeyboardMarkup(main_menu_en, resize_keyboard=True)
            )
        elif text == "🔙 Back to Main Menu":
            await update.message.reply_text(
                "Main Menu 👇",
                reply_markup=ReplyKeyboardMarkup(main_menu_en, resize_keyboard=True)
            )
        else:
            user_state[user_id]["messages"].append(text)

# ============ إرسال الرسائل للمطور ============
async def forward_to_admin(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id, mode, mode_name):
    user = update.effective_user
    messages = user_state[user_id]["messages"]

    header = f"📩 {mode_name} جديدة\n"
    header += f"👤 From: {user.first_name} (@{user.username})\n"
    header += f"🆔 User ID: {user.id}\n\n"

    full_message = header + "\n".join(messages)
    await context.bot.send_message(chat_id=ADMIN_ID, text=full_message)

    # تفريغ الرسائل بعد الإرسال
    user_state[user_id]["messages"] = []

# ============ تشغيل البوت ============
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, set_language))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu))

    app.run_polling()

if __name__ == "__main__":
    main()
