from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "7976746285:AAE_-QVN_jebLuznEGej2xd_DgSQzrW3sj0"
DRIVER_GROUP = -1001234567890  # Keyinroq o'zgartiramiz

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["🚕 Taksi chaqirish"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "Assalomu alaykum! Qo'qon-Guliston Taxi Botga xush kelibsiz! 🚕",
        reply_markup=reply_markup
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.message.from_user

    if text == "🚕 Taksi chaqirish":
        await update.message.reply_text("📍 Manzilingizni yuboring (yoki lokatsiya):")
        context.user_data['waiting'] = 'location'

    elif context.user_data.get('waiting') == 'location':
        location = text
        user_info = f"🚕 Yangi buyurtma!\n👤 Mijoz: {user.first_name}\n📍 Manzil: {location}\n📞 Telefon: @{user.username}"
        await context.bot.send_message(chat_id=DRIVER_GROUP, text=user_info)
        await update.message.reply_text("✅ Buyurtmangiz yuborildi! Haydovchi tez orada bog'lanadi.")
        context.user_data['waiting'] = None

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
