# main.py
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import requests
import os
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

app = FastAPI()

# Configuration (replace with your actual OpenAI API key and endpoint)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_API_URL = os.getenv("OPENAI_API_URL", "http://0.0.0.0:1234/v1")

# Use environment variables for DATABASE_URL
DB_USER = os.getenv("DB_USER", "yourusername")
DB_PASSWORD = os.getenv("DB_PASSWORD", "yourpass")
DB_NAME = os.getenv("DB_NAME", "chatdb")
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@localhost/{DB_NAME}"

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    content: str

# Database connection setup
def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn

# Function to convert datetime objects to strings in a dictionary
def convert_datetime_to_str(data):
    print("convert_datetime_to_str data: ", data)
    if isinstance(data, datetime):
        return data.isoformat()
    elif isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, datetime):
                print("converting: ", data[key], value, )
                data[key] = value.isoformat()
                print("converting: ", data[key], value)
            elif isinstance(data, list) or isinstance(data, tuple):
                for item in value:
                    convert_datetime_to_str(item)
    elif isinstance(data, tuple):
        tmp = list(data)
        for i, value in enumerate(data):
            if isinstance(value, datetime):
                print("converting: ", tmp[i], value, )
                tmp[i] = value.isoformat()
                print("converting: ", tmp[i])
        return tuple(tmp)
    elif isinstance(data, list):
        for i, value in enumerate(data):
            if isinstance(value, datetime):
                print("converting: ", data[i], value, )
                data[i] = value.isoformat()
                print("converting: ", data[i])
            elif isinstance(value, list):
                for item in value:
                    convert_datetime_to_str(item)
    return data

@app.get("/api/messages/latest")
async def get_latest_message():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute("SELECT * FROM messages ORDER BY timestamp DESC LIMIT 2;")
        message = cur.fetchall()
        if not message:
            raise HTTPException(status_code=404, detail="No messages found.")
        return convert_datetime_to_str(message)
    finally:
        cur.close()
        conn.close()

@app.get("/api/messages/history")
async def get_chat_history():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute("SELECT * FROM messages ORDER BY timestamp;")
        messages = cur.fetchall()
        res = [convert_datetime_to_str(message) for message in messages]
        return res
    finally:
        cur.close()
        conn.close()

@app.post("/api/messages/send")
async def send_message(message: Message):
    user_message = {
        "role": "user",
        "content": message.content
    }
    
    # Add the user message to the database
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO messages (role, content) VALUES (%s, %s) RETURNING *;",
            (user_message["role"], user_message["content"])
        )
        fetch_res = cur.fetchone()
        inserted_user_message = convert_datetime_to_str(fetch_res)
        # Get a response from the OpenAI-like API
        payload = {
            "messages": [{"role": inserted_user_message[1], "content": inserted_user_message[2]}],  # Adjust as needed based on your requirements
            "max_tokens": 150
        }
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(f"{OPENAI_API_URL}/chat/completions", json=payload, headers=headers)
        if response.status_code == 200:
            assistant_message = response.json().get('choices', [{}])[0].get('message', {})
            # Add the assistant message to the database
            cur.execute(
                "INSERT INTO messages (role, content) VALUES (%s, %s) RETURNING *;",
                (assistant_message["role"], assistant_message["content"])
            )
            inserted_assistant_message = convert_datetime_to_str(cur.fetchone())
            conn.commit()
            res = {"role": inserted_assistant_message[1], "content": inserted_assistant_message[2]}
            return res
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)
    except Exception as e:
        print(e)
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

# Run the application with: uvicorn main:app --reload