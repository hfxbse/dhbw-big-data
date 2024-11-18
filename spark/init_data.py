from spark_io import *

if __name__ == '__main__':
    raw = spark_raw_reader(spark_session()).load(f'{RAW_DIRECTORY_PATH}/cell_towers.csv')
    spark_writer(calculate_identifier(raw), override=True)
