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
WEBHOOK = os.environ.get("WEBHOOK", "")

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

async def delete_message(chat_id, message_id):
    return await telegram_request(
        "deleteMessage",
        {
            "chat_id": chat_id,
            "message_id": message_id
        }
    )

async def edit_message(data):
    try:
        return await telegram_request(
            "editMessageText",data
        )
    except Exception as e:
        return str(e)

async def setWebhook(token, secret):
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.post(f"https://api.telegram.org/bot{token}/setWebhook?url={WEBHOOK}/&secret_token={secret}")
            response.raise_for_status()
            return response.json()
    except Exception as e:
        return str(e)

async def fix_database(*args):
    if "fix_token" in args: db.connect_db().table("tokens").delete().eq("token",None).execute()

@app.get("/")
async def index():
    return PlainTextResponse("ok good")


@app.post("/")
async def webhook(request: Request):

    update = await request.json()
    message = update.get("message", {}) or update.get("edited_message", {})

    #https://api.telegram.org/bot<TOKEN>)/setWebhook?url=<URL>/&secret_token=SEC
    bot_sec = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "none")

    if "callback_query" in update:
        class callback:
            data = update.get("callback_query",{})
            id = data.get("id",0)
            chat_id = data.get("message",{}).get("chat",{}).get("id",0)
            message_id = data.get("message",{}).get("message_id",0)
            button = data.get("data",{})
            class user:
                user = update.get("callback_query",{}).get("from",{})
                id = user.get("id", 0)
                first_name = user.get("first_name", "")
                last_name = user.get("last_name", "")
                username = user.get("username","")

        match callback.button:
            case "cb_1":
                await send_message_data(data={
                    "chat_id": callback.chat_id,
                    "text": "نام بات رو وارد کنید:"
                })
                db.set_status(eq="user_id", eq_value=int(callback.user.id), status="enter_bot_name_1")
            case "mb_1":
                token_list = []
                inline_keyboard = []
                db_list = db.select(table_name="tokens", eq="creator_id", eq_value=int(callback.user.id))
                
                if len(db_list) == 0: return

                for i in range(int(len(db_list)/2)):
                    inline_keyboard.append([])
                if int(len(db_list)/2) == 0: inline_keyboard.append([])
                inline_keyboard.append([])

                index = 0
                for data in db_list:
                    if len(data.get("token","")) < 2: break
                    token_list.append(data["token"])
                    index += 1
                    iindex = int((float(index/2)-0.5)) 
                    last_index = iindex - 1 if iindex != 0 else iindex
                
                    if len(inline_keyboard[last_index]) >= 2:
                        inline_keyboard[last_index+1].append({"text": data["secret"], "callback_data": "mb_2", "style": "success"})
                    else:
                        inline_keyboard[last_index].append({"text": data["secret"], "callback_data": "mb_2", "style": "success"})
                
                inline_keyboard.append([{"text": "Back", "callback_data": "back_1", "style": "primary"}])
                await edit_message(data={
                    "chat_id": callback.chat_id,
                    "message_id": callback.message_id,
                    "text": f"""شما {len(token_list)} ربات ثبت شده دارید\nبرای مدیریت هر ربات برروی آن کلیک کنید""",
                    "reply_markup": {
                        "inline_keyboard": inline_keyboard
                    }
                })
            case "back_1":
                db.set_status(eq="user_id", eq_value=int(callback.user.id), status="main")
                await edit_message(data={
                    "chat_id": callback.chat_id,
                    "message_id": callback.message_id,
                    "text": """
                    Create Bot
                    """,
                    "reply_markup": {
                        "inline_keyboard": [
                                [
                                    {"text": "Create bot", "callback_data": "cb_1", "style": "primary"},
                                    {"text": "My bots", "callback_data": "mb_1", "style": "success"}
                                ]
                            ]
                    }
                })

        await telegram_request("answerCallbackQuery", {"callback_query_id": callback.id})
                
        return {"ok": True}

    class msg:
        chat_id = message.get("chat",{}).get("id",0)
        message_id = message.get("message_id",0)
        class user:
            user = message.get("from", {})
            id = user.get("id", 0)
            first_name = user.get("first_name", "")
            last_name = user.get("last_name", "")
            username = user.get("username","")
        chat_type = message.get("chat",{}).get("type","")
        text = str(message.get("text", ""))

    if db.exist(eq="user_id", eq_value=int(msg.user.id)) == False:
        db.insert(data={
            "name": f'{msg.user.first_name} {msg.user.last_name}',
            "username": str(msg.user.username),
            "user_id": int(msg.user.id)
        })

    if msg.text == "/start":
        db.set_status(eq="user_id", eq_value=int(msg.user.id), status="main")
        await send_message_data(data={
            "chat_id": msg.chat_id,
            "text": """
            Create Bot
            """,
            "reply_markup": {
                "inline_keyboard": [
                        [
                            {"text": "Create bot", "callback_data": "cb_1", "style": "primary"},
                            {"text": "My bots", "callback_data": "mb_1", "style": "success"}
                        ]
                    ]
                }
        })

    await send_message(msg.chat_id, str(db.get_status(eq="user_id", eq_value=int(msg.user.id))))

    status = db.get_status(eq="user_id", eq_value=int(msg.user.id))[0]["status"]
    match status:
        case "main":
            pass
        case "enter_bot_name_1":
            if db.connect_db().table("tokens").select("*").eq("creator_id",msg.user.id).eq("name",msg.text.lower()).execute().data != []:
                await send_reply(msg.chat_id, msg.message_id, "نام ربات تکراری هست\nنام دیگری وارد کنید:")
                return
            
            if len(msg.text) > 1 and len(msg.text) <= 32:
                auth = random.randint(1111111111111111, 9999999999999999)

                db.insert(table_name="tokens", data={"name":msg.text.lower(), "creator_id":msg.user.id, "secret":str(auth)})
                db.set_status(eq="user_id", eq_value=int(msg.user.id), status=f"enter_bot_token_1_{auth}")
                await send_reply(msg.chat_id, msg.message_id, "توکن ربات رو وارد کنید:")
        case text if "enter_bot_token_1" in text:
            if len(msg.text) > 10 and len(msg.text) < 120:
                secret = msg.text[0:10]
                auth = text[18:34]

                if db.connect_db().table("tokens").select("*").eq("creator_id",msg.user.id).eq("token",msg.text).execute().data != []:
                    await send_reply(msg.chat_id, msg.message_id, "این توکن قبلا ثبت شده است\nتوکن دیگری وارد کنید:")
                else:
                    resp = await setWebhook(msg.text, secret)
                    if resp.get("result",False) != True:
                        await send_reply(msg.chat_id, "عملیات ست کردن توکن موفقیت آمیز نبود.\nلطفا دوباره تلاش کنید")
                        return {"ok": True}
                    
                    db.connect_db().table("tokens").update({"token":msg.text, "secret":secret, "webhook": WEBHOOK}).eq("creator_id",msg.user.id).eq("secret",auth).execute().data
                    db.set_status(eq="user_id", eq_value=int(msg.user.id), status="main")
                    await send_reply(msg.chat_id, msg.message_id, "توکن با موفقیت اضافه شد")

    return {"ok": True}
