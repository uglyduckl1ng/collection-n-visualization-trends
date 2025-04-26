import os
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# Имя файла для хранения фраз
FILENAME = 'phrases.csv'

def add_phrase_to_csv(phrase):
    # Проверяем, существует ли файл
    if os.path.exists(FILENAME):
        df = pd.read_csv(FILENAME)
    else:
        df = pd.DataFrame(columns=['phrase'])

    # Добавляем новую фразу
    new_row = pd.DataFrame({'phrase': [phrase]})
    df = pd.concat([df, new_row], ignore_index=True)

    # Сохраняем обновлённый DataFrame в CSV
    df.to_csv(FILENAME, index=False)

def generate_wordcloud():
    # Загружаем фразы из CSV
    df = pd.read_csv(FILENAME)
    text = ' '.join(df['phrase'].astype(str))

    # Генерируем облако слов
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)

    # Создаём папку pics, если она не существует
    if not os.path.exists('pics'):
        os.makedirs('pics')

    # Сохраняем облако слов в папку pics
    wordcloud_image_path = 'pics/wordcloud.png'
    wordcloud.to_file(wordcloud_image_path)

    print(f"Облако слов сохранено в {wordcloud_image_path}")

if __name__ == "__main__":
    while True:
        phrase = input("Введите фразу (или 'выход' для завершения): ").strip()
        if phrase.lower() == 'выход':
            break
        if phrase:
            add_phrase_to_csv(phrase)
            generate_wordcloud()
        else:
            print("Пустой ввод. Пожалуйста, введите фразу.")
