from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, PollAnswerHandler, CallbackQueryHandler
from dotenv import load_dotenv
import os
from bot.trend_storage import save_user_case, save_trend_to_db, get_user_trends, update_trend, delete_trend, get_all_votes, has_user_voted, add_user_vote, increase_vote_result



user_states = {}


load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

VOTE_SHORT_NAMES = {
    "SOCIAL_1": "Социальные 1-3 года",
    "TECH_1": "Технологии 1-3 года",
    "SOCIAL_3": "Социальные 3-5 лет",
    "TECH_3": "Технологии 3-5 лет",
    "ECON_3": "Экономика 3-5 лет",
    "POLIT_3": "Политика 3-5 лет",
    "SOCIAL_ECON_5": "Соц/Экон 5-7 лет",
    "POL_TECH_LAW_5": "Пол/Техн/Юр 5-7 лет",
}


VOTE_MAPPING = {
    "SOCIAL_1": "Социальные 1-3 года",
    "TECH_1": "Технологии 1-3 года",
    "SOCIAL_3": "Социальные 3-5 лет",
    "TECH_3": "Технологии 3-5 лет",
    "ECON_3": "Экономика 3-5 лет",
    "POLIT_3": "Политика 3-5 лет",
    "SOCIAL_ECON_5": "Соц/Экон 5-7 лет",
    "POL_TECH_LAW_5": "Пол/Техн/Юр 5-7 лет",
}

PHASES = [
    ["SOCIAL_1", "TECH_1"],
    ["SOCIAL_3", "TECH_3", "ECON_3", "POLIT_3"],
    ["SOCIAL_ECON_5", "POL_TECH_LAW_5"]
]

FINAL_MESSAGE = (
    "Благодарим за сотрудничество в формировании рейтинга наиболее значимых трендов, драйверов в KM индустрии!\n\n"
    "Обновленный рейтинг будет доступен на экране в Центре сбора трендов (в общем пространстве)! \n"
    "Используйте знание о трендах, чтобы адаптироваться к меняющимся условиям рынка, повышать эффективность работы команды, вовремя запускать новые продукты или услуги, снижать риски и поддерживать конкурентоспособность.\n\n"
    "Если Вы готовы перейти на продвинутый уровень, можно добавить свой тренд – что влияет сегодня на рынок, но не учтено в списке или поделиться реакцией на существующий тренд."
)

poll_messages = {
    "Социальные 1-3 года": {
        "start": (
            "Пожалуйста, выберите наиболее значимые тренды в горизонте 1-3 года. Они важны для оперативного реагирования на рыночные изменения, оптимизацию текущих процессов и эффективного распределения ресурсов.\n\n"
            "Выберите топ-3 тренда из группы социальных и экономических трендов:"
        ),
        "end": (
            "Спасибо! Рейтинг социальных и экономических трендов трендов в горизонте 1-3 лет будет обновлен.\n\n"
            "Готовы посмотреть на тренды с другой стороны? Переходим к списку технологических трендов."
        ),
    },
    "Технологии 1-3 года": {
        "start": (
            "Ниже – список из группы технологических трендов в горизонте 1-3 года. Пожалуйста, Выберите топ-3 тренда наиболее значимых из них:"
        ),
        "end": (
            "Спасибо! Мы обновим рейтинг технологических трендов в горизонте 1-3 лет с учетом вашего ответа.\n\n"
            "А теперь предлагаем отметить более сильные тренды, влияние которых нельзя игнорировать в ближайшие 3-5 лет. "
            "Понимание среднесрочных трендов необходимо для разработки устойчивых бизнес-стратегий, инвестиций в перспективные направления и подготовки к будущим вызовам. Эти знания позволяют компаниям создавать условия для стабильного роста, формировать инновационные проекты и готовиться к возможным экономическим колебаниям."
        ),
    },
    "Социальные 3-5 лет": {
        "start": "Рассмотрим социальные тренды - какие из них, на ваш взгляд, наиболее значимы? Выберите топ-3:",
        "end": "Спасибо! Давайте теперь выберем топ-3 самых влиятельных технологических трендов.",
    },
    "Технологии 3-5 лет": {
        "start": "Выберите топ-3 самых влиятельных технологических тренда:",
        "end": "Отлично, мы учли ваш ответ в рейтинге! Идём дальше?",
    },
    "Экономика 3-5 лет": {
        "start": "Переходим к экономическим трендам - какие топ-3 влияют на отрасль больше всего?",
        "end": "Хм, интересный выбор. Давайте посмотрим, как обстоят дела с ещё на политические и юридические тренды.",
    },
    "Политика 3-5 лет": {
        "start": "Посмотрите, какие политические и юридические тренды подготовили эксперты в горизонте планирования 3-5 лет, выберите топ-3:",
        "end": "Благодарим за сотрудничество! Готовы перейти к голосованию за долгосрочные тренды?\n"
                "Они формирует основу для стратегических изменений бизнеса, способствует формированию устойчивого конкурентного преимущества и созданию новых рынков сбыта.",
    },
    "Соц/Экон 5-7 лет": {
        "start": "Мы приготовили для вас 2 списка трендов, которые будут иметь влияние в ближайшие 5-7 лет. Проголосуйте за топ-3 из группы социальных и экономических трендов:",
        "end": "Спасибо! Осталось финальное голосование, и нам интересно Ваше мнение. Хотите пройти?",
    },
    "Пол/Техн/Юр 5-7 лет": {
        "start": "И заключительный рейтинг - ждем ваш ответ по группе политических, юридических, технологических трендов:",
        "end": (
            "Спасибо, вы завершили рейтинг! Ваш вклад поможет формировать будущее индустрии знаний."
        ),
    },
}


CATEGORIES = {
    "1": "Политический",
    "2": "Экономический",
    "3": "Социальный",
    "4": "Технологический",
    "5": "Юридический",
    "6": "Экологический",
    "7": "Другое"
}

TIME_ZONES = {
    "1": "1-3 года (Новая нормальность)",
    "2": "3-5 лет (Краткосрочное планирование)",
    "3": "5-7 лет (Среднесрочное планирование)",
    "4": "7+ лет (Долгосрочное планирование)"
}

MAIN_MENU_BUTTONS = [
    ["Записать тренд", "Мои тренды"],
    ["Проголосовать", "Поделиться реакцией"]
]
BACK_BUTTON = [["Назад"]]

def get_category_keyboard():
    keyboard = [
        [InlineKeyboardButton(f"{i}. {CATEGORIES[i]}", callback_data=f"cat_{i}")] for i in CATEGORIES
    ]
    return InlineKeyboardMarkup(keyboard)

def get_time_keyboard():
    keyboard = [
        [InlineKeyboardButton(f"{i}. {TIME_ZONES[i]}", callback_data=f"time_{i}")] for i in TIME_ZONES
    ]
    return InlineKeyboardMarkup(keyboard)

def get_vote_keyboard(votes):
    keyboard = [[InlineKeyboardButton(f"Голосовать: {vote['vote_name']}", callback_data=f"vote_{vote['vote_name']}")] for vote in votes]
    return InlineKeyboardMarkup(keyboard)

def get_trend_actions_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("Изменить", callback_data="change_trends"),
            InlineKeyboardButton("Удалить", callback_data="delete_trends")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_keep_name_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Оставить таким же", callback_data="keep_trend_name")]
    ])

async def send_my_trends(user_id, context, chat_id):
    user_trends = get_user_trends(user_id)
    trends_list = ""
    for idx, trend in enumerate(user_trends, start=1):
        trends_list += f"{idx}. {trend['trend']} ({trend['category']} / {trend['time_zone']})\n"
    user_states[user_id] = {
        "step": "choose_action_for_trend",
        "trends": user_trends
    }
    await context.bot.send_message(
        chat_id=chat_id,
        text=f"Вот список Ваших трендов:\n\n{trends_list}",
        reply_markup=get_trend_actions_keyboard()
    )
    await context.bot.send_message(
        chat_id=chat_id,
        text="Для возврата используйте кнопку снизу.",
        reply_markup=ReplyKeyboardMarkup(BACK_BUTTON, resize_keyboard=True)
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    greeting = (
        "Привет!\n\n"
        "Добро пожаловать в чат-бот спец.проекта Карта трендов KM Conf!\n\n"
        "Мы будем рады вместе обсудить ключевые тренды в области управления знаниями, которые сегодня и завтра меняют ландшафт рынка.\n\n"
        "Главное о карте трендов:\n"
        "Это совместная инициатива KM Conf, SKIMC (Strategic Knowledge and Innovation Management Community) и KMGN (Knowledge Management Global Network).\n"
        "Предназначение – создать актуальную карту ключевых трендов, которые меняют индустрию KM в сотворчестве с наиболее активными её участниками и обновлять её на ежегодной основе.\n\n"
        "Что можно сделать вместе с ботом:\n"
        "1. Изучить текущую версию карты. По итогам события будет создана следующая версия, которой мы поделимся с участниками.\n"
        "2. Повлиять на рейтинг трендов – оценить их важность в рамках разных временных периодов и разных групп трендов.\n"
        "3. Добавить свой тренд – что влияет сегодня на рынок, но не учтено в списке.\n"
        "4.* Продвинутый уровень – поделиться кейсом или реакцией на тренд."
    )

    try:
        with open('data/diagram.png', 'rb') as photo:
            await context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo)
    except Exception as e:
        print(f"Ошибка отправки фото: {e}")
    await update.message.reply_text(greeting)
    keyboard = ReplyKeyboardMarkup(MAIN_MENU_BUTTONS, resize_keyboard=True)
    await update.message.reply_text("Выберите действие:", reply_markup=keyboard)



def get_votes_by_phase(user_id):
    user_voted = set()
    votes_data = get_all_votes()
    for vid, vname in VOTE_MAPPING.items():
        if has_user_voted(user_id, vname):
            user_voted.add(vid)
    if not all(opr in user_voted for opr in PHASES[0]):
        votes = [{**v, "vote_id": vid} for vid in PHASES[0] for v in votes_data if v["vote_name"] == VOTE_MAPPING[vid] and vid not in user_voted]
    elif not all(opr in user_voted for opr in PHASES[1]):
        votes = [{**v, "vote_id": vid} for vid in PHASES[1] for v in votes_data if v["vote_name"] == VOTE_MAPPING[vid] and vid not in user_voted]
    else:
        votes = [{**v, "vote_id": vid} for vid in PHASES[2] for v in votes_data if v["vote_name"] == VOTE_MAPPING[vid] and vid not in user_voted]
    return votes


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    state = user_states.get(user_id)
    if not state:

        if text.lower() == "записать тренд":
            user_states[user_id] = {"step": "choose_category", "category": None, "time_zone": None, "trend": None}
            await update.message.reply_text(
                "*Выберите категорию тренда из списка:*",
                parse_mode="Markdown",
                reply_markup=get_category_keyboard()
            )
            await update.message.reply_text("Для возврата используйте кнопку снизу.", reply_markup=ReplyKeyboardMarkup(BACK_BUTTON, resize_keyboard=True))
            return
        if text.lower() == "мои тренды":
            await send_my_trends(user_id, context, update.effective_chat.id)
            return
        if text.lower() == "проголосовать":
            votes = get_votes_by_phase(user_id)
            if not votes:
                await update.message.reply_text(FINAL_MESSAGE, reply_markup=ReplyKeyboardMarkup(MAIN_MENU_BUTTONS, resize_keyboard=True))
                user_states.pop(user_id, None)
                return
            await update.message.reply_text(
                "Доступные голосования:",
                reply_markup=get_vote_keyboard(votes)
            )
            await update.message.reply_text("Для возврата используйте кнопку снизу.", reply_markup=ReplyKeyboardMarkup(BACK_BUTTON, resize_keyboard=True))
            user_states[user_id] = {"step": "choose_vote", "votes": votes}
            return
        
        if text.lower() == "поделиться реакцией":
            user_states[user_id] = {"step": "share_case"}
            await update.message.reply_text(
                "✨ Поделитесь своим кейсом или реакцией на тренд!\n\n"
                "Опишите ситуацию, реальный пример или вашу реакцию на тренд, который считаете важным для индустрии управления знаниями. "
                "Ваш опыт поможет другим участникам увидеть тренды глазами практиков!\n\n"
                "Просто отправьте свой текст в ответ на это сообщение."
            )
            await update.message.reply_text("Для возврата используйте кнопку снизу.", reply_markup=ReplyKeyboardMarkup(BACK_BUTTON, resize_keyboard=True))
            return
        
        await update.message.reply_text("Пожалуйста, выберите действие через кнопки ⬇️")
        return
    
        
    if text == "Назад":
        if state.get("step") == "share_case":
            user_states.pop(user_id, None)
            keyboard = ReplyKeyboardMarkup(MAIN_MENU_BUTTONS, resize_keyboard=True)
            await update.message.reply_text("Вы вернулись в главное меню.", reply_markup=keyboard)
            return

        if state.get("step") == "editing_category":
            await send_my_trends(user_id, context, update.effective_chat.id)
            return
        
        if state.get("step") == "editing_time_zone":
            user_states[user_id]["step"] = "editing_category"
            await update.message.reply_text(
                "*Выберите новую категорию тренда:*",
                parse_mode="Markdown",
                reply_markup=get_category_keyboard()
            )
            await update.message.reply_text("Для возврата используйте кнопку снизу.", reply_markup=ReplyKeyboardMarkup(BACK_BUTTON, resize_keyboard=True))
            return
        if state.get("step") == "editing_trend_text":
            user_states[user_id]["step"] = "editing_time_zone"
            await update.message.reply_text(
                "*Выберите новый горизонт планирования тренда:*",
                parse_mode="Markdown",
                reply_markup=get_time_keyboard()
            )
            await update.message.reply_text("Для возврата используйте кнопку снизу.", reply_markup=ReplyKeyboardMarkup(BACK_BUTTON, resize_keyboard=True))
            return
        if state.get("step") == "choose_category":
            user_states.pop(user_id, None)
            keyboard = ReplyKeyboardMarkup(MAIN_MENU_BUTTONS, resize_keyboard=True)
            await update.message.reply_text("Вы вернулись в главное меню.", reply_markup=keyboard)
            return
        if state.get("step") == "choose_time_zone":
            user_states[user_id]["step"] = "choose_category"
            await update.message.reply_text(
                "*Выберите категорию тренда из списка:*",
                parse_mode="Markdown",
                reply_markup=get_category_keyboard()
            )
            await update.message.reply_text("Для возврата используйте кнопку снизу.", reply_markup=ReplyKeyboardMarkup(BACK_BUTTON, resize_keyboard=True))
            return
        if state.get("step") == "input_trend":
            user_states[user_id]["step"] = "choose_time_zone"
            await update.message.reply_text(
                "*Выберите горизонт планирования тренда:*",
                parse_mode="Markdown",
                reply_markup=get_time_keyboard()
            )
            await update.message.reply_text("Для возврата используйте кнопку снизу.", reply_markup=ReplyKeyboardMarkup(BACK_BUTTON, resize_keyboard=True))
            return

        if state.get("step") == "wait_for_poll_answer":
            votes = get_votes_by_phase(user_id)
            if votes:
                user_states[user_id] = {"step": "choose_vote", "votes": votes}
                await update.message.reply_text(
                    "Доступные голосования:",
                    reply_markup=get_vote_keyboard(votes)
                )
                await update.message.reply_text(
                    "Для возврата используйте кнопку снизу.",
                    reply_markup=ReplyKeyboardMarkup(BACK_BUTTON, resize_keyboard=True)
                )
            else:
                user_states.pop(user_id, None)
                keyboard = ReplyKeyboardMarkup(MAIN_MENU_BUTTONS, resize_keyboard=True)
                await update.message.reply_text("Вы вернулись в главное меню.", reply_markup=keyboard)
            return
        user_states.pop(user_id, None)
        keyboard = ReplyKeyboardMarkup(MAIN_MENU_BUTTONS, resize_keyboard=True)
        await update.message.reply_text("Вы вернулись в главное меню.", reply_markup=keyboard)
        return
    if state.get("step") == "input_trend":
        trend_text = text
        category = state["category"]
        time_zone = state["time_zone"]
        save_trend_to_db(user_id, category, time_zone, trend_text)
        user_states.pop(user_id, None)
        keyboard = ReplyKeyboardMarkup(MAIN_MENU_BUTTONS, resize_keyboard=True)
        await update.message.reply_text(
            "Спасибо, что поделились с нами своими мыслями! 😊",
            reply_markup=keyboard
        )
        return
    if state.get("step") == "editing_trend_text":
        trend_text = text
        trend = state["trend_to_edit"]
        success = update_trend(
            trend_id=int(trend["id"]),
            user_id=user_id,
            new_trend_text=trend_text,
            new_category=state["new_category"],
            new_time_zone=state["new_time_zone"]
        )
        await send_my_trends(user_id, context, update.effective_chat.id)
        return
    
    if state and state.get("step") == "share_case":
        case_text = text
        save_user_case(user_id, case_text)
        user_states.pop(user_id, None)
        keyboard = ReplyKeyboardMarkup(MAIN_MENU_BUTTONS, resize_keyboard=True)
        await update.message.reply_text("Спасибо за вашу реакцию! Ваш опыт ценен для нас 🙌", reply_markup=keyboard)
        return



async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    user_id = query.from_user.id
    state = user_states.get(user_id)
    if data.startswith("cat_") and (not state or state.get("step") != "editing_category"):
        cat_num = data.split("_")[1]
        user_states[user_id] = {
            **(state or {}),
            "category": CATEGORIES[cat_num],
            "step": "choose_time_zone"
        }
        await query.answer()
        await query.edit_message_text(
            "*Выберите горизонт планирования тренда:*",
            parse_mode="Markdown",
            reply_markup=get_time_keyboard()
        )
        return
    
    if data.startswith("time_") and (not state or state.get("step") != "editing_time_zone"):
        time_num = data.split("_")[1]
        user_states[user_id]["time_zone"] = TIME_ZONES[time_num].split(" (")[0]
        user_states[user_id]["step"] = "input_trend"
        await query.answer()
        await query.edit_message_text(
            "Теперь напишите свой тренд (или используйте кнопку снизу для возврата):"
        )
        return
    
    if data.startswith("vote_"):
        vote_name = data.replace("vote_", "")
        if has_user_voted(user_id, vote_name):
            await query.answer(text="Вы уже участвовали в этом голосовании!", show_alert=True)
            return
        votes = state["votes"] if state and "votes" in state else get_all_votes()
        vote = next((v for v in votes if v["vote_name"] == vote_name), None)
        if vote:

            poll_msg = poll_messages.get(vote_name, {}).get("start")
            if poll_msg:
                await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text=poll_msg
                )
            poll_message = await context.bot.send_poll(
                chat_id=query.message.chat_id,
                question=f"Голосование: {vote_name}",
                options=vote["trends"],
                is_anonymous=False,
                allows_multiple_answers=True
            )
            user_states[user_id] = {
                "step": "wait_for_poll_answer",
                "vote_name": vote_name,
                "poll_id": poll_message.poll.id
            }
        await query.answer()
        return

    if data == "change_trends":
        user_states[user_id]["step"] = "select_trend_to_edit"
        trends = user_states[user_id]["trends"]
        buttons = [[InlineKeyboardButton(str(i), callback_data=f"edit_{i}")] for i in range(1, len(trends)+1)]
        await query.answer()
        await query.edit_message_text(
            "Выберите номер тренда, который хотите отредактировать:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return
    if data.startswith("edit_"):
        idx = int(data.split("_")[1]) - 1
        trends = user_states[user_id]["trends"]
        if 0 <= idx < len(trends):
            trend = trends[idx]
            user_states[user_id] = {
                "step": "editing_category",
                "trend_to_edit": trend,
                "new_category": None,
                "new_time_zone": None,
                "new_trend_text": None,
                "trends": trends
            }
            await query.answer()
            await query.edit_message_text(
                "*Выберите новую категорию тренда:*",
                parse_mode="Markdown",
                reply_markup=get_category_keyboard()
            )
        else:
            await query.answer("Некорректный номер тренда", show_alert=True)
        return
    if data.startswith("cat_") and state and state.get("step") == "editing_category":
        cat_num = data.split("_")[1]
        user_states[user_id]["new_category"] = CATEGORIES[cat_num]
        user_states[user_id]["step"] = "editing_time_zone"
        await query.answer()
        await query.edit_message_text(
            "*Выберите новый горизонт планирования тренда:*",
            parse_mode="Markdown",
            reply_markup=get_time_keyboard()
        )
        return
    if data.startswith("time_") and state and state.get("step") == "editing_time_zone":
        time_num = data.split("_")[1]
        user_states[user_id]["new_time_zone"] = TIME_ZONES[time_num].split(" (")[0]
        user_states[user_id]["step"] = "editing_trend_text"
        await query.answer()
        await query.edit_message_text(
            "Введите новый текст тренда или нажмите 'Оставить таким же' ⬇️",
            reply_markup=get_keep_name_keyboard()
        )
        return
    if data == "keep_trend_name":
        trend = state["trend_to_edit"]
        success = update_trend(
            trend_id=int(trend["id"]),
            user_id=user_id,
            new_trend_text=None,
            new_category=state["new_category"],
            new_time_zone=state["new_time_zone"]
        )
        await send_my_trends(user_id, context, query.message.chat_id)
        return
    if data == "delete_trends":
        user_states[user_id]["step"] = "select_trend_to_delete"
        trends = user_states[user_id]["trends"]
        buttons = [[InlineKeyboardButton(str(i), callback_data=f"del_{i}")] for i in range(1, len(trends)+1)]
        await query.answer()
        await query.edit_message_text(
            "Выберите номер тренда, который хотите удалить:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return

    if data.startswith("del_"):
        idx = int(data.split("_")[1]) - 1
        trends = user_states[user_id]["trends"]
        if 0 <= idx < len(trends):
            trend = trends[idx]
            delete_trend(int(trend["id"]), user_id)
            await send_my_trends(user_id, context, query.message.chat_id)
        else:
            await query.answer("Некорректный номер тренда", show_alert=True)
        return

async def handle_poll_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.poll_answer.user.id
    poll_id = update.poll_answer.poll_id
    for uid, st in user_states.items():
        if st.get("poll_id") == poll_id:
            vote_name = st["vote_name"]
            option_ids = update.poll_answer.option_ids
            votes = get_all_votes()
            vote = next((v for v in votes if v["vote_name"] == vote_name), None)
            vote_id = None
            for vid, mapping in VOTE_MAPPING.items():
                if mapping == vote_name:
                    vote_id = vid

            if vote and vote_id:
                trend_names = [vote["trends"][idx] for idx in option_ids]
                add_user_vote(user_id, vote_name, trend_names)
                for trend in trend_names:
                    increase_vote_result(vote_name, trend)
                end_msg = poll_messages.get(vote_name, {}).get("end")
                if end_msg:
                    await context.bot.send_message(chat_id=user_id, text=end_msg)
                votes = get_votes_by_phase(user_id)
                if votes:
                    user_states[user_id] = {"step": "choose_vote", "votes": votes}
                    await context.bot.send_message(
                        chat_id=user_id,
                        text="Доступные голосования:",
                        reply_markup=get_vote_keyboard(votes)
                    )
                    await context.bot.send_message(
                        chat_id=user_id,
                        text="Для возврата используйте кнопку снизу.",
                        reply_markup=ReplyKeyboardMarkup(BACK_BUTTON, resize_keyboard=True)
                    )
                else:
                    await context.bot.send_message(
                        chat_id=user_id,
                        text=FINAL_MESSAGE,
                        reply_markup=ReplyKeyboardMarkup(MAIN_MENU_BUTTONS, resize_keyboard=True)
                    )
                    user_states.pop(user_id, None)
            break



def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(PollAnswerHandler(handle_poll_answer))
    app.add_handler(CallbackQueryHandler(handle_callback))
    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
