import argparse

from pipeline.pipeline import Pipeline
from prepare_data.api_handlers import HubEauAPIHandler, OpenMeteoAPIHandler
from prepare_data.csv_handlers import (
    EolienneCSVHandler,
    HydroCSVHandler,
    SolaireCSVHandler,
)
from prepare_data.db_handler import DBHandler, supabase
from prepare_data.merge_handler import DataMerger, DataSpliter, HydroDataMerger
from productors.productors import ProducteurEolien, ProducteurHydro, ProducteurSolaire


def main():
    parser = argparse.ArgumentParser(
        prog='predict-energy-production',
        description='Predict future energy production',
    )
    parser.add_argument(
        '-e',
        '--explore',
        action='store_true',
        help='returns data exploration',
    )
    parser.add_argument(
        '-i',
        '--insert',
        action='store_true',
        help='insert clean data into the database',
    )
    arguments = parser.parse_args()
    pipeline = Pipeline(client=supabase)
    if arguments.explore:
        pipeline.data_exploration()
    if arguments.insert:
        pipeline.db_insertion()


def notmain():
    open_meteo_api_data = OpenMeteoAPIHandler()
    open_meteo_api_data.load()
    open_meteo_api_data.explore()
    open_meteo_api_data.clean()

    hub_eau_api_data = HubEauAPIHandler()
    hub_eau_api_data.load()
    hub_eau_api_data.explore()
    hub_eau_api_data.clean()

    eolienne_csv_data = EolienneCSVHandler()
    eolienne_csv_data.load()
    eolienne_csv_data.explore()
    eolienne_csv_data.clean()

    solaire_csv_data = SolaireCSVHandler()
    solaire_csv_data.load()
    solaire_csv_data.explore()
    solaire_csv_data.clean()

    hydro_csv_data = HydroCSVHandler()
    hydro_csv_data.load()
    hydro_csv_data.explore()
    hydro_csv_data.clean()

    # ----- data spliter
    data_s = DataSpliter(open_meteo_api_data.clean_df)
    data_winds, data_solar = data_s.split_data()
    # -----------data hydro merge---------------#
    hydro_data_merge = HydroDataMerger(
        hub_eau_api_data.clean_df,  # pyright: ignore[reportArgumentType]
        open_meteo_api_data.clean_df,
        hydro_csv_data.clean_df,
        'hydro',
    )
    hydro_data_merge.merge_data('date')
    # ------------data wind merge----------------#
    eolienne_data_merge = DataMerger(data_winds, eolienne_csv_data.clean_df, 'eolienne')  # pyright: ignore[reportArgumentType]
    eolienne_data_merge.merge_data('date')
    # -----------------data solar merge-----------#
    solaire_data_merge = DataMerger(data_solar, solaire_csv_data.clean_df, 'solaire')  # pyright: ignore[reportArgumentType]
    solaire_data_merge.merge_data('date')

    eolienne_db_handler = DBHandler(client=supabase)
    eolienne_db_handler.insert(
        df_to_insert=eolienne_data_merge.merge_df,
        table_name='eolienne',
    )

    solaire_db_handler = DBHandler(client=supabase)
    solaire_db_handler.insert(
        df_to_insert=solaire_data_merge.merge_df,
        table_name='solaire',
    )

    hydro_db_handler = DBHandler(client=supabase)
    hydro_db_handler.insert(
        df_to_insert=hydro_data_merge.merge_df,
        table_name='hydro',
    )

    data_eol = ProducteurEolien('eolienne')
    data_eol.load_data('2016-11-10', '2023-09-11')
    data_eol.calculer_production('2016-11-10', '2023-09-11')

    data_eol = ProducteurSolaire('solaire')
    data_eol.load_data('2016-11-10', '2023-09-11')
    data_eol.calculer_production('2016-11-10', '2023-09-11')

    data_eol = ProducteurHydro('hydro')
    data_eol.load_data('2016-11-10', '2023-09-11')
    data_eol.calculer_production('2016-11-10', '2023-09-11')

    data_eol = ProducteurEolien("eolienne")
    data_eol.load_data()
    data_eol.calculer_production()

    data_eol = ProducteurSolaire("solaire")
    data_eol.load_data()
    data_eol.calculer_production()

    data_eol = ProducteurHydro("hydro")
    data_eol.load_data()
    data_eol.calculer_production()


if __name__ == '__main__':
    main()
