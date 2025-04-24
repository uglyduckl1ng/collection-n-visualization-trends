import csv
import os
from datetime import datetime

DATA_PATH = "data/trends.csv"

def save_trend(trend: str, user_id: int):
    os.makedirs("data", exist_ok=True)
    with open(DATA_PATH, mode="a", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([datetime.now().isoformat(), user_id, trend])
