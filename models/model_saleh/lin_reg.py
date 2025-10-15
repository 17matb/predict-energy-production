import pandas as pd
from prepare_data.db_handler import DBHandler, supabase
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score


class ModelLinearRegression:
    def load(self):
        """Load data from the database and define features and target"""
        self.data = DBHandler(client=supabase).fetch("eolienne")
        self.X = self.data[["wind_speed_10m_mean", "wind_gusts_10m_mean", "winddirection_10m_dominant"]]
        self.y = self.data["prod_eolienne"]

    def split_and_standardize(self):
        """Split the data into train/test and standardize features"""
        # Split the data
        X_train, X_test, y_train, y_test = train_test_split(self.X, self.y, test_size=0.2, random_state=42)

        # Standardize features
        self.scaler = StandardScaler()
        self.X_train_scaled = self.scaler.fit_transform(X_train)
        self.X_test_scaled = self.scaler.transform(X_test)

        # Save target splits
        self.y_train = y_train
        self.y_test = y_test

    def run_model(self):
        """Train Linear Regression, predict, and evaluate"""
        self.model = LinearRegression()
        self.model.fit(self.X_train_scaled, self.y_train)

        # Predict
        y_pred = self.model.predict(self.X_test_scaled)

        # Evaluate
        mse = mean_squared_error(self.y_test, y_pred)
        r2 = r2_score(self.y_test, y_pred)
        print("Pipeline ML Results:")
        print("Mean Squared Error:", mse)
        print("R² Score:", r2)
        return mse, r2
