import pandas as pd
import numpy as np
from prepare_data.db_handler import DBHandler, supabase
from sklearn.model_selection import train_test_split


def transform_date(df: pd.DataFrame) -> pd.DataFrame:
    """Transforme la colonne 'date' en variables temporelles (année, mois, jour, jour de la semaine)."""
    if "date" not in df.columns:
        return df

    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    df["day"] = df["date"].dt.day
    df["dayofweek"] = df["date"].dt.dayofweek

    return df.drop(columns=["date"])


def prepare_data(test_size=0.2, random_state=42):
    """Charge, transforme et découpe les données eoliennes."""
    db = DBHandler(client=supabase)
    df = db.fetch("eolienne")

    y = df["prod_eolienne"]
    X = df.drop(columns=["prod_eolienne"])

    X = transform_date(X)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )

    print(f"X_train shape: {X_train.shape}")
    print(f"X_test shape: {X_test.shape}")
    print(f"y_train shape: {y_train.shape}")
    print(f"y_test shape: {y_test.shape}")

    return X_train, X_test, y_train, y_test


# Permet d’exécuter le script directement pour debug
if __name__ == "__main__":
    prepare_data()
