import pandas as pd
import requests
from prepare_data.cleaning_utils import CleaningUtils
from prepare_data.data_handler import DataHandler


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
                'rain_sum',
                'precipitation_hours',
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
            print(f'· Column types: {data.get("daily_units", {})}')
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
        print('· Ensuring `date` column type is datetime')
        self.clean_df = CleaningUtils.ensure_datetime(self.clean_df, 'date')
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
        print('· Ensuring `date` column type is datetime')
        self.clean_df = CleaningUtils.ensure_datetime(self.clean_df, 'date')
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
        cols_to_drop = [
            'code_site',
            'code_station',
            'longitude',
            'latitude',
            'libelle_statut',
            'code_methode',
            'date_prod',
            'code_statut',
            'code_qualification',
            'libelle_methode',
            'libelle_qualification',
            'grandeur_hydro_elab',
        ]
        self.clean_df = self.clean_df.drop(cols_to_drop, axis=1)
        print(f'· Length after cleaning: {len(self.clean_df)}')
        print(f'Clean dataframe preview:\n{self.clean_df.head(10)}')
        return pd.DataFrame(self.clean_df)
