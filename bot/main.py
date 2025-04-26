from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
import os
import pandas as pd
import csv
from datetime import datetime

from bot.trend_storage import save_trend_to_csv, get_user_trends, update_trend, delete_trend

# =========================
# Глобальная переменная для хранения состояний пользователей
user_states = {}

# =========================
# Настройки
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Путь к файлу с трендами
DATA_PATH = "data/trends.csv"

# =========================
# Кнопки
MAIN_MENU_BUTTONS = [
    ["Записать тренд", "Сгенерировать радарную карту"],
    ["Мои тренды"]
]
CATEGORY_BUTTONS = [["1", "2", "3"], ["4", "5", "6"], ["Назад"]]
TIMEZONE_BUTTONS = [["1", "2"], ["3", "4"], ["Назад"]]

# =========================
# Словари соответствий
CATEGORIES = {
    "1": "Технологии",
    "2": "Процессы и методологии",
    "3": "Культура и организация",
    "4": "Стандарты и безопасность",
    "5": "Лидерство и стратегия",
    "6": "Другое"
}

TIME_ZONES = {
    "1": "Сейчас (Новая нормальность)",
    "2": "1-5 лет (Краткосрочное планирование)",
    "3": "5-20 лет (Среднесрочное планирование)",
    "4": "20+ лет (Долгосрочное планирование)"
}


# =========================
# Бот команды

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = ReplyKeyboardMarkup(MAIN_MENU_BUTTONS, resize_keyboard=True)
    await update.message.reply_text("Выбери действие или отправь тренд вручную:", reply_markup=keyboard)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    state = user_states.get(user_id)

    if not state:
        if text.lower() == "записать тренд":
            user_states[user_id] = {"step": "choose_category", "category": None, "time_zone": None, "trend": None}
            keyboard = ReplyKeyboardMarkup(CATEGORY_BUTTONS, resize_keyboard=True)
            await update.message.reply_text(
                "*Выберите категорию тренда из списка:*\n\n"
                "`1.` Технологии\n"
                "`2.` Процессы и методологии\n"
                "`3.` Культура и организация\n"
                "`4.` Стандарты и безопасность\n"
                "`5.` Лидерство и стратегия\n"
                "`6.` Другое",
                parse_mode="Markdown",
                reply_markup=keyboard
            )
            return

        if text.lower() == "сгенерировать радарную карту":
            await update.message.reply_text("(Здесь будет генерация радарной карты)")
            return

        if text.lower() == "мои тренды":
            user_trends = get_user_trends(user_id)
            if not user_trends:
                keyboard = ReplyKeyboardMarkup(MAIN_MENU_BUTTONS, resize_keyboard=True)
                await update.message.reply_text(
                    "Вы ещё не записывали тренд.",
                    reply_markup=keyboard
                )
                user_states.pop(user_id, None)
                return

            trends_list = ""
            for idx, trend in enumerate(user_trends, start=1):
                trends_list += f"{idx}. {trend['trend']} ({trend['category']} / {trend['time_zone']})\n"

            keyboard = ReplyKeyboardMarkup(
                [["Изменить", "Удалить"], ["Назад"]],
                resize_keyboard=True
            )

            user_states[user_id] = {
                "step": "choose_action_for_trend",
                "trends": user_trends
            }

            await update.message.reply_text(
                f"Вот список Ваших трендов:\n\n{trends_list}",
                reply_markup=keyboard
            )
            return

        await update.message.reply_text("Пожалуйста, выберите действие через кнопки ⬇️")
        return

    # ========== FSM этапы ==========

    # Раздел "Записать тренд"
    # ===========================
    if state["step"] == "choose_category":
        if text == "Назад":
            user_states.pop(user_id)
            keyboard = ReplyKeyboardMarkup(MAIN_MENU_BUTTONS, resize_keyboard=True)
            await update.message.reply_text("Вы вернулись в главное меню.", reply_markup=keyboard)
            return

        if text in CATEGORIES:
            user_states[user_id]["category"] = CATEGORIES[text]
            user_states[user_id]["step"] = "choose_time_zone"
            keyboard = ReplyKeyboardMarkup(TIMEZONE_BUTTONS, resize_keyboard=True)
            await update.message.reply_text(
                "*Выберите горизонт планирования тренда:*\n\n"
                "`1.` Сейчас (Новая нормальность)\n"
                "`2.` 1-5 лет (Краткосрочное планирование)\n"
                "`3.` 5-20 лет (Среднесрочное планирование)\n"
                "`4.` 20+ лет (Долгосрочное планирование)",
                parse_mode="Markdown",
                reply_markup=keyboard
            )
            return

        await update.message.reply_text("Пожалуйста, выберите категорию через кнопки ⬇️")

    if state["step"] == "choose_time_zone":
        if text == "Назад":
            user_states[user_id]["step"] = "choose_category"
            keyboard = ReplyKeyboardMarkup(CATEGORY_BUTTONS, resize_keyboard=True)
            await update.message.reply_text(
                "*Выберите категорию тренда из списка:*\n\n"
                "`1.` Технологии\n"
                "`2.` Процессы и методологии\n"
                "`3.` Культура и организация\n"
                "`4.` Стандарты и безопасность\n"
                "`5.` Лидерство и стратегия\n"
                "`6.` Другое",
                parse_mode="Markdown",
                reply_markup=keyboard
            )
            return

        if text in TIME_ZONES:
            user_states[user_id]["time_zone"] = TIME_ZONES[text]
            user_states[user_id]["step"] = "input_trend"
            keyboard = ReplyKeyboardMarkup([["Назад"]], resize_keyboard=True)
            await update.message.reply_text(
                "Теперь напишите свой тренд:",
                reply_markup=keyboard
            )
            return

        await update.message.reply_text("Пожалуйста, выберите горизонт через кнопки ⬇️")

    if state["step"] == "input_trend":
        if text == "Назад":
            user_states[user_id]["step"] = "choose_time_zone"
            keyboard = ReplyKeyboardMarkup(TIMEZONE_BUTTONS, resize_keyboard=True)
            await update.message.reply_text(
                "*Выберите горизонт планирования тренда:*\n\n"
                "`1.` Сейчас (Новая нормальность)\n"
                "`2.` 1-5 лет (Краткосрочное планирование)\n"
                "`3.` 5-20 лет (Среднесрочное планирование)\n"
                "`4.` 20+ лет (Долгосрочное планирование)",
                parse_mode="Markdown",
                reply_markup=keyboard
            )
            return

        # Сохраняем тренд
        trend_text = text
        category = user_states[user_id]["category"]
        time_zone = user_states[user_id]["time_zone"]

        save_trend_to_csv(user_id, category, time_zone, trend_text)
        user_states.pop(user_id)

        keyboard = ReplyKeyboardMarkup(MAIN_MENU_BUTTONS, resize_keyboard=True)
        await update.message.reply_text(
            "Спасибо, что поделились с нами своими мыслями! 😊",
            reply_markup=keyboard
        )
        return
    

    # ==== FSM этапы: работа с трендами ====

    # Выбор действия с трендами
    if state["step"] == "choose_action_for_trend":
        if text == "Назад":
            user_states.pop(user_id, None)
            keyboard = ReplyKeyboardMarkup(MAIN_MENU_BUTTONS, resize_keyboard=True)
            await update.message.reply_text(
                "Вы вернулись в главное меню.",
                reply_markup=keyboard
            )
            return

        if text == "Изменить":
            user_states[user_id]["step"] = "select_trend_to_edit"
            trends = user_states[user_id]["trends"]
            buttons = [[str(i)] for i in range(1, len(trends) + 1)]
            buttons += [["Назад"]]
            keyboard = ReplyKeyboardMarkup(buttons, resize_keyboard=True)

            await update.message.reply_text(
                "Выберите номер тренда, который хотите отредактировать:",
                reply_markup=keyboard
            )
            return

        if text == "Удалить":
            user_states[user_id]["step"] = "select_trend_to_delete"
            trends = user_states[user_id]["trends"]
            buttons = [[str(i)] for i in range(1, len(trends) + 1)]
            buttons += [["Назад"]]
            keyboard = ReplyKeyboardMarkup(buttons, resize_keyboard=True)

            await update.message.reply_text(
                "Выберите номер тренда, который хотите удалить:",
                reply_markup=keyboard
            )
            return

        await update.message.reply_text("Пожалуйста, выберите действие через кнопки ⬇️")

    # Выбор тренда для удаления
    if state["step"] == "select_trend_to_delete":
        if text == "Назад":
            user_states[user_id]["step"] = "choose_action_for_trend"
            keyboard = ReplyKeyboardMarkup([["Изменить", "Удалить"], ["Назад"]], resize_keyboard=True)
            await update.message.reply_text(
                "Что хотите сделать с трендами?",
                reply_markup=keyboard
            )
            return

        if text.isdigit():
            idx = int(text) - 1
            trends = user_states[user_id]["trends"]
            if 0 <= idx < len(trends):
                from bot.trend_storage import delete_trend
                trend = trends[idx]
                delete_trend(int(trend["id"]), user_id)

                user_states.pop(user_id, None)
                keyboard = ReplyKeyboardMarkup(MAIN_MENU_BUTTONS, resize_keyboard=True)
                await update.message.reply_text(
                    "Тренд удалён! 🗑️",
                    reply_markup=keyboard
                )
                return

        await update.message.reply_text("Пожалуйста, выберите корректный номер тренда ⬇️")

    # Выбор тренда для редактирования
    if state["step"] == "select_trend_to_edit":
        if text == "Назад":
            # Возвращаем обратно на выбор действия (Изменить / Удалить / Назад)
            user_states[user_id]["step"] = "choose_action_for_trend"
            keyboard = ReplyKeyboardMarkup(
                [["Изменить", "Удалить"], ["Назад"]],
                resize_keyboard=True
            )
            await update.message.reply_text(
                "Что хотите сделать с трендами?",
                reply_markup=keyboard
            )
            return

        if text.isdigit():
            idx = int(text) - 1
            trends = user_states[user_id]["trends"]

            if 0 <= idx < len(trends):
                trend = trends[idx]
                user_states[user_id] = {
                    "step": "editing_category",
                    "trend_to_edit": trend,
                    "new_category": None,
                    "new_time_zone": None,
                    "new_trend_text": None,
                    "trends": trends  # Сохраняем список трендов чтобы "Назад" работал!
                }
                keyboard = ReplyKeyboardMarkup(CATEGORY_BUTTONS, resize_keyboard=True)
                await update.message.reply_text(
                    "*Выберите новую категорию тренда:*\n\n"
                    "`1.` Технологии\n"
                    "`2.` Процессы и методологии\n"
                    "`3.` Культура и организация\n"
                    "`4.` Стандарты и безопасность\n"
                    "`5.` Лидерство и стратегия\n"
                    "`6.` Другое",
                    parse_mode="Markdown",
                    reply_markup=keyboard
                )
                return

        await update.message.reply_text(
            "Пожалуйста, выберите корректный номер тренда ⬇️"
        )


    # Редактирование категории
    if state["step"] == "editing_category":
        if text == "Назад":
            user_states[user_id]["step"] = "select_trend_to_edit"
            trends = user_states[user_id]["trends"]
            buttons = [[str(i)] for i in range(1, len(trends) + 1)]
            buttons.append(["Назад"])
            keyboard = ReplyKeyboardMarkup(buttons, resize_keyboard=True)
            await update.message.reply_text(
                "Выберите номер тренда, который хотите отредактировать:",
                reply_markup=keyboard
            )
            return

        if text in CATEGORIES:
            user_states[user_id]["new_category"] = CATEGORIES[text]
            user_states[user_id]["step"] = "editing_time_zone"
            keyboard = ReplyKeyboardMarkup(TIMEZONE_BUTTONS, resize_keyboard=True)
            await update.message.reply_text(
                "*Выберите новый горизонт планирования тренда:*\n\n"
                "`1.` Сейчас (Новая нормальность)\n"
                "`2.` 1-5 лет (Краткосрочное планирование)\n"
                "`3.` 5-20 лет (Среднесрочное планирование)\n"
                "`4.` 20+ лет (Долгосрочное планирование)",
                parse_mode="Markdown",
                reply_markup=keyboard
            )
            return

        await update.message.reply_text("Пожалуйста, выберите категорию через кнопки ⬇️")

    # Редактирование временного диапазона
    if state["step"] == "editing_time_zone":
        if text == "Назад":
            user_states[user_id]["step"] = "editing_category"
            keyboard = ReplyKeyboardMarkup(CATEGORY_BUTTONS, resize_keyboard=True)
            await update.message.reply_text(
                "*Выберите новую категорию тренда:*\n\n"
                "`1.` Технологии\n"
                "`2.` Процессы и методологии\n"
                "`3.` Культура и организация\n"
                "`4.` Стандарты и безопасность\n"
                "`5.` Лидерство и стратегия\n"
                "`6.` Другое",
                parse_mode="Markdown",
                reply_markup=keyboard
            )
            return

        if text in TIME_ZONES:
            user_states[user_id]["new_time_zone"] = TIME_ZONES[text]
            user_states[user_id]["step"] = "editing_trend_text"
            keyboard = ReplyKeyboardMarkup([["Оставить таким же"], ["Назад"]], resize_keyboard=True)
            await update.message.reply_text(
                "Введите новый текст тренда или нажмите \"Оставить таким же\" ⬇️",
                reply_markup=keyboard
            )
            return

        await update.message.reply_text("Пожалуйста, выберите горизонт через кнопки ⬇️")

    # Редактирование текста тренда
    if state["step"] == "editing_trend_text":
        if text == "Назад":
            user_states[user_id]["step"] = "editing_time_zone"
            keyboard = ReplyKeyboardMarkup(TIMEZONE_BUTTONS, resize_keyboard=True)
            await update.message.reply_text(
                "*Выберите новый горизонт планирования тренда:*\n\n"
                "`1.` Сейчас (Новая нормальность)\n"
                "`2.` 1-5 лет (Краткосрочное планирование)\n"
                "`3.` 5-20 лет (Среднесрочное планирование)\n"
                "`4.` 20+ лет (Долгосрочное планирование)",
                parse_mode="Markdown",
                reply_markup=keyboard
            )
            return

        trend_text = None if text == "Оставить таким же" else text

        from bot.trend_storage import update_trend

        trend = user_states[user_id]["trend_to_edit"]
        success = update_trend(
            trend_id=int(trend["id"]),
            user_id=user_id,
            new_trend_text=trend_text,
            new_category=user_states[user_id]["new_category"],
            new_time_zone=user_states[user_id]["new_time_zone"]
        )

        keyboard = ReplyKeyboardMarkup(MAIN_MENU_BUTTONS, resize_keyboard=True)
        user_states.pop(user_id, None)

        if success:
            await update.message.reply_text(
                "Спасибо! Тренд обновлён! ✅",
                reply_markup=keyboard
            )
        else:
            await update.message.reply_text(
                "Ошибка при обновлении тренда 😢",
                reply_markup=keyboard
            )


# =========================
# Запуск бота

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
