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


class CleaningUtils:
    @staticmethod
    def ensure_datetime(df: pd.DataFrame, date_column: str) -> pd.DataFrame:
        if date_column in df.columns:
            df[date_column] = pd.to_datetime(df[date_column], errors='coerce')
        return df

    @staticmethod
    def drop_duplicates_keep_last(df: pd.DataFrame, date_column: str) -> pd.DataFrame:
        if date_column in df.columns:
            df = df.drop_duplicates(subset=[date_column], keep='last')
        return df

    @staticmethod
    def fill_missing_with_monthly_median(
        df: pd.DataFrame,
        value_column: str,
    ) -> pd.DataFrame:
        if df.empty:
            return df
        min_date = df['date'].min()
        max_date = df['date'].max()
        df = df.set_index('date').reindex(
            pd.date_range(start=min_date, end=max_date, freq='D')
        )
        df.index.name = 'date'
        df[value_column] = df[value_column].fillna(
            df.groupby([df.index.year, df.index.month])[value_column].transform(  # pyright: ignore[reportAttributeAccessIssue]
                'median'
            )
        )
        return df.reset_index()

    @staticmethod
    def replace_outliers_with_monthly_median(
        df: pd.DataFrame,
        value_column: str,
    ) -> pd.DataFrame:
        if df.empty:
            return df
        min_value = df[value_column].min()
        max_value = df[value_column].max()
        mask_outliers = (df[value_column] < min_value) | (df[value_column] > max_value)
        monthly_medians = df.groupby([df['date'].dt.year, df['date'].dt.month])[
            value_column
        ].transform('median')
        df.loc[mask_outliers, value_column] = monthly_medians[mask_outliers]
        return df


class EolienneCSVHandler(DataHandler):
    def load(self) -> pd.DataFrame:
        print('\n-> LOADING DATA FROM CSV FILE...')
        self.df = pd.read_csv('./data/prod/prod_eolienne.csv')
        print('· Successfully loaded `Eolienne` CSV data into a dataframe')
        print('· Dataframe preview:')
        print(self.df.head(10))
        return self.df

    def clean(self) -> pd.DataFrame:
        super().clean()
        self.clean_df = self.df.copy()
        print('· Ensuring `date` column type is datetime')
        self.clean_df = CleaningUtils.ensure_datetime(self.clean_df, 'date')
        print('· Dropping eventual duplicates')
        self.clean_df = CleaningUtils.drop_duplicates_keep_last(self.clean_df, 'date')
        print('· Filling missing values with monthly median')
        self.clean_df = CleaningUtils.fill_missing_with_monthly_median(
            self.clean_df, 'prod_eolienne'
        )
        self.clean_df = CleaningUtils.replace_outliers_with_monthly_median(
            self.clean_df, 'prod_eolienne'
        )
        print(f'Clean dataframe preview:\n{self.clean_df.head(10)}')
        print(f'Clean dataframe shape: {self.clean_df.shape}')
        return self.clean_df


class SolaireCSVHandler(DataHandler):
    def load(self) -> pd.DataFrame:
        print('\n-> LOADING DATA FROM CSV FILE...')
        self.df = pd.read_csv('./data/prod/prod_solaire.csv')
        print('· Successfully loaded `Solaire` CSV data into a dataframe')
        print('· Dataframe preview:')
        print(self.df.head(10))
        return self.df

    def clean(self) -> pd.DataFrame:
        super().clean()
        self.clean_df = self.df.copy()
        print('· Ensuring `date` column type is datetime')
        self.clean_df = CleaningUtils.ensure_datetime(self.clean_df, 'date')
        print('· Dropping eventual duplicates')
        self.clean_df = CleaningUtils.drop_duplicates_keep_last(self.clean_df, 'date')
        print('· Filling missing values with monthly median')
        self.clean_df = CleaningUtils.fill_missing_with_monthly_median(
            self.clean_df, 'prod_solaire'
        )
        self.clean_df = CleaningUtils.replace_outliers_with_monthly_median(
            self.clean_df, 'prod_solaire'
        )
        print(f'Clean dataframe preview:\n{self.clean_df.head(10)}')
        print(f'Clean dataframe shape: {self.clean_df.shape}')
        return self.clean_df


class HydroCSVHandler(DataHandler):
    def load(self) -> pd.DataFrame:
        print('\n-> LOADING DATA FROM CSV FILE...')
        self.df = pd.read_csv('./data/prod/prod_hydro.csv')
        print('· Successfully loaded `Hydro` CSV data into a dataframe')
        print('· Dataframe preview:')
        print(self.df.head(10))
        return self.df

    def clean(self) -> pd.DataFrame:
        super().clean()
        self.clean_df = self.df.copy()
        if (
            'date_obs_elab' in self.clean_df.columns
            and 'date' not in self.clean_df.columns
        ):
            print('· Renaming `date_obs_elab` column to `date`')
            self.clean_df = self.clean_df.rename(columns={'date_obs_elab': 'date'})
        print('· Ensuring `date` column type is datetime')
        self.clean_df = CleaningUtils.ensure_datetime(self.clean_df, 'date')
        print('· Dropping eventual duplicates')
        self.clean_df = CleaningUtils.drop_duplicates_keep_last(self.clean_df, 'date')
        print('· Dropping irrelevant values')
        self.clean_df = self.clean_df[
            self.clean_df.groupby(self.clean_df['date'].dt.to_period('M'))[
                'date'
            ].transform('count')
            > 1
        ]
        print('· Filling missing values with monthly median')
        self.clean_df = CleaningUtils.fill_missing_with_monthly_median(
            pd.DataFrame(self.clean_df), 'prod_hydro'
        )
        self.clean_df = CleaningUtils.replace_outliers_with_monthly_median(
            pd.DataFrame(self.clean_df), 'prod_hydro'
        )
        print(f'Clean dataframe preview:\n{self.clean_df.head(10)}')
        print(f'Clean dataframe shape: {self.clean_df.shape}')
        return pd.DataFrame(self.clean_df)


class OpenMeteoAPIHandler(DataHandler):
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
        print('· Renaming `time` column to `date`')
        self.clean_df = self.clean_df.rename(columns={'time': 'date'})
        print(f'Clean dataframe preview:\n{self.clean_df.head(10)}')
        return self.clean_df


class HubEauAPIHandler(DataHandler):
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
        print('· Renaming `date_obs_elab` column to `date`')
        self.clean_df = self.clean_df.rename(columns={'date_obs_elab': 'date'})
        summary = self.clean_df.groupby('libelle_qualification')[
            'resultat_obs_elab'
        ].describe()
        print(
            f'· Deleting {summary["count"]["Douteuse"]} values where `libelle_qualification` == `Douteuse`'
        )
        print(f'· Original length: {len(self.clean_df)}')
        self.clean_df = self.clean_df[
            self.clean_df['libelle_qualification'] != 'Douteuse'
        ]
        print(f'· Length after cleaning: {len(self.clean_df)}')
        print(f'Clean dataframe preview:\n{self.clean_df.head(10)}')
        return pd.DataFrame(self.clean_df)


open_meteo_api_data = OpenMeteoAPIHandler(client=None)
open_meteo_api_data.load()
open_meteo_api_data.explore()
open_meteo_api_data.clean()

hub_eau_api_data = HubEauAPIHandler(client=None)
hub_eau_api_data.load()
hub_eau_api_data.explore()
hub_eau_api_data.clean()

eolienne_csv_data = EolienneCSVHandler(client=None)
eolienne_csv_data.load()
eolienne_csv_data.explore()
eolienne_csv_data.clean()

solaire_csv_data = SolaireCSVHandler(client=None)
solaire_csv_data.load()
solaire_csv_data.explore()
solaire_csv_data.clean()

hydro_csv_data = HydroCSVHandler(client=None)
hydro_csv_data.load()
hydro_csv_data.explore()
hydro_csv_data.clean()
