from spark_io import *

if __name__ == '__main__':
    db_config = get_database_arguments()

    raw = spark_raw_reader(spark_session()).load(f'{RAW_DIRECTORY_PATH}/cell_towers.csv')
    spark_writer(calculate_identifier(raw), postgres_config=db_config)
