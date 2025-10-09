from typing import Any
import pandas as pd


class DataSpliter:
    def __init__(self, df: pd.DataFrame):
        self.df = df

    def split_data(self):
        """
        split api data into 2 dataframes
        parameters:
        df : DataFrame
        return : 2 DataFrames
        """
        print('start splitting.......')
        self.group_wind = self.df[
            [
                'date',
                'wind_gusts_10m_mean',
                'wind_speed_10m_mean',
                'winddirection_10m_dominant',
            ]
        ]
        self.group_solar = self.df[
            ['date', 'daylight_duration', 'sunshine_duration', 'cloud_cover_mean']
        ]
        if self.df is not None:
            print('Data wind :')
            print(self.group_wind)
            print('-' * 50)
            print('Data Solar :')
            print(self.group_solar)
        else:
            raise ValueError('data frame is not found')

        return self.group_wind, self.group_solar


class DataMerger:
    def __init__(self, api_df: pd.DataFrame, prod_df: pd.DataFrame, name: str):
        # Store Dataframes from api or csv sources
        self.api_df = api_df
        self.prod_df = prod_df
        self.name = name

    def merge_data(self, on_column, how: Any = 'inner'):
        """
        Merge  available DataFrames on a specific column.
        Parameters:
            on_column (str): The column name to merge on (must exist in both DataFrames)
            how (str): Type of join ('inner')
        Returns:
            pd.DataFrame: merged dataframe
        """
        # Start with API DataFrame
        if self.api_df is not None:
            self.merge_df = self.api_df.copy()
        else:
            raise ValueError('API Data is required to start merging !!')
        # Merge with dataframe from csv
        if self.prod_df is not None:
            self.merge_df = pd.merge(self.merge_df, self.prod_df, on=on_column, how=how)
            print(self.name)
            print(self.merge_df)

            return self.merge_df


class HydroDataMerger(DataMerger):
    def __init__(
        self,
        api_df: pd.DataFrame,
        second_api_df: pd.DataFrame,
        prod_df: pd.DataFrame,
        name: str,
    ):
        super().__init__(api_df=api_df, prod_df=prod_df, name=name)
        self.second_api_df = second_api_df

    def merge_data(self, on_column, how: Any = 'inner'):
        # Start with API DataFrame
        if self.api_df is not None:
            self.merge_df = self.api_df.copy()
        else:
            raise ValueError('API Data is required to start merging !!')
        if self.prod_df is not None:
            self.merge_df = pd.merge(self.merge_df, self.prod_df, on=on_column, how=how)
            self.second_api_df = self.second_api_df[
                ['date', 'rain_sum', 'precipitation_hours']
            ]
            self.merge_df = pd.merge(
                self.merge_df,
                self.second_api_df,  # pyright: ignore[reportArgumentType]
                on=on_column,
                how=how,
            )
            print(self.name)
            print(self.merge_df)
            return self.merge_df

