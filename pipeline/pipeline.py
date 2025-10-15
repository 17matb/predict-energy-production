from datetime import datetime

from models.model import run_model
from prepare_data.api_handlers import HubEauAPIHandler, OpenMeteoAPIHandler
from prepare_data.csv_handlers import (
    EolienneCSVHandler,
    HydroCSVHandler,
    SolaireCSVHandler,
)
from prepare_data.db_handler import DBHandler
from prepare_data.merge_handler import DataMerger, DataSpliter, HydroDataMerger
from productors.productors import ProducteurEolien, ProducteurHydro, ProducteurSolaire
from supabase import Client


class Pipeline:
    def __init__(self, client: Client):
        self.handlers = {
            'open_meteo_api_data': OpenMeteoAPIHandler(),
            'hub_eau_api_data': HubEauAPIHandler(),
            'eolienne_csv_data': EolienneCSVHandler(),
            'solaire_csv_data': SolaireCSVHandler(),
            'hydro_csv_data': HydroCSVHandler(),
        }
        self._is_loaded = False
        self._is_clean = False
        self.client = client

    def data_loading(self):
        """
        Loops in handlers dict to call their `load()` method.

        Parameters:
            self

        Returns:
            self
        """
        for title, handler in self.handlers.items():
            print(f'\n-> DATA LOADING FOR `{title}` STARTING...')
            handler.load()
        self._is_loaded = True
        return self

    def data_exploration(self):
        """
        Loops in handlers dict to call their `explore()` method.

        Parameters:
            self

        Returns:
            self
        """
        if not self._is_loaded:
            print('· Data needs to be loaded, loading data...')
            self.data_loading()
        for title, handler in self.handlers.items():
            print(f'\n-> DATA EXPLORATION FOR `{title}`:')
            handler.explore()
        return self

    def data_cleaning(self):
        """
        Loops in handlers dict to call their `clean()` method.

        Parameters:
            self

        Returns:
            self
        """
        if not self._is_loaded:
            print('· Data needs to be loaded, loading data...')
            self.data_loading()
        for title, handler in self.handlers.items():
            print(f'\n-> DATA CLEANING FOR `{title}` STARTING...')
            handler.clean()
        self._is_clean = True
        return self

    def db_insertion(self):
        """
        Loops in handlers dict to call their load() method.

        Parameters:
            self

        Returns:
            self
        """
        if not self._is_clean:
            print('· Data needs to be clean, cleaning data...')
            self.data_cleaning()

        print('\n· Splitting data...')
        data_s = DataSpliter(self.handlers['open_meteo_api_data'].clean_df)
        data_winds, data_solar = data_s.split_data()

        print('\n· Merging data...')
        hydro_merge = HydroDataMerger(
            self.handlers['hub_eau_api_data'].clean_df,
            self.handlers['open_meteo_api_data'].clean_df,
            self.handlers['hydro_csv_data'].clean_df,
            'hydro',
        )
        hydro_merge.merge_data('date')

        wind_merge = DataMerger(
            data_winds,  # pyright: ignore[reportArgumentType]
            self.handlers['eolienne_csv_data'].clean_df,
            'eolienne',
        )
        wind_merge.merge_data('date')

        solar_merge = DataMerger(
            data_solar,  # pyright: ignore[reportArgumentType]
            self.handlers['solaire_csv_data'].clean_df,
            'solaire',
        )
        solar_merge.merge_data('date')

        print('\n· Inserting in database...')
        db = DBHandler(client=self.client)

        db.insert(df_to_insert=wind_merge.merge_df, table_name='eolienne')
        db.insert(df_to_insert=solar_merge.merge_df, table_name='solaire')
        db.insert(df_to_insert=hydro_merge.merge_df, table_name='hydro')

        print('· Database insertion process complete')
        return self

    def get_production_data(self):
        start_date_input = input(
            'Start date (leave blank for full range) <YYYY-MM-DD>: '
        )
        if not start_date_input:
            start_date = None
            end_date = None
        else:
            start_year, start_month, start_day = map(int, start_date_input.split('-'))
            start_date = datetime(start_year, start_month, start_day).date()
            end_date_input = input('End date <YYYY-MM-DD>: ')
            if not end_date_input:
                raise ValueError('× End date is needed')
            end_year, end_month, end_day = map(int, end_date_input.split('-'))
            end_date = datetime(end_year, end_month, end_day).date()
            if start_date > end_date:
                raise ValueError('× End date cannot be before start date')
        print(f'· Start date: {start_date}, end date: {end_date}')

        data_eol = ProducteurEolien('eolienne')
        data_eol.load_data(start=start_date, end=end_date)
        data_eol.calculer_production()

        data_sol = ProducteurSolaire('solaire')
        data_sol.load_data(start=start_date, end=end_date)
        data_sol.calculer_production()

        data_hyd = ProducteurHydro('hydro')
        data_hyd.load_data(start=start_date, end=end_date)
        data_hyd.calculer_production()

    def start_prediction(self):
        """
        Lance la phase de prédiction (entraînement, évaluation et sauvegarde du modèle).
        """
        print("\n Démarrage du processus de prédiction...")
        run_model()

