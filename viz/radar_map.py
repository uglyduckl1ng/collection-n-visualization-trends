import pandas as pd
import plotly.graph_objects as go
import sys

# Загрузка данных
df = pd.read_csv('C:\\Users\\galov\\OneDrive\\Workspace\\Работа\\Projects\\fffff\\collection-n-visualization-trends\\viz\\examples.csv')

# Определение уникальных категорий и интервалов
categories = df['Категория'].unique()
intervals = ['Сейчас', '1–5 лет', '5–15 лет', '15+ лет']

# Подготовка данных для радарной диаграммы
data = []
for interval in intervals:
    interval_data = []
    for category in categories:
        count = df[(df['Категория'] == category) & (df['Интервал'] == interval)].shape[0]
        interval_data.append(count)
    # Замыкаем круг
    interval_data.append(interval_data[0])
    data.append(go.Scatterpolar(
        r=interval_data,
        theta=list(categories) + [categories[0]],
        fill='toself',
        name=interval
    ))

# Создание фигуры
fig = go.Figure(data=data)
fig.update_layout(
    polar=dict(
        radialaxis=dict(
            visible=True,
            range=[0, max(max(d.r) for d in data)]
        )
    ),
    showlegend=True,
    title='Радарная диаграмма трендов в управлении знаниями'
)

fig.show()
