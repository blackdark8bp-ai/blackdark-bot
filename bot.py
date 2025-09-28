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
import telegram.error
from flask import Flask
import threading

# ============== إعدادات ==============
TOKEN = "8270195922:AAGDVz_mL8FOJta3NnnNSZTm1m-5guzba4Y"
DEVELOPER_ID = 6597567561

# ============== لوج ==============
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# ============== حالة المستخدم ==============
user_state = {}

# ============== مفاتيح الواجهات (Inline) ==============
def language_keyboard():
    kb = [
        [InlineKeyboardButton("العربية", callback_data="lang_ar"),
         InlineKeyboardButton("English", callback_data="lang_en")]
    ]
    return InlineKeyboardMarkup(kb)

def main_menu_markup(lang: str):
    if lang == "ar":
        kb = [
            [
                InlineKeyboardButton("📩 إرسال المشكلة", callback_data="menu_issue"),
                InlineKeyboardButton("💡 إرسال اقتراحات", callback_data="menu_suggestion"),
                InlineKeyboardButton("🥳 إرسال صور الفوز", callback_data="menu_win"),
            ]
        ]
        text = "اختر من القائمة:"
    else:
        kb = [
            [
                InlineKeyboardButton("📩 Send Issue", callback_data="menu_issue"),
                InlineKeyboardButton("💡 Send Suggestion", callback_data="menu_suggestion"),
                InlineKeyboardButton("🥳 Send Win Screenshot", callback_data="menu_win"),
            ]
        ]
        text = "Choose from the menu:"
    return text, InlineKeyboardMarkup(kb)

def confirm_markup(lang: str, mode: str):
    if lang == "ar":
        if mode == "issue":
            send_text = "✅ إرسال المشكلة"
        elif mode == "suggestion":
            send_text = "✅ إرسال الاقتراح"
        else:
            send_text = "✅ إرسال الصورة"
        back_text = "🔙 رجوع"
    else:
        if mode == "issue":
            send_text = "✅ Send Issue"
        elif mode == "suggestion":
            send_text = "✅ Send Suggestion"
        else:
            send_text = "✅ Send Screenshot"
        back_text = "🔙 Back"

    kb = [
        [InlineKeyboardButton(send_text, callback_data=f"send_{mode}")],
        [InlineKeyboardButton(back_text, callback_data="back_to_menu")]
    ]
    return InlineKeyboardMarkup(kb)

# ============== دوال أساسية ==============
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_state[chat_id] = {"lang": None, "mode": None, "buffer": []}
    welcome = (
        "👋 اهلا بك في بوت بلاك دارك\n"
        "الرجاء اختيار اللغة\n\n"
        "👋 Welcome to Black Dark Bot\n"
        "Please choose your language"
    )
    await update.message.reply_text(welcome, reply_markup=language_keyboard())

async def safe_edit_message(query, text: str, reply_markup=None):
    try:
        await query.edit_message_text(text, reply_markup=reply_markup)
    except telegram.error.BadRequest as e:
        if "Message is not modified" in str(e):
            logger.debug("edit_message_text ignored: Message is not modified")
        else:
            logger.exception("BadRequest while editing message")

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    chat_id = query.from_user.id

    if data == "lang_ar":
        user_state[chat_id] = {"lang": "ar", "mode": None, "buffer": []}
        text, markup = main_menu_markup("ar")
        await safe_edit_message(query, "✅ تم اختيار اللغة: العربية\n\n" + text, reply_markup=markup)
        return

    if data == "lang_en":
        user_state[chat_id] = {"lang": "en", "mode": None, "buffer": []}
        text, markup = main_menu_markup("en")
        await safe_edit_message(query, "✅ Language selected: English\n\n" + text, reply_markup=markup)
        return

    if chat_id not in user_state or not user_state[chat_id].get("lang"):
        await safe_edit_message(query, "الرجاء اختيار اللغة أولاً / Please select a language first.", reply_markup=language_keyboard())
        return

    lang = user_state[chat_id]["lang"]

    if data == "menu_issue":
        user_state[chat_id]["mode"] = "issue"
        user_state[chat_id]["buffer"] = []
        text = "✍️ يرجى إرسال المشكلة أو مقطع فيديو يوضحها 👇\n\nبعد الانتهاء اضغط زر الإرسال" if lang == "ar" else \
               "✍️ Please send your issue or a clear video 👇\n\nWhen finished, press the Send button"
        await safe_edit_message(query, text, reply_markup=confirm_markup(lang, "issue"))
        return

    if data == "menu_suggestion":
        user_state[chat_id]["mode"] = "suggestion"
        user_state[chat_id]["buffer"] = []
        text = "💡 اكتب اقتراحك وسنقوم بمراجعته 👇\n\nبعد الانتهاء اضغط زر الإرسال" if lang == "ar" else \
               "💡 Please type your suggestion 👇\n\nWhen finished, press the Send button"
        await safe_edit_message(query, text, reply_markup=confirm_markup(lang, "suggestion"))
        return

    if data == "menu_win":
        user_state[chat_id]["mode"] = "win"
        user_state[chat_id]["buffer"] = []
        text = "🥳 أرسل صورة فوزك 🎉 وسنحتفظ بها ضمن قائمة الإنجازات 👇\n\nبعد الانتهاء اضغط زر الإرسال" if lang == "ar" else \
               "🥳 Send your winning screenshot 🎉 We’ll add it to the achievements 👇\n\nWhen finished, press the Send button"
        await safe_edit_message(query, text, reply_markup=confirm_markup(lang, "win"))
        return

    if data == "back_to_menu":
        text, markup = main_menu_markup(lang)
        await safe_edit_message(query, text, reply_markup=markup)
        user_state[chat_id]["mode"] = None
        user_state[chat_id]["buffer"] = []
        return

    if data.startswith("send_"):
        mode = data.replace("send_", "")
        state = user_state.get(chat_id, {})
        buffer = state.get("buffer", [])
        lang = state.get("lang", "ar")

        if not buffer:
            nothing_text = "❌ لم ترسل أي محتوى بعد!" if lang == "ar" else "❌ You haven't sent any content yet!"
            await safe_edit_message(query, nothing_text, reply_markup=confirm_markup(lang, mode))
            return

        user = query.from_user
        if lang == "ar":
            mode_name = "مشكلة" if mode == "issue" else ("اقتراح" if mode == "suggestion" else "صورة فوز")
        else:
            mode_name = "Issue" if mode == "issue" else ("Suggestion" if mode == "suggestion" else "Winning Screenshot")

        header = (
            f"📩 نوع الإرسال: {mode_name}\n"
            f"👤 From: {user.full_name} (@{user.username})\n"
            f"🆔 ID: {user.id}\n\n"
        ) if lang == "ar" else (
            f"📩 Type: {mode_name}\n"
            f"👤 From: {user.full_name} (@{user.username})\n"
            f"🆔 ID: {user.id}\n\n"
        )

        try:
            await context.bot.send_message(chat_id=DEVELOPER_ID, text=header)
        except Exception:
            logger.exception("Failed to send header to developer")

        for msg_id in buffer:
            try:
                await context.bot.forward_message(chat_id=DEVELOPER_ID, from_chat_id=chat_id, message_id=msg_id)
            except Exception:
                logger.exception(f"Failed to forward message {msg_id} from {chat_id}")

        confirm_text = (
            "✅ تم إرسال مشكلتك للمطور بنجاح، سيتم مراجعتها قريباً" if mode == "issue" and lang == "ar" else
            "✅ تم إرسال اقتراحك للمطور بنجاح" if mode == "suggestion" and lang == "ar" else
            "✅ تم إرسال صورة فوزك بنجاح 🎉" if mode == "win" and lang == "ar" else
            "✅ Your issue has been sent to the developer successfully. It will be reviewed shortly" if mode == "issue" and lang == "en" else
            "✅ Your suggestion has been sent to the developer successfully" if mode == "suggestion" and lang == "en" else
            "✅ Your win screenshot has been sent successfully 🎉"
        )

        text_menu, markup = main_menu_markup(lang)
        try:
            await query.edit_message_text(confirm_text + "\n\n" + text_menu, reply_markup=markup)
        except telegram.error.BadRequest as e:
            if "Message is not modified" in str(e):
                try:
                    await context.bot.send_message(chat_id=chat_id, text=confirm_text, reply_markup=markup)
                except Exception:
                    logger.exception("Failed to send confirmation message as new message")
            else:
                logger.exception("Unexpected BadRequest on edit after send")

        user_state[chat_id]["mode"] = None
        user_state[chat_id]["buffer"] = []
        return

async def collect_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    chat_id = update.message.from_user.id
    state = user_state.get(chat_id)
    if not state or not state.get("mode"):
        return

    msg_id = update.message.message_id
    if msg_id not in state["buffer"]:
        state["buffer"].append(msg_id)

# ======= ميني ويب سيرفر للحفاظ على البوت نشط =======
app_server = Flask("")

@app_server.route("/")
def home():
    return "Bot is alive!"

def run_server():
    app_server.run(host="0.0.0.0", port=8080)

# ======= تشغيل البوت =======
def main():
    threading.Thread(target=run_server).start()  # تشغيل السيرفر في خلفية thread

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, collect_messages))

    logger.info("Bot is starting...")
    app.run_polling()

if __name__ == "__main__":
    main()
