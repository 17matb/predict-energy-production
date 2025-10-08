import pandas as pd
from supabase import create_client, Client
from dotenv import load_dotenv
import os

load_dotenv()

url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_SECRET_KEY')

if not url or not key:
    raise ValueError(
        'Error: `SUPABASE_URL` and `SUPABASE_KEY` environment variables are missing'
    )

supabase: Client = create_client(url, key)


class DBHandler:
    def __init__(
        self, df_to_insert: pd.DataFrame, table_name: str, client: Client
    ) -> None:
        self.df_to_insert = df_to_insert
        self.table_name = table_name
        self.client = client

    def insert(self):
        self.df_to_insert['date'] = self.df_to_insert['date'].dt.strftime('%Y-%m-%d')
        records = self.df_to_insert.to_dict(orient='records')
        try:
            response = self.client.table(self.table_name).insert(records).execute()
            print(response)
        except Exception as e:
            print(f'Error: {e}')
        return None
