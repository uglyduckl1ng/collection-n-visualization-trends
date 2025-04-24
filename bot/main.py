from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
import os

from bot.trend_storage import save_trend
from viz.wordcloud_input import generate_wordcloud

# Загружаем токен из .env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Команда /start — показывает кнопки
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["Добавить тренд", "Сгенерировать wordCloud"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "Выбери действие или просто отправь тренд вручную 👇",
        reply_markup=reply_markup
    )

# Обработка сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.strip()

    if user_input.lower() == "сгенерировать wordcloud":
        generate_wordcloud()
        image_path = "pics/wordcloud.png"
        if os.path.exists(image_path):
            await update.message.reply_photo(photo=open(image_path, "rb"))
        else:
            await update.message.reply_text("Картинка не найдена 😢")
        return

    if user_input.lower() == "добавить тренд":
        await update.message.reply_text("Введите тренд, который хотите добавить:")
        return

    # Сохраняем тренд
    save_trend(user_input, user_id=update.effective_user.id)
    await update.message.reply_text(f"Спасибо! Я записал тренд: {user_input}")

# Запуск бота
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
