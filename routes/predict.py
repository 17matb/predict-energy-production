from fastapi import APIRouter

router = APIRouter(prefix='/predict', tags=['Predict'])


@router.get('/')
def predict():
    return {'prediction': 0}
