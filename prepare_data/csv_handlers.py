import pandas as pd
from prepare_data.cleaning_utils import CleaningUtils
from prepare_data.data_handler import DataHandler


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
