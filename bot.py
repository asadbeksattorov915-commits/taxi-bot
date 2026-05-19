from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "7976746285:AAFV0-Q2wWIFV4YxC5eRLKIseJd2PP-L5zs"
DRIVER_GROUP = -1002383317308

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["🚗 Qo'qon → Guliston"],
        ["🚗 Guliston → Qo'qon"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "Assalomu alaykum! Qo'qon-Guliston Taxi Botga xush kelibsiz! 🚕\n\nYo'nalishni tanlang:",
        reply_markup=reply_markup
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.message.from_user

    if text in ["🚗 Qo'qon → Guliston", "🚗 Guliston → Qo'qon"]:
        context.user_data['yonalish'] = text
        keyboard = [[KeyboardButton("📞 Raqamni yuborish", request_contact=True)]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(
            f"Yo'nalish: {text}\n\n📞 Telefon raqamingizni yuboring:",
            reply_markup=reply_markup
        )

    elif update.message.contact:
        context.user_data['telefon'] = update.message.contact.phone_number
        await update.message.reply_text("📍 Manzilingizni yozing:")

    elif context.user_data.get('yonalish') and context.user_data.get('telefon'):
        yonalish = context.user_data['yonalish']
        telefon = context.user_data['telefon']
        manzil = text
        user_info = f"🚕 Yangi buyurtma!\n👤 Mijoz: {user.first_name}\n🚗 Yo'nalish: {yonalish}\n📍 Manzil: {manzil}\n📞 Telefon: {telefon}"
        await update.message.bot.send_message(chat_id=DRIVER_GROUP, text=user_info)
        await update.message.reply_text("✅ Buyurtmangiz yuborildi! Haydovchi tez orada bog'lanadi.")
        context.user_data.clear()

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT | filters.CONTACT, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
