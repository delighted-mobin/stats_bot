import os
import random
import httpx
import json
import supabase
import os

from supabase import create_client, Client
from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse

app = FastAPI()

TOKEN = os.environ.get("BOT_TOKEN", "")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

TELEGRAM_API = f"https://api.telegram.org/bot{TOKEN}"

import db as db

async def telegram_request(method, data):
    if not TOKEN:
        print("BOT_TOKEN is not set.")
        return None

    try:
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.post(
                f"{TELEGRAM_API}/{method}",
                json=data
            )
            response.raise_for_status()
            return response.json()

    except Exception as e:
        print("Telegram API Error:", e)
        return None


async def send_reply(chat_id, message_id, text):
    return await telegram_request(
        "sendMessage",
        {
            "chat_id": chat_id,
            "text": text,
            "reply_to_message_id": message_id
        }
    )


async def send_message(chat_id, text):
    return await telegram_request(
        "sendMessage",
        {
            "chat_id": chat_id,
            "text": text
        }
    )

@app.get("/")
async def index():
    return PlainTextResponse("ok good")


@app.post("/")
async def webhook(request: Request):

    update = await request.json()

    message = update.get("message") or update.get("edited_message")

    if not message:
        return {"ok": True}

    if message.get("from", {}).get("is_bot", False):
        return {"ok": True}

    class msg:
        chat_id = message["chat"]["id"]
        message_id = message.get("message_id")
        user = message.get("from", {})
        chat_type = message["chat"]["type"]
        text = message.get("text", "")

    x = await db.fetch()
    await send_message(msg.chat_id, str(x))


    return {"ok": True}
