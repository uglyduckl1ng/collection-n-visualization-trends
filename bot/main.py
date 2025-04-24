from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
import os
from bot.trend_storage import save_trend

# Загружаем токен из .env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Отправь мне тренд, который, по твоему мнению, сейчас актуален 📈")

# Обработка обычного текстового сообщения
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    trend = update.message.text.strip()
    save_trend(trend, user_id=update.effective_user.id)
    await update.message.reply_text(f"Спасибо! Я записал тренд: {trend}")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
