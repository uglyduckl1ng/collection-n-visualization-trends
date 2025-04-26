from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
import os
import pandas as pd

from bot.trend_storage import save_trend
from viz.trend_map import analyze_and_visualize_trends

# Загружаем токен из .env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Команда /start — показывает кнопки
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["Добавить тренд", "Сгенерировать радарную карту"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "Выбери действие или просто отправь тренд вручную 👇",
        reply_markup=reply_markup
    )

# Обработка входящих сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.strip().lower()

    if user_input == "сгенерировать радарную карту":
        trends_path = "data/trends.csv"
        if not os.path.exists(trends_path):
            await update.message.reply_text("Файл с трендами не найден 😢")
            return

        df = pd.read_csv(trends_path, header=None, names=["timestamp", "user_id", "trend"])
        if df.empty:
            await update.message.reply_text("Тренды пока не добавлены 😢")
            return

        terms = df["trend"].dropna().tolist()
        image_path = analyze_and_visualize_trends(terms)

        if os.path.exists(image_path):
            await update.message.reply_photo(photo=open(image_path, "rb"))
        else:
            await update.message.reply_text("Не удалось сгенерировать карту 😢")
        return

    if user_input == "добавить тренд":
        await update.message.reply_text("Введите тренд, который хотите добавить:")
        return

    # Иначе — просто сохраняем сообщение как тренд
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
