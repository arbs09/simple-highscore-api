from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import sqlite3

app = FastAPI()

class Highscore(BaseModel):
    username: str
    score: int

def get_db_connection():
    conn = sqlite3.connect('highscores.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.post("/highscores/", response_model=Highscore)
def create_highscore(highscore: Highscore):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO highscores (username, score) VALUES (?, ?)', (highscore.username, highscore.score))
    conn.commit()
    conn.close()
    return highscore

@app.get("/highscores/", response_model=List[Highscore])
def get_highscores():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT username, score FROM highscores')
    rows = cursor.fetchall()
    conn.close()
    return [Highscore(username=row['username'], score=row['score']) for row in rows]

@app.get("/highscores/{username}", response_model=Highscore)
def get_highscore(username: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT username, score FROM highscores WHERE username = ?', (username,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return Highscore(username=row['username'], score=row['score'])
    raise HTTPException(status_code=404, detail="Highscore not found")

@app.delete("/highscores/{username}", response_model=Highscore)
def delete_highscore(username: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT username, score FROM highscores WHERE username = ?', (username,))
    row = cursor.fetchone()
    if row:
        cursor.execute('DELETE FROM highscores WHERE username = ?', (username,))
        conn.commit()
        conn.close()
        return Highscore(username=row['username'], score=row['score'])
    conn.close()
    raise HTTPException(status_code=404, detail="Highscore not found")

@app.get("/highscores/current", response_model=Highscore)
def get_top_highscore():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT username, score FROM highscores ORDER BY score DESC LIMIT 1')
    row = cursor.fetchone()
    conn.close()
    if row:
        return Highscore(username=row['username'], score=row['score'])
    raise HTTPException(status_code=404, detail="No highscores available")

@app.get("/highscores/average", response_model=Highscore)
def get_average_highscore():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT AVG(score) FROM highscores')
    average_score = cursor.fetchone()[0]
    conn.close()
    if average_score is not None:
        return Highscore(username="average", score=int(average_score))
    raise HTTPException(status_code=404, detail="No highscores available")