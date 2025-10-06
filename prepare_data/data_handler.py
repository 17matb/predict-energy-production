from abc import ABC, abstractmethod
import pandas as pd
from supabase import create_client


# supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


class DataHandler(ABC):
    def __init__(self, client):
        self.client = client

    @abstractmethod
    def load(self) -> pd.DataFrame:
        self.df = pd.DataFrame()
        return self.df

    def explore(self) -> dict:
        if self.df is None:
            raise ValueError('× Dataframe not found')
        exploration_info = {
            'shape': self.df.shape,
            'columns': self.df.columns.tolist(),
            'dtypes': self.df.dtypes.to_dict(),
            'missing': self.df.isna().sum().to_dict(),
        }
        print('-> EXPLORATION')
        print(f'· SHAPE: {exploration_info["shape"]}')
        print(f'· COLUMNS: {exploration_info["columns"]}')
        print(f'· DTYPES: {exploration_info["dtypes"]}')
        print(f'· MISSING: {exploration_info["missing"]}')
        return exploration_info

    def clean(self) -> pd.DataFrame:
        if self.df is None:
            raise ValueError('× Dataframe not found')
        print('\n-> CLEANING')
        return pd.DataFrame()

    def save_to_db(self, table_name: str):
        pass
