import sys
import os
import json
sys.path.append(os.path.join(os.path.dirname(__file__), 'bot'))

from trend_storage import get_unclustered_trends, add_cluster
import sqlite3

DB_PATH = "data/trends.db"

def get_existing_clusters():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, cluster_name, trends FROM clusters")
    clusters = []
    for row in cursor.fetchall():
        clusters.append({"id": row[0], "name": row[1], "trends": json.loads(row[2])})
    conn.close()
    return clusters

def update_cluster(cluster_id, new_trends):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT trends FROM clusters WHERE id = ?", (cluster_id,))
    current = cursor.fetchone()
    if not current:
        conn.close()
        return False
    trends = set(json.loads(current[0]))
    trends.update(new_trends)
    cursor.execute("UPDATE clusters SET trends = ? WHERE id = ?", (json.dumps(list(trends)), cluster_id))
    conn.commit()
    conn.close()
    return True

def main():
    unclustered = get_unclustered_trends()
    if not unclustered:
        print("Нет новых трендов для распределения.")
        return

    print("\nСвежие тренды:")
    for i, t in enumerate(unclustered, 1):
        print(f"{i}. {t}")

    raw = input("\nВведите номера трендов через запятую для нового кластера или добавления в существующий: ")
    indices = [int(x.strip())-1 for x in raw.split(",") if x.strip().isdigit()]
    selected_trends = [unclustered[i] for i in indices if 0 <= i < len(unclustered)]

    if not selected_trends:
        print("Ничего не выбрано.")
        return

    clusters = get_existing_clusters()
    if clusters:
        print("\nСуществующие кластеры:")
        for c in clusters:
            print(f"{c['id']}. {c['name']} (всего {len(c['trends'])} трендов)")

        mode = input("\nДобавить в (1) новый кластер или (2) существующий? (1/2): ").strip()
        if mode == "2":
            cid = int(input("Введите ID существующего кластера: ").strip())
            if update_cluster(cid, selected_trends):
                print("Тренды успешно добавлены в кластер!")
            else:
                print("Ошибка обновления кластера.")
            return

    name = input("\nВведите название нового кластера: ").strip()
    category = input("Введите категорию кластера: ").strip()
    time_zone = input("Введите временной диапазон кластера: ").strip()
    desc = input("Описание кластера (опционально): ").strip() or None
    add_cluster(name, category, time_zone, selected_trends, desc)
    print("Кластер успешно создан!")

if __name__ == "__main__":
    main()
