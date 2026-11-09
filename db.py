import supabase
import os
from supabase import create_client, Client
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")


def connect_db(url = SUPABASE_URL, key = SUPABASE_KEY):
    try:
        db = create_client(url, key)
        return db
    except Exception as e:
        return e

def fetch(table_name:str = "users"):
    try:
        db = connect_db()
        response = db.table(table_name).select("*").execute()
        return response.data
    except Exception as e:
        return e

def select(table_name:str = "users", eq:str = "id", eq_value:str = "0"):
    try:
        db = connect_db()
        response = db.table(table_name).select("*").eq(eq, eq_value).execute()
        return response.data
    except:
        return -1

def insert(table_name:str = "users", data:dict = {}):
    try:
        db = connect_db()
        response = db.table(table_name).insert(data).execute()
        return response.data
    except:
        return -1

def update(table_name:str = "users", eq:str = "id", eq_value:str = "0", data:dict = {}):
    try:
        db = connect_db()
        response = db.table(table_name).update(data).eq(eq, eq_value).execute()
        return response.data
    except:
        return -1

def upsert(table_name:str = "users", data:dict = {}):
    try:
        db = connect_db()
        response = db.table(table_name).upsert(data).execute()
        return response.data
    except:
        return -1

def exist(table_name:str = "users", eq:str = "id", eq_value:int = 0):
    try:
        db = connect_db()
        response = db.table(table_name).select("*").eq(eq, eq_value).execute()
        return True if response.data != [] else False
    except:
        return -1