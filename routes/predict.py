import joblib
import pandas as pd
from fastapi import APIRouter
from models.data_preparation import transform_date
from pydantic import BaseModel

model = joblib.load('./models/random_forest_model.pkl')
router = APIRouter(prefix='/predict', tags=['Predict'])


class Input(BaseModel):
    date: str
    wind_gusts_10m_mean: float
    wind_speed_10m_mean: float
    winddirection_10m_dominant: int


class Output(BaseModel):
    date: str
    production: float


@router.post('/', response_model=Output)
def predict(data: Input):
    """
    Predict production for a specific day

    Parameters:
        data (Input): date, wind_gusts_10m_mean, wind_speed_10m_mean, winddirection_10m_dominant

    Returns:
        Output: date, production (predicted)
    """
    df = pd.DataFrame(
        [
            {
                'date': data.date,
                'wind_gusts_10m_mean': data.wind_gusts_10m_mean,
                'wind_speed_10m_mean': data.wind_speed_10m_mean,
                'winddirection_10m_dominant': data.winddirection_10m_dominant,
            }
        ]
    )
    df = transform_date(df)
    prediction = model.predict(df)[0]
    return Output(date=data.date, production=prediction)
