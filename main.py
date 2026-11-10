import os
import random
import httpx
import json
import supabase
import os
import db as db

from supabase import create_client, Client
from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse

app = FastAPI()

TOKEN = os.environ.get("BOT_TOKEN", "")

TELEGRAM_API = f"https://api.telegram.org/bot{TOKEN}"

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

async def send_message_data(data):
    return await telegram_request(
            "sendMessage",data
        )

@app.get("/")
async def index():
    return PlainTextResponse("ok good")


@app.post("/")
async def webhook(request: Request):

    update = await request.json()

    message = update.get("message", {}) or update.get("edited_message", {})
    await send_message(message.get("chat").get("id"), str(update))
    sec = request.headers.get("X-Telegram-Bot-Api-Secret-Token","none")
    await send_message(message.get("chat").get("id"), str(sec))
    sec = request.headers.json()
    await send_message(message.get("chat").get("id"), str(sec))

    try:
        if "callback_query" in update:
            class callback:
                data = update["callback_query"]
                id = data.get("id")
                chat_id = data.get("message").get("chat").get("id")
                message_id = data.get("message").get("message_id")
                button = data.get("data")
                user = data.get("from")

            await telegram_request("answerCallbackQuery", {"callback_query_id": callback.id})
            match callback.button:
                case "signin":
                    await send_message_data(data={
                        "chat_id": callback.chat_id,
                        "text": "شما با موفقیت عضو شدید",
                    })
            return {"ok": True}

        class msg:
            chat_id = message.get("chat").get("id")
            message_id = message.get("message_id")
            user = message.get("from", {})
            chat_type = message.get("chat").get("type")
            text = message.get("text", "")
            username = user.get("username","")

        if db.exist(eq="user_id", eq_value=int(msg.user.get("id", 0))) == False:
            db.insert(data={
                        "name": f'{callback.user.get("first_name", "")} {callback.user.get("last_name", "")}',
                        "username": str(callback.user.get("username", "")),
                        "user_id": int(callback.user.get("id", 0))
            })

        if "/start" or "start" in msg.text:
            await send_message_data(data={
            "chat_id": msg.chat_id,
            "text": """
Create Bot
""",
            "reply_markup": {
                "inline_keyboard": [
                        [
                            {"text": "Create bot", "callback_data": "rain_stat_main", "style": "primary"}
                        ]
                    ]
                }
            })
    except Exception as e:
        return {"ok": False, "error": str(e)}

    return {"ok": True}
