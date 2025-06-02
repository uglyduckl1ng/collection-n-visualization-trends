import sqlite3

DB_PATH = "data/trends.db"

def cleanup_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Удалить таблицы (если существуют)
    cursor.execute("DROP TABLE IF EXISTS clusters")
    print("Таблица clusters удалена (если была).")
    cursor.execute("DROP TABLE IF EXISTS user_forms")
    print("Таблица user_forms удалена (если была).")
    # Удалить тренды без описания
    cursor.execute("DELETE FROM trends WHERE description IS NULL")
    print("Тренды без описания удалены из таблицы trends.")
    conn.commit()
    conn.close()
    print("Готово!")

if __name__ == "__main__":
    cleanup_db()
