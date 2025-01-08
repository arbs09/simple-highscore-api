from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
import os

app = FastAPI()

class Highscore(BaseModel):
    score: int

class HighscoreCreate(BaseModel):
    username: str
    score: int

def get_db_connection():
    os.makedirs('db', exist_ok=True)
    conn = sqlite3.connect('db/highscores.db')
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS highscores (
            username TEXT PRIMARY KEY,
            score INTEGER NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

create_tables()

@app.post("/post/", response_model=HighscoreCreate)
def create_or_update_highscore(highscore: HighscoreCreate):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT score FROM highscores WHERE username = ?', (highscore.username,))
    row = cursor.fetchone()
    
    if row:
        current_score = row['score']
        if highscore.score > current_score:
            cursor.execute('''
                UPDATE highscores SET score = ? WHERE username = ?
            ''', (highscore.score, highscore.username))
    else:
        cursor.execute('''
            INSERT INTO highscores (username, score) VALUES (?, ?)
        ''', (highscore.username, highscore.score))
    
    conn.commit()
    conn.close()
    return highscore

@app.get("/", response_model=dict)
def get_highscores():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Höchster Highscore
    cursor.execute('SELECT MAX(score) as score FROM highscores')
    highest_score = cursor.fetchone()['score']
    
    # Durchschnittlicher Highscore
    cursor.execute('SELECT AVG(score) as score FROM highscores')
    average_score = cursor.fetchone()['score']
    
    conn.close()
    
    if highest_score is None or average_score is None:
        raise HTTPException(status_code=404, detail="No highscores available")
    
    return {
        "highest_score": highest_score,
        "average_score": int(average_score)
    }