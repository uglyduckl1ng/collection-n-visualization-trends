import networkx as nx
import matplotlib.pyplot as plt

# Создание графа
G = nx.Graph()

# Добавление узлов (трендов)
G.add_node("Искусственный интеллект", pos=(0, 0))
G.add_node("Машинное обучение", pos=(1, 1))
G.add_node("Большие данные", pos=(2, 0))
G.add_node("Интернет вещей", pos=(3, 1))
G.add_node("Умные города", pos=(4, 0))

# Добавление рёбер (связей между трендами)
G.add_edges_from([
    ("Искусственный интеллект", "Машинное обучение"),
    ("Машинное обучение", "Большие данные"),
    ("Большие данные", "Интернет вещей"),
    ("Интернет вещей", "Умные города")
])

# Получение позиций узлов
pos = nx.get_node_attributes(G, 'pos')

# Визуализация графа
plt.figure(figsize=(10, 5))
nx.draw(G, pos, with_labels=True, node_size=2000, node_color='lightblue', font_size=10, font_weight='bold')
plt.title("Карта трендов")
plt.axis('off')
plt.show()
