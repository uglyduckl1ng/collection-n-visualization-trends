from fastapi import FastAPI
from fastapi.responses import JSONResponse
import sqlite3
import json
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

DB_PATH = "data/trends.db"
app = FastAPI()

# Описание ручек

class TrendModel(BaseModel):
    trend_name: str

class ClusterModel(BaseModel):
    cluster_name: str
    category: str
    time_zone: str
    description: Optional[str] = None
    trends: List[TrendModel]

class ClustersResponse(BaseModel):
    error: Optional[str]
    results: Optional[List[ClusterModel]]

class VoteTrendModel(BaseModel):
    trend_name: str
    position: str

class VoteResultModel(BaseModel):
    vote_name: str
    trends: List[VoteTrendModel]

class VoteResultsResponse(BaseModel):
    error: Optional[str]
    results: Optional[List[VoteResultModel]]

class TrendDescriptionModel(BaseModel):
    trend_name: str
    description: str

class TrendDescriptionsResponse(BaseModel):
    error: Optional[str]
    results: Optional[List[TrendDescriptionModel]]


# 1. /api/trends/clusters
@app.get(
    "/api/trends/clusters",
    response_model=ClustersResponse,
    summary="Получить топ-50 кластеров по количеству трендов",
    description="""
Метод возвращает 50 кластеров, в которых содержится наибольшее количество трендов.
"""
)
def get_clusters():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT cluster_name, category, time_zone, trends, description
            FROM clusters
        """)
        clusters = []
        for row in cursor.fetchall():
            cluster_name, category, time_zone, trends_json, description = row
            trends_list = json.loads(trends_json)
            clusters.append({
                "cluster_name": cluster_name,
                "category": category,
                "time_zone": time_zone,
                "description": description,
                "trends": [{"trend_name": t} for t in trends_list],
                "trend_count": len(trends_list)
            })
        clusters = sorted(clusters, key=lambda x: x["trend_count"], reverse=True)[:50]
        for c in clusters:
            del c["trend_count"]
        return JSONResponse({"error": None, "results": clusters})
    except Exception as e:
        return JSONResponse({"error": str(e), "results": None})



# 2. /api/trends/vote_results
@app.get(
    "/api/trends/vote_results",
    response_model=VoteResultsResponse,
    summary="Получить результаты голосований за тренды",
    description="""
Метод возвращает результаты голосования за тренды. В каждом голосовании тренды ранжируются по количеству голосов.
"""
)
def get_vote_results():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        # Получаем все уникальные голосования
        cursor.execute("SELECT DISTINCT vote_name FROM vote_results")
        votes = [row[0] for row in cursor.fetchall()]
        results = []
        for vote_name in votes:
            cursor.execute("""
                SELECT trend_name, vote_amount
                FROM vote_results
                WHERE vote_name = ?
                ORDER BY vote_amount DESC
            """, (vote_name,))
            vote_trends = cursor.fetchall()
            trends = []
            for pos, row in enumerate(vote_trends, 1):
                trends.append({
                    "trend_name": row[0],
                    "position": str(pos)
                })
            results.append({
                "vote_name": vote_name,
                "trends": trends
            })
        return JSONResponse({"error": None, "results": results})
    except Exception as e:
        return JSONResponse({"error": str(e), "results": None})


# 3. /api/trends/descriptions
@app.get(
    "/api/trends/descriptions",
    response_model=TrendDescriptionsResponse,
    summary="Получить тренды с описанием для карусели",
    description="""
Метод возвращает тренды с описанием для карусели.
"""
)
def get_trend_descriptions():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT trend_name, description
            FROM trends
            WHERE description IS NOT NULL AND description != ''
        """)
        trends = []
        for row in cursor.fetchall():
            trends.append({
                "trend_name": row[0],
                "description": row[1]
            })
        return JSONResponse({"error": None, "results": trends})
    except Exception as e:
        return JSONResponse({"error": str(e), "results": None})

