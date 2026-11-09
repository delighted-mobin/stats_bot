import supabase
import os
from supabase import create_client, Client
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")


async def connect_db(url = SUPABASE_URL, key = SUPABASE_KEY):
    try:
        db = create_client(url, key)
        return db
    except Exception as e:
        return e

async def fetch(table_name:str = "users"):
    try:
        db = await connect_db()
        response = await db.table(table_name).select("*").execute()
        return response.data
    except Exception as e:
        return e

async def select(table_name:str = "users", eq:str = "id", eq_value:str = "0"):
    try:
        db = await connect_db()
        response = await db.table(table_name).select("*").eq(eq, eq_value).execute()
        return response.data
    except:
        return -1

async def insert(table_name:str = "users", data:dict = {}):
    try:
        db = await connect_db()
        response = await db.table(table_name).insert(data).execute()
        return response.data
    except:
        return -1

async def update(table_name:str = "users", eq:str = "id", eq_value:str = "0", data:dict = {}):
    try:
        db = await connect_db()
        response = await db.table(table_name).update(data).eq(eq, eq_value).execute()
        return response.data
    except:
        return -1

async def upsert(table_name:str = "users", data:dict = {}):
    try:
        db = await connect_db()
        response = await db.table(table_name).upsert(data).execute()
        return response.data
    except:
        return -1
