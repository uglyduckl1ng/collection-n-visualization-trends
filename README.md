# Telegram Trend Collection & Visualization Bot

Проект для сбора, ручной обработки и визуализации трендов через Telegram-бота, с возможностью голосований пользователей и REST API для внешнего сайта.

---

## 📦 Функционал

- Сбор трендов от пользователей через Telegram-бота.
- Голосование за тренды (каждый пользователь голосует один раз).
- Ручное формирование и редактирование кластеров через CLI-скрипт.
- REST API (FastAPI):
    - Получение топ-50 кластеров.
    - Получение результатов голосований.
    - Получение трендов с описаниями.

---

## 📁 Структура проекта

collection-n-visualization-trends/
│
├── bot/
│ ├── main.py # Telegram-бот
│ ├── trend_storage.py # Функции работы с БД
│ ├── cluster_manager.py # Ручное управление кластерами
│ └── script.py # Скрипт инициализации БД
│
├── data/
│ └── trends.db # Основная база данных SQLite
│
├── api_server.py # FastAPI-сервер (API)
├── requirements.txt # Зависимости проекта
└── README.md # Описание проекта

---------------------------

## 🚀 Запуск проекта

### 1. Установка зависимостей

```bash
pip install -r requirements.txt

### 2. Инициализация базы данных
```bash
python bot/script.py

### 3. Запуск Telegram-бота

```bash
python bot/main.py

### 4. Ручное управление кластерами

```bash
python bot/cluster_manager.py

### 5. Запуск API-сервера

```bash
uvicorn api_server:app --reload

API будет доступен по адресу http://127.0.0.1:8000/docs

---------------------------

⚙️ Окружение
В проекте используется файл .env для хранения токена Telegram-бота.
Создай .env на основе .env.example и пропиши свой BOT_TOKEN.

📋 Требования
- Python 3.8+
- pip

🧑‍💻 Контакты
Telegram: [@schwarz_pussy]
