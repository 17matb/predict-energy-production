import numpy as np
import pandas as pd
from prepare_data.db_handler import DBHandler, supabase
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
    root_mean_squared_error,
)
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor


class Predict:
    def load(self):
        self.data = DBHandler(client=supabase).fetch(table_name='eolienne')
        return self

    def prepare(self):
        self.data['date'] = pd.to_datetime(self.data['date'])

        self.data['year'] = self.data['date'].dt.year
        self.data['month'] = self.data['date'].dt.month
        self.data['day_of_year'] = self.data['date'].dt.day_of_year
        self.data['day_of_week'] = self.data['date'].dt.day_of_week

        self.data['month_sin'] = np.sin(2 * np.pi * self.data['month'] / 12)
        self.data['month_cos'] = np.cos(2 * np.pi * self.data['month'] / 12)
        self.data['day_of_year_sin'] = np.sin(
            2 * np.pi * self.data['day_of_year'] / 365.25
        )
        self.data['day_of_year_cos'] = np.cos(
            2 * np.pi * self.data['day_of_year'] / 365.25
        )
        self.data['day_of_week_sin'] = np.sin(2 * np.pi * self.data['day_of_week'] / 7)
        self.data['day_of_week_cos'] = np.cos(2 * np.pi * self.data['day_of_week'] / 7)
        self.data['wind_direction_sin'] = np.sin(
            2 * np.pi * self.data['winddirection_10m_dominant'] / 360
        )
        self.data['wind_direction_cos'] = np.cos(
            2 * np.pi * self.data['winddirection_10m_dominant'] / 360
        )

        self.data = self.data.drop(
            labels=[
                'date',
                'month',
                'day_of_year',
                'day_of_week',
                'winddirection_10m_dominant',
            ],
            axis=1,
        )
        return self

    def run_model(self):
        X = self.data.drop(labels='prod_eolienne', axis=1)
        y = self.data['prod_eolienne']
        print(X.sample(20))
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=1
        )
        model = XGBRegressor(
            n_estimators=500,
            max_depth=6,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=1,
            random_state=1,
            reg_lambda=1.2,
        )
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        metrics = {
            'mean absolute error': mean_absolute_error(y_true=y_test, y_pred=y_pred),
            'mean squared error': mean_squared_error(y_true=y_test, y_pred=y_pred),
            'r squared': r2_score(y_true=y_test, y_pred=y_pred),
            'root mean squared error': root_mean_squared_error(
                y_true=y_test, y_pred=y_pred
            ),
        }
        print(metrics)
