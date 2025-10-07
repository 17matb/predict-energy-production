import pandas as pd


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

    @staticmethod
    def drop_irrelevant_months(df: pd.DataFrame) -> pd.DataFrame:
        if df.empty or 'date' not in df.columns:
            return df
        df = df[df.groupby(df['date'].dt.to_period('M'))['date'].transform('count') > 1]
        return df