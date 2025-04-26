import os
import csv

data_path = "data/trends.csv"

def save_trend_to_csv(user_id, category, time_zone, trend_text):
    file_exists = os.path.isfile(data_path)

    if not file_exists:
        os.makedirs(os.path.dirname(data_path), exist_ok=True)

    with open(data_path, mode="a", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow(["id", "user_id", "trend", "category", "time_zone"])

        current_id = 1
        if file_exists:
            with open(data_path, mode="r", encoding="utf-8") as f:
                reader = csv.reader(f)
                next(reader)
                ids = [int(row[0]) for row in reader if row]
                if ids:
                    current_id = max(ids) + 1

        writer.writerow([current_id, user_id, trend_text, category, time_zone])

def get_user_trends(user_id):
    if not os.path.exists(data_path):
        return []

    with open(data_path, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        trends = [row for row in reader if int(row["user_id"]) == user_id]

    return trends

def update_trend(trend_id, user_id, new_trend_text=None, new_category=None, new_time_zone=None):
    if not os.path.exists(data_path):
        return False

    updated = False
    rows = []

    with open(data_path, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if int(row["id"]) == trend_id and int(row["user_id"]) == user_id:
                if new_trend_text:
                    row["trend"] = new_trend_text
                if new_category:
                    row["category"] = new_category
                if new_time_zone:
                    row["time_zone"] = new_time_zone
                updated = True
            rows.append(row)

    if updated:
        with open(data_path, mode="w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=["id", "user_id", "trend", "category", "time_zone"])
            writer.writeheader()
            writer.writerows(rows)

    return updated

def delete_trend(trend_id, user_id):
    if not os.path.exists(data_path):
        return False

    deleted = False
    rows = []

    with open(data_path, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if not (int(row["id"]) == trend_id and int(row["user_id"]) == user_id):
                rows.append(row)
            else:
                deleted = True

    if deleted:
        with open(data_path, mode="w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=["id", "user_id", "trend", "category", "time_zone"])
            writer.writeheader()
            writer.writerows(rows)

    return deleted
