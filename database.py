import supabase
import os
from supabase import create_client, Client
from main import SUPABASE_URL, SUPABASE_KEY

async def select(table_name:str = "users", data:str = "*"):
    supabase: Client = await create_client(SUPABASE_URL, SUPABASE_KEY)
    response = await supabase.table(table_name).select(data).execute()

    return response.data