import pyspark
from pyspark.sql.types import StructType, StructField, IntegerType, StringType, DoubleType
from pyspark.sql import SparkSession

HADOOP_BASE_PATH = '/user/hadoop/cell-coverage'
RAW_DIRECTORY_PATH = f'{HADOOP_BASE_PATH}/raw'
FINAL_DIRECTORY_PATH = f'{HADOOP_BASE_PATH}/final'
TABLE_NAME = 'cell_towers'
TECHNOLOGIES = ['CDMA', 'GSM', 'UMTS', 'LTE', 'NR']


def spark_reader():
    return SparkSession(pyspark.SparkContext()).read.format('csv').options(
        header='true',
        delimiter=',',
        nullValue='null',
        inferSchema='false'
    ).schema(StructType([
        StructField("radio", StringType(), True),
        StructField("mcc", IntegerType(), True),
        StructField("net", IntegerType(), True),
        StructField("area", IntegerType(), True),
        StructField("cell", IntegerType(), True),
        StructField("unit", IntegerType(), True),
        StructField("lon", DoubleType(), True),
        StructField("lat", DoubleType(), True),
        StructField("range", IntegerType(), True),
        StructField("samples", IntegerType(), True),
        StructField("changeable", IntegerType(), True),
        StructField("created", IntegerType(), True),
        StructField("updated", IntegerType(), True),
        StructField("averageSignal", IntegerType(), True),
    ]))


def spark_writer(frame, override=False):
    mode = 'overwrite' if override else 'append'
    frame = frame.select("radio", "lat", "lon", "range")

    frame.printSchema()
    frame.count()
    frame.show()
    frame = frame.repartition('radio')

    frame.write.format('parquet').mode(mode).option(
        'path',
        FINAL_DIRECTORY_PATH
    ).partitionBy('radio').saveAsTable('cell_towers')

    frame.write.format('jdbc').options(
        url='jdbc:postgresql://user-db:5432/postgres',
        driver='org.postgresql.Driver',
        dbtable=TABLE_NAME,
        user='postgres',
        password='password',
        createTableOptions=
        f'PARTITION BY LIST (radio);' + ' '.join([
            f"CREATE TABLE {TABLE_NAME}_{technology} PARTITION OF {TABLE_NAME} FOR VALUES IN ('{technology}');"
            for technology in TECHNOLOGIES
        ])
    ).mode(mode).save()


if __name__ == '__main__':
    raw = spark_reader().load(f'{RAW_DIRECTORY_PATH}/cell_towers.csv')
    spark_writer(raw, override=True)
