import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ===== إعدادات البوت =====
TOKEN = "8270195922:AAGDVz_mL8FOJta3NnnNSZTm1m-5guzba4Y"
ADMIN_ID = 6597567561  # الايدي الخاص فيك

# ===== تسجيل الأخطاء =====
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# ===== القوائم =====
main_menu = [["🚨 المشكله", "💡 الاقتراحات", "🏆 الفوز"]]

# ===== أوامر البداية =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "اهلاً بك! اختر من القائمة 👇",
        reply_markup=ReplyKeyboardMarkup(main_menu, resize_keyboard=True)
    )

# ===== معالجات الأزرار =====
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "🚨 المشكله":
        await update.message.reply_text("✍️ اكتب مشكلتك هنا.\nبعد الانتهاء من تحديد المشكله الرجاء الضغط على زر الإرسال ✅")

    elif text == "💡 الاقتراحات":
        await update.message.reply_text("✍️ اكتب اقتراحك هنا.")

    elif text == "🏆 الفوز":
        await update.message.reply_text("🎉 شاركنا قصة فوزك!")

    else:
        # إرسال الرسالة للـ ADMIN
        await context.bot.send_message(chat_id=ADMIN_ID, text=f"📩 رسالة من {update.effective_user.id}:\n\n{text}")
        await update.message.reply_text("✅ تم إرسال رسالتك للإدارة.")

# ===== تشغيل البوت =====
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()

if __name__ == "__main__":
    main()
