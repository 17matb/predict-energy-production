from prepare_data.api_handlers import HubEauAPIHandler, OpenMeteoAPIHandler
from prepare_data.csv_handlers import (
    EolienneCSVHandler,
    HydroCSVHandler,
    SolaireCSVHandler,
)
from prepare_data.db_handler import DBHandler
from prepare_data.merge_handler import DataMerger, DataSpliter, HydroDataMerger
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
        for handler in self.handlers.values():
            handler.load()
        self._is_loaded = True
        return self

    def data_exploration(self):
        if not self._is_loaded:
            print('· Data needs to be loaded, loading data...')
            self.data_loading()
        for handler in self.handlers.values():
            handler.explore()
        return self

    def data_cleaning(self):
        if not self._is_loaded:
            print('· Data needs to be loaded, loading data...')
            self.data_loading()
        for handler in self.handlers.values():
            handler.clean()
        self._is_clean = True
        return self

    def db_insertion(self):
        if not self._is_clean:
            print('· Data needs to be clean, cleaning data...')
            self.data_cleaning()

        print('· Splitting data...')
        data_s = DataSpliter(self.handlers['open_meteo_api_data'].clean_df)
        data_winds, data_solar = data_s.split_data()

        print('· Merging data...')
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

        print('· Inserting in database...')
        db = DBHandler(client=self.client)

        db.insert(df_to_insert=wind_merge.merge_df, table_name='eolienne')
        db.insert(df_to_insert=solar_merge.merge_df, table_name='solaire')
        db.insert(df_to_insert=hydro_merge.merge_df, table_name='hydro')

        print('· Database insertion complete')
        return self
