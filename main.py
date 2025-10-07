from prepare_data.api_handlers import HubEauAPIHandler, OpenMeteoAPIHandler
from prepare_data.csv_handlers import (
    EolienneCSVHandler,
    HydroCSVHandler,
    SolaireCSVHandler,
)
from prepare_data.merge_handler import DataMerger, DataSpliter


def main():
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

    # ----- data spliter
    data_s = DataSpliter(open_meteo_api_data.clean_df)
    data_winds, data_solar = data_s.split_data()
    # -----------data hydro merge---------------#
    data_merge = DataMerger(hub_eau_api_data.clean_df, hydro_csv_data.clean_df, 'hydro')  # pyright: ignore[reportArgumentType]
    data_merge.merge_data('date')
    # ------------data wind merge----------------#
    data_merge = DataMerger(data_winds, eolienne_csv_data.clean_df, 'eolienne')  # pyright: ignore[reportArgumentType]
    data_merge.merge_data('date')
    # -----------------data solar merge-----------#
    data_merge = DataMerger(data_solar, solaire_csv_data.clean_df, 'solaire')  # pyright: ignore[reportArgumentType]
    data_merge.merge_data('date')


if __name__ == '__main__':
    main()
