from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from datetime import datetime

TOKEN = "7976746285:AAFV0-Q2wWIFV4YxC5eRLKIseJd2PP-L5zs"
ADMIN_ID = 1234567890  # O'zingizning ID ingizni yozing

NARX = {
    "🚗 Qo'qon → Guliston": 25000,
    "🚗 Guliston → Qo'qon": 25000
}

haydovchilar = {}
buyurtmalar = {}
statistika = {"jami": 0, "bugun": 0, "daromad": 0}

# ADMIN ID ni bilish
async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Sizning ID ingiz: {update.message.from_user.id}")

# START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id == ADMIN_ID:
        keyboard = [
            ["📊 Statistika", "👥 Haydovchilar"],
            ["🚗 Qo'qon → Guliston"],
            ["🚗 Guliston → Qo'qon"],
            ["🚕 Haydovchi sifatida kirish"]
        ]
    else:
        keyboard = [
            ["🚗 Qo'qon → Guliston"],
            ["🚗 Guliston → Qo'qon"],
            ["🚕 Haydovchi sifatida kirish"]
        ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "Assalomu alaykum! Qo'qon-Guliston Taxi 🚕\n\nYo'nalishni tanlang:",
        reply_markup=reply_markup
    )

# ASOSIY XABARLAR
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.message.from_user
    user_id = user.id

    # ADMIN PANEL
    if text == "📊 Statistika" and user_id == ADMIN_ID:
        msg = (
            f"📊 Statistika:\n"
            f"📦 Jami buyurtmalar: {statistika['jami']}\n"
            f"📅 Bugungi buyurtmalar: {statistika['bugun']}\n"
            f"💰 Jami daromad: {statistika['daromad']:,} so'm\n"
            f"👥 Haydovchilar: {len(haydovchilar)}\n"
            f"✅ Faol: {sum(1 for h in haydovchilar.values() if h.get('holat') == '✅ Faolman')}"
        )
        await update.message.reply_text(msg)

    elif text == "👥 Haydovchilar" and user_id == ADMIN_ID:
        if not haydovchilar:
            await update.message.reply_text("Hali haydovchi yo'q!")
            return
        msg = "👥 Haydovchilar ro'yxati:\n\n"
        for h in haydovchilar.values():
            msg += f"👨‍✈️ {h['ism']} | 📞 {h['telefon']} | {h.get('holat', '❓')}\n"
        await update.message.reply_text(msg)

    # YO'LOVCHI
    elif text in ["🚗 Qo'qon → Guliston", "🚗 Guliston → Qo'qon"]:
        context.user_data['yonalish'] = text
        context.user_data['rol'] = 'yolovchi'
        keyboard = [[KeyboardButton("📞 Raqamni yuborish", request_contact=True)]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(
            f"Yo'nalish: {text}\n💰 Narx: {NARX[text]:,} so'm\n\n📞 Telefon raqamingizni yuboring:",
            reply_markup=reply_markup
        )

    # HAYDOVCHI
    elif text == "🚕 Haydovchi sifatida kirish":
        context.user_data['rol'] = 'haydovchi'
        keyboard = [[KeyboardButton("📞 Raqamni yuborish", request_contact=True)]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(
            "Haydovchi ro'yxatidan o'tish uchun raqamingizni yuboring:",
            reply_markup=reply_markup
        )

    elif text in ["✅ Faolman", "❌ Dam olmoqdaman"]:
        if user_id in haydovchilar:
            haydovchilar[user_id]['holat'] = text
            await update.message.reply_text(f"Holat yangilandi: {text}")

    elif update.message.contact:
        telefon = update.message.contact.phone_number
        rol = context.user_data.get('rol')

        if rol == 'haydovchi':
            haydovchilar[user_id] = {
                'ism': user.first_name,
                'telefon': telefon,
                'username': user.username,
                'reyting': 0,
                'baholar': []
            }
            keyboard = [["✅ Faolman", "❌ Dam olmoqdaman"]]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            await update.message.reply_text("✅ Ro'yxatdan o'tdingiz!\nHolatingizni tanlang:")
        else:
            context.user_data['telefon'] = telefon
            await update.message.reply_text("📍 Manzilingizni yozing:")

    elif context.user_data.get('yonalish') and context.user_data.get('telefon'):
        yonalish = context.user_data['yonalish']
        telefon = context.user_data['telefon']
        buyurtma_id = str(user_id)

        buyurtmalar[buyurtma_id] = {
            'yonalish': yonalish,
            'manzil': text,
            'telefon': telefon,
            'ism': user.first_name,
            'user_id': user_id,
            'vaqt': datetime.now().strftime("%H:%M")
        }

        statistika['jami'] += 1
        statistika['bugun'] += 1
        statistika['daromad'] += NARX[yonalish]

        faol = [h_id for h_id, h in haydovchilar.items() if h.get('holat') == '✅ Faolman']

        if faol:
            for h_id in faol:
                h = haydovchilar[h_id]
                reyting = h.get('reyting', 0)
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("✅ Qabul", callback_data=f"qabul_{buyurtma_id}"),
                     InlineKeyboardButton("❌ Rad", callback_data=f"rad_{buyurtma_id}")]
                ])
                await context.bot.send_message(
                    chat_id=h_id,
                    text=f"🚕 Yangi buyurtma!\n👤 {user.first_name}\n🚗 {yonalish}\n📍 {text}\n📞 {telefon}\n⏰ {buyurtmalar[buyurtma_id]['vaqt']}\n⭐ Reyting: {reyting:.1f}",
                    reply_markup=keyboard
                )
            await update.message.reply_text("✅ Buyurtmangiz yuborildi! Haydovchi tez orada bog'lanadi.")
        else:
            await update.message.reply_text("⚠️ Hozir faol haydovchi yo'q. Keyinroq urinib ko'ring!")

        context.user_data.clear()

# CALLBACK — QABUL/RAD/BAHO
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    haydovchi = query.from_user

    if data.startswith("qabul_"):
        buyurtma_id = data.split("_")[1]
        if buyurtma_id in buyurtmalar:
            b = buyurtmalar[buyurtma_id]
            h = haydovchilar.get(haydovchi.id, {})
            await query.edit_message_text(
                f"✅ Qabul qildingiz!\n👤 {b['ism']}\n📞 {b['telefon']}\n📍 {b['manzil']}\n🚗 {b['yonalish']}"
            )
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("⭐1", callback_data=f"baho_1_{haydovchi.id}"),
                 InlineKeyboardButton("⭐2", callback_data=f"baho_2_{haydovchi.id}"),
                 InlineKeyboardButton("⭐3", callback_data=f"baho_3_{haydovchi.id}"),
                 InlineKeyboardButton("⭐4", callback_data=f"baho_4_{haydovchi.id}"),
                 InlineKeyboardButton("⭐5", callback_data=f"baho_5_{haydovchi.id}")]
            ])
            await context.bot.send_message(
                chat_id=b['user_id'],
                text=f"🎉 Haydovchi topildi!\n👨‍✈️ {haydovchi.first_name}\nTez orada keladi!\n\nXizmatga baho bering:",
                reply_markup=keyboard
            )

    elif data.startswith("rad_"):
        await query.edit_message_text("❌ Rad etdingiz.")

    elif data.startswith("baho_"):
        parts = data.split("_")
        baho = int(parts[1])
        h_id = int(parts[2])
        if h_id in haydovchilar:
            haydovchilar[h_id]['baholar'].append(baho)
            o_rta = sum(haydovchilar[h_id]['baholar']) / len(haydovchilar[h_id]['baholar'])
            haydovchilar[h_id]['reyting'] = o_rta
            await query.edit_message_text(f"⭐ Bahoyingiz: {baho}/5\nRahmat!")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("myid", myid))
    app.add_handler(MessageHandler(filters.TEXT | filters.CONTACT, handle_message))
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.run_polling()

if __name__ == "__main__":
    main()
