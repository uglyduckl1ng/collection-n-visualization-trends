from fastapi import FastAPI
from fastapi.responses import JSONResponse, StreamingResponse
import sqlite3
import json
from pydantic import BaseModel
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware
import csv
import io

DB_PATH = "data/trends.db"
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Описание ручек

class VoteTrendModel(BaseModel):
    trend_name: str
    position: str

class VoteResultModel(BaseModel):
    vote_name: str
    trends: List[VoteTrendModel]

class VoteResultsResponse(BaseModel):
    error: Optional[str]
    results: Optional[List[VoteResultModel]]




# 1. /api/trends/vote_results
@app.get(
    "/api/trends/vote_results",
    response_model=VoteResultsResponse,
    summary="Получить результаты голосований за тренды",
    description="""Метод возвращает результаты голосования за тренды. В каждом голосовании тренды ранжируются по количеству голосов."""
)
def vote_results():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("SELECT vote_name, trends FROM votes")
        votes = cursor.fetchall()
        results = []
        for vote_name, trends_json in votes:
            trends = json.loads(trends_json)
            cursor.execute("""
                SELECT trend_name, vote_amount
                FROM vote_results
                WHERE vote_name = ?
            """, (vote_name,))
            votes_count_dict = {row[0]: row[1] for row in cursor.fetchall()}

            trends_with_votes = []
            for trend in trends:
                count = votes_count_dict.get(trend, 0)
                trends_with_votes.append({
                    "trend_name": trend,
                    "vote_amount": count
                })

            trends_with_votes = sorted(trends_with_votes, key=lambda x: -x["vote_amount"])

            trends_out = []
            for pos, item in enumerate(trends_with_votes, 1):
                trends_out.append({
                    "trend_name": item["trend_name"],
                    "position": str(pos)
                })

            results.append({
                # Маппим vote_name на короткое название
                "vote_name": vote_name,
                "trends": trends_out
            })
        return JSONResponse({"error": None, "results": results})
    except Exception as e:
        return JSONResponse({"error": str(e), "results": None})

def format_time_zone(tz):
    if tz == "1-3":
        return "1-3 года"
    elif tz == "3-5":
        return "3-5 лет"
    elif tz == "5-7":
        return "5-7 лет"
    elif tz == "7+":
        return "7+ лет"
    return tz

@app.get("/api/trends/export_trends", summary="Выгрузка трендов без описания в формате CSV")
def export_trends_no_description():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, user_id, trend_name, category, time_zone 
        FROM trends 
        WHERE description IS NULL OR description = ''
    """)
    rows = cursor.fetchall()
    conn.close()

    # Маппим time_zone перед записью
    formatted_rows = []
    for row in rows:
        row = list(row)
        row[4] = format_time_zone(row[4])
        formatted_rows.append(row)

    output = io.StringIO()
    writer = csv.writer(output, delimiter=";")
    writer.writerow(["id", "user_id", "trend_name", "category", "time_zone"])
    writer.writerows(formatted_rows)
    output.seek(0)

    # BOM для Excel
    bom = '\ufeff'
    content = bom + output.getvalue()

    return StreamingResponse(
        io.StringIO(content),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=trends_no_description.csv"}
    )

