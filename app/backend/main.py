from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import requests
import os
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configuration (replace with your actual OpenAI API key and endpoint)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_API_URL = os.getenv("OPENAI_API_URL", "http://0.0.0.0:1234/v1")

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

messages_history = []

@app.get("/api/messages/latest")
async def get_latest_message():
    if not messages_history:
        raise HTTPException(status_code=404, detail="No messages found.")
    return messages_history[-1]

@app.get("/api/messages/history")
async def get_chat_history():
    return messages_history

@app.post("/api/messages/send")
async def send_message(message: Message):
    user_message = {
        "role": "user",
        "content": message.content
    }
    
    # Add the user message to the history
    messages_history.append(user_message)
    
    # Get a response from the OpenAI-like API
    payload = {
        "messages": messages_history,
        "max_tokens": 150
    }
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(f"{OPENAI_API_URL}/chat/completions", json=payload, headers=headers)
        if response.status_code == 200:
            assistant_message = response.json().get('choices', [{}])[0].get('message', {})
            messages_history.append(assistant_message)
            return assistant_message
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run the application with: uvicorn main:app --reload