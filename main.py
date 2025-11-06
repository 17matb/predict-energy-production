import argparse

from fastapi import FastAPI
from pipeline.pipeline import Pipeline
from prepare_data.db_handler import supabase
from routes import predict

app = FastAPI(
    title="predict-energy-production",
    description="predict-energy-production API",
    version="1.0.0",
)

app.include_router(predict.router)


@app.get("/")
def read_root():
    return {"project": "predict-energy-production"}


def main():
    parser = argparse.ArgumentParser(
        prog="predict-energy-production",
        description="Predict future energy production",
    )
    parser.add_argument(
        "-e",
        "--explore",
        action="store_true",
        help="return data exploration",
    )
    parser.add_argument(
        "-i",
        "--insert",
        action="store_true",
        help="insert clean data into the database",
    )
    parser.add_argument(
        "-p",
        "--production",
        action="store_true",
        help="return production values for a date range",
    )
    parser.add_argument(
        "-t",
        "--train",
        action="store_true",
        help="start a new training for our model",
    )
    parser.add_argument(
        "-P",
        "--predict",
        nargs="*",
        metavar="params",
        help="predict production: optionally you can provide (in order) <date> <wind_gusts> <wind_speed> <wind_direction> OR launch interactive mode",
    )
    arguments = parser.parse_args()
    pipeline = Pipeline(client=supabase)
    if (
        not arguments.explore
        and not arguments.insert
        and not arguments.production
        and not arguments.train
        and arguments.predict is None
    ):
        print(
            "× Please use flags, you may want to read the help message. Use: uv run main.py -h"
        )
    if arguments.explore:
        pipeline.data_exploration()
    if arguments.insert:
        pipeline.db_insertion()
    if arguments.production:
        pipeline.get_production_data()
    if arguments.train:
        pipeline.start_train()
    # if arguments.predict is not None:
    #     if len(arguments.predict) == 4:
    #         pipeline.fetch_prediction(
    #             date=arguments.predict[0],
    #             wind_gusts=arguments.predict[1],
    #             wind_speed=arguments.predict[2],
    #             wind_direction=arguments.predict[3],
    #         )
    #     else:
    #         pipeline.fetch_prediction()


if __name__ == "__main__":
    main()
