import sqlite3
import json

DB_PATH = "data/trends.db"


def format_time_zone_short(time_zone):
    # Преобразует "1-3 года" -> "1-3"
    if isinstance(time_zone, str) and "-" in time_zone:
        return time_zone.split()[0]
    return time_zone

def save_trend_to_db(user_id, category, time_zone, trend_text, description=None):
    time_zone_short = format_time_zone_short(time_zone)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO trends (user_id, trend_name, category, time_zone, description)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, trend_text, category, time_zone_short, description))
    conn.commit()
    conn.close()

def get_user_trends(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, trend_name, category, time_zone
        FROM trends
        WHERE user_id = ?
    """, (user_id,))
    trends = [
        {
            "id": row[0],
            "trend": row[1],
            "category": row[2],
            "time_zone": row[3]
        }
        for row in cursor.fetchall()
    ]
    conn.close()
    return trends


def update_trend(trend_id, user_id, new_trend_text=None, new_category=None, new_time_zone=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    fields = []
    values = []

    if new_trend_text is not None:
        fields.append("trend_name = ?")
        values.append(new_trend_text)
    if new_category is not None:
        fields.append("category = ?")
        values.append(new_category)
    if new_time_zone is not None:
        values.append(format_time_zone_short(new_time_zone))
        fields.append("time_zone = ?")
    if not fields:
        conn.close()
        return False  # Нет данных для обновления
    values.append(trend_id)
    values.append(user_id)
    sql = f"UPDATE trends SET {', '.join(fields)} WHERE id = ? AND user_id = ?"
    cursor.execute(sql, values)
    conn.commit()
    updated = cursor.rowcount > 0
    conn.close()
    return updated
def delete_trend(trend_id, user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        DELETE FROM trends WHERE id = ? AND user_id = ?
    """, (trend_id, user_id))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted

def get_official_trends():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, trend_name, category, time_zone, description
        FROM trends
        WHERE description IS NOT NULL
    """)
    trends = [
        {
            "id": row[0],
            "trend": row[1],
            "category": row[2],
            "time_zone": row[3],
            "description": row[4]
        }
        for row in cursor.fetchall()
    ]
    conn.close()
    return trends

def get_all_votes():
    """Возвращает список всех голосований"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT vote_name, trends FROM votes")
    votes = [{"vote_name": row[0], "trends": json.loads(row[1])} for row in cursor.fetchall()]
    conn.close()
    return votes

def has_user_voted(user_id, vote_name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM user_vote WHERE user_id = ? AND vote_name = ?", (user_id, vote_name))
    result = cursor.fetchone()
    conn.close()
    return result is not None


def add_user_vote(user_id, vote_name, trend_names):
    """Добавляет запись о голосах пользователя (теперь поддерживает несколько трендов)"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    if isinstance(trend_names, list):
        for trend in trend_names:
            cursor.execute(
                "INSERT INTO user_vote (user_id, vote_name, trend_name) VALUES (?, ?, ?)",
                (user_id, vote_name, trend)
            )
    else:
        cursor.execute(
            "INSERT INTO user_vote (user_id, vote_name, trend_name) VALUES (?, ?, ?)",
            (user_id, vote_name, trend_names)
        )
    conn.commit()
    conn.close()


def increase_vote_result(vote_name, trend_name):
    """Увеличивает количество голосов за тренд в голосовании (или создаёт запись если тренд новый)"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Проверяем, есть ли уже запись
    cursor.execute("SELECT id, vote_amount FROM vote_results WHERE vote_name = ? AND trend_name = ?", (vote_name, trend_name))
    row = cursor.fetchone()
    if row:
        cursor.execute("UPDATE vote_results SET vote_amount = vote_amount + 1 WHERE id = ?", (row[0],))
    else:
        cursor.execute("INSERT INTO vote_results (vote_name, trend_name, vote_amount) VALUES (?, ?, 1)", (vote_name, trend_name))
    conn.commit()
    conn.close()

def get_all_users():

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT user_id FROM trends")
    users = [row[0] for row in cursor.fetchall()]
    conn.close()
    return users

def save_user_case(user_id, case_text):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO user_cases (user_id, "case") VALUES (?, ?)',
        (user_id, case_text)
    )
    conn.commit()
    conn.close()

