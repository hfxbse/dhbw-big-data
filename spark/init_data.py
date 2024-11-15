from spark_io import spark_session, spark_reader, spark_writer, RAW_DIRECTORY_PATH

if __name__ == '__main__':
    raw = spark_reader(spark_session()).load(f'{RAW_DIRECTORY_PATH}/cell_towers.csv')
    spark_writer(raw, override=True)
