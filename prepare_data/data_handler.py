from abc import ABC, abstractmethod
import pandas as pd
from supabase import create_client
import requests

# supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


class DataHandler(ABC):
    def __init__(self, client):
        self.client = client

    @abstractmethod
    def load(self) -> pd.DataFrame:
        pass

    @abstractmethod
    def explore(self):
        pass

    @abstractmethod
    def clean(self) -> pd.DataFrame:
        pass

    def save_to_db(self, table_name: str):
        pass


class APIHandler(DataHandler):
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


class OpenMeteoAPIHandler(APIHandler):
    def load(self) -> pd.DataFrame:
        url = 'https://archive-api.open-meteo.com/v1/archive'
        params = {
            'latitude': '43.62505',
            'longitude': '3.862038',
            'timezone': 'Europe/Berlin',
            'start_date': '2016-09-01',
            'end_date': '2025-09-29',
            'daily': [
                'daylight_duration',
                'sunshine_duration',
                'temperature_2m_mean',
                'wind_gusts_10m_mean',
                'wind_speed_10m_mean',
                'cloud_cover_mean',
                'winddirection_10m_dominant',
                'weather_code',
            ],
        }
        try:
            print('\n-> FETCHING DATA FROM OPEN-METEO API...')
            response = requests.get(url, params)
            response.raise_for_status()
            print(f'· URL: {response.url}')
            data = response.json()
            daily_data = data.get('daily', {})
            self.df = pd.DataFrame(daily_data)
            print('· Successfully loaded API data into a dataframe')
            print('· Dataframe preview:')
            print(self.df.head(10))
        except requests.exceptions.RequestException as e:
            print(f'× API request error: {e}')
        return self.df

    def clean(self) -> pd.DataFrame:
        super().clean()
        self.clean_df = self.df.copy()
        return self.clean_df


class HubEauAPIHandler(APIHandler):
    def load(self) -> pd.DataFrame:
        url = 'https://hubeau.eaufrance.fr/api/v2/hydrometrie/obs_elab'
        params = {
            'code_entite': 'Y321002101',
            'grandeur_hydro_elab': 'QmnJ',
            'date_debut': '2022-07-07',
            'date_fin': ' 2025-02-23',
            'size': '2000',
        }
        try:
            print("\n-> FETCHING DATA FROM HUB'EAU API...")
            response = requests.get(url, params=params)
            response.raise_for_status()
            print(f'· URL: {response.url}')
            data = response.json()
            if 'data' in data:
                self.df = pd.DataFrame(data['data'])
                print('· Successfully loaded API data into a dataframe')
                print('· Dataframe preview:')
                print(self.df.head(10))
            else:
                print('No data found')
        except requests.exceptions.RequestException as e:
            print(f'× API request error: {e}')
        return self.df

    def clean(self) -> pd.DataFrame:
        super().clean()
        self.clean_df = self.df.copy()
        # display libelle_qualification values grouped by resultat_obs_elab to detect the outliers
        summary = self.clean_df.groupby('libelle_qualification')[
            'resultat_obs_elab'
        ].describe()
        print(f'· SUMMARY\n{summary}')
        print('· Deleting values where `libelle_qualification` == `Douteuse`')
        print(f'· Original length: {len(self.clean_df)}')
        self.clean_df = self.clean_df[
            self.clean_df['libelle_qualification'] != 'Douteuse'
        ]
        print(f'· Length after cleaning: {len(self.clean_df)}')
        return pd.DataFrame(self.clean_df)


om_handler = OpenMeteoAPIHandler(client=None)
om_handler.load()
om_handler.explore()
om_handler.clean()

he_handler = HubEauAPIHandler(client=None)
he_handler.load()
he_handler.explore()
he_handler.clean()
