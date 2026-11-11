import os
from main import supabase

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

async def fetch(table_name:str = "users"):
    try:
        response = await supabase.table(table_name).select("*").execute()
        return response.data
    except Exception as e:
        return e

async def select(table_name:str = "users", eq:str = "id", eq_value:str = "0"):
    try:
        response = await supabase.table(table_name).select("*").eq(eq, eq_value).execute()
        return response.data
    except:
        return -1

async def insert(table_name:str = "users", data:dict = {}):
    try:
        response = await supabase.table(table_name).insert(data).execute()
        return response.data
    except:
        return -1

async def update(table_name:str = "users", eq:str = "id", eq_value:str = "0", data:dict = {}):
    try:
        response = await supabase.table(table_name).update(data).eq(eq, eq_value).execute()
        return response.data
    except:
        return -1

async def upsert(table_name:str = "users", data:dict = {}):
    try:
        response = await supabase.table(table_name).upsert(data).execute()
        return response.data
    except:
        return -1

async def exist(table_name:str = "users", eq:str = "id", eq_value:int = 0):
    try:
        response = await supabase.table(table_name).select("*").eq(eq, eq_value).execute()
        return True if response.data != [] else False
    except:
        return -1


async def set_status(table_name:str = "users", eq:str = "id", eq_value:int = 0, status:str = "main"):
    try:
        response = await supabase.table(table_name).update({"status": status}).eq(eq, eq_value).execute()
        return response.data
    except:
        return -1

async def get_status(table_name:str = "users", eq:str = "id", eq_value:int = 0, status:str = "main"):
    try:
        response = await supabase.table(table_name).select("status").eq(eq, eq_value).execute()
        return response.data
    except:
        return -1
