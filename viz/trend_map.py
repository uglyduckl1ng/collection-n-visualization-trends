import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sentence_transformers import SentenceTransformer
from sklearn.cluster import DBSCAN

# Ключевые слова для определения временных зон
zone_keywords = {
    "New Normal": ["ИИ", "искусственный интеллект", "machine learning", "автоматизация"],
    "Reactive Zone": ["гибридная работа", "психологическая безопасность", "ментальное здоровье"],
    "Innovation Zone": ["виртуальная реальность", "VR", "дополненная реальность"],
    "Foresight Zone": ["метавселенная", "метаселенные", "AR"]
}

def determine_zone(term):
    for zone, keywords in zone_keywords.items():
        if any(keyword.lower() in term.lower() for keyword in keywords):
            return zone
    return "Innovation Zone"  # по умолчанию

def analyze_and_visualize_trends(terms, output_path="pics/trend_map.png"):
    model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    embeddings = model.encode(terms)

    clustering_model = DBSCAN(eps=1.0, min_samples=1, metric='cosine')
    labels = clustering_model.fit_predict(embeddings)

    categories = {}
    for label, term in zip(labels, terms):
        categories.setdefault(label, []).append(term)

    zones_order = ["New Normal", "Reactive Zone", "Innovation Zone", "Foresight Zone"]
    zone_to_radius = {zone: i + 1 for i, zone in enumerate(zones_order)}

    data = []
    for label, terms_in_cat in categories.items():
        angle = (360 / len(categories)) * label
        for i, term in enumerate(terms_in_cat):
            zone = determine_zone(term)
            radius = zone_to_radius[zone]
            data.append({
                "term": term,
                "category": label,
                "angle": np.deg2rad(angle + (i * 5)),
                "radius": radius,
                "zone": zone
            })

    df = pd.DataFrame(data)

    plt.figure(figsize=(10, 10))
    ax = plt.subplot(111, polar=True)
    ax.set_theta_direction(-1)
    ax.set_theta_offset(np.pi / 2)

    colors = plt.cm.viridis(np.linspace(0, 1, len(categories)))

    for idx, row in df.iterrows():
        ax.plot(row["angle"], row["radius"], 'o', color=colors[int(row["category"])])
        ax.text(row["angle"], row["radius"] + 0.1, row["term"], fontsize=8, ha='center', va='bottom')

    for i, zone in enumerate(zones_order, start=1):
        ax.plot(np.linspace(0, 2 * np.pi, 100), [i] * 100, '--', label=zone)

    ax.set_rticks([])
    ax.set_xticks([])
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
    ax.set_title("Карта трендов по категориям и временным зонам", va='bottom')

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()

    return output_path
