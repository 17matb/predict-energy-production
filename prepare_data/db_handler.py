import os

import pandas as pd
from dotenv import load_dotenv
from supabase import Client, create_client

load_dotenv()

url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_SECRET_KEY')

if not url or not key:
    raise ValueError(
        'Error: `SUPABASE_URL` and `SUPABASE_KEY` environment variables are missing'
    )

supabase: Client = create_client(url, key)


class DBHandler:
    def __init__(self, client: Client) -> None:
        self.client = client

    def insert(self, df_to_insert: pd.DataFrame, table_name: str):
        """
        Insert a provided DataFrame into a specific database table.

        Parameters:
            df_to_insert (pd.DataFrame): DataFrame that will be inserted into the database.
            table_name (str): Database table to insert to.

        Returns:
            None
        """
        df_to_insert['date'] = df_to_insert['date'].dt.strftime('%Y-%m-%d')
        records = df_to_insert.to_dict(orient='records')
        try:
            response = self.client.table(table_name).insert(records).execute()
            print(response)
        except Exception as e:
            print(f'Error: {e}')
        return None

    def fetch(self, table_name: str) -> pd.DataFrame:
        """
        Fetch data from a specific database table and return a DataFrame.

        Parameters:
            table_name (str): Database table to fetch data from.

        Returns:
            self.df_fetched (pd.DataFrame): DataFrame made of fetched data from database.
        """
        try:
            response = self.client.table(table_name).select('*').execute()
            self.df_fetched = pd.DataFrame(response.model_dump().get('data', {}))
            print(self.df_fetched.head())
        except Exception as e:
            print(f'Error: {e}')
        return self.df_fetched
