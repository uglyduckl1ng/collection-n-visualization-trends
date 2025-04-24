import os
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt

def generate_wordcloud():
    trends_path = "data/trends.csv"

    # Проверим, существует ли файл
    if not os.path.exists(trends_path):
        print("Файл с трендами не найден.")
        return

    # Загружаем тренды
    df = pd.read_csv(trends_path, header=None, names=["timestamp", "user_id", "trend"])
    text = ' '.join(df["trend"].astype(str))

    # Генерируем облако слов
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)

    # Сохраняем изображение
    os.makedirs("pics", exist_ok=True)
    wordcloud_path = "pics/wordcloud.png"
    wordcloud.to_file(wordcloud_path)
    print(f"Облако слов сохранено в {wordcloud_path}")
