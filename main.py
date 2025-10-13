import argparse

from pipeline.pipeline import Pipeline
from prepare_data.db_handler import supabase


def main():
    parser = argparse.ArgumentParser(
        prog='predict-energy-production',
        description='Predict future energy production',
    )
    parser.add_argument(
        '-e',
        '--explore',
        action='store_true',
        help='returns data exploration',
    )
    parser.add_argument(
        '-i',
        '--insert',
        action='store_true',
        help='insert clean data into the database',
    )
    parser.add_argument(
        '-p',
        '--production',
        action='store_true',
        help='returns production values for a date range',
    )
    parser.add_argument(
        '-P',
        '--predict',
        action='store_true',
        help='predicts production',
    )
    arguments = parser.parse_args()
    pipeline = Pipeline(client=supabase)
    if arguments.explore:
        pipeline.data_exploration()
    if arguments.insert:
        pipeline.db_insertion()
    if arguments.production:
        pipeline.get_production_data()
    if arguments.predict:
        pipeline.start_prediction()


if __name__ == '__main__':
    main()
