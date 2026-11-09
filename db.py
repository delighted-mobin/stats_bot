import supabase
import main as base
from supabase import create_client, Client

async def connect_db(url = base.SUPABASE_URL, key = base.SUPABASE_KEY):
    try:
        db: Client = create_client(url, key)
        return db
    except :
        return -1

async def fetch(table_name:str = "users"):
    try:
        db = await connect_db()
        response = await db.table(table_name).select("*").execute()
        return response.data
    except:
        return -1

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
