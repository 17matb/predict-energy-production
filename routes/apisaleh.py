from fastapi import FastAPI, HTTPException
#from productors.productors import ProducteurEolien 

import os
print(os.getcwd())


road = FastAPI()

@road.get("/")
def root():
    return {"Hello": "API"}


# @road.get("/statistics/")
# def get_stats(
#     start=None,
#     end=None
#     ):
#     try:
#         filter_df = ProducteurEolien()
#         filter_df.calculer_production()
#         return filter_df.to_dict(orient="records")
#     except Exception:
#         raise HTTPException(status_code=404, detail="n")

