import argparse

import pyspark
from pyspark.sql.types import StructType, StructField, IntegerType, StringType, DoubleType
from pyspark.sql import SparkSession
from pyspark.sql.functions import hash

HADOOP_BASE_PATH = '/user/hadoop/cell-coverage'
RAW_DIRECTORY_PATH = f'{HADOOP_BASE_PATH}/raw'
FINAL_DIRECTORY_PATH = f'{HADOOP_BASE_PATH}/final'
TMP_DIRECTORY_PATH = f'/tmp/cell-coverage'
TABLE_NAME = 'cell_towers'

# Would be the CDMA American equivalent to GSM
#                2G,    3G,     4G,    5G
TECHNOLOGIES = ['GSM', 'UMTS', 'LTE', 'NR']


def spark_session():
    return SparkSession(pyspark.SparkContext())


def spark_raw_reader(session):
    return session.read.format('csv').options(
        header='true',
        delimiter=',',
        nullValue='null',
        inferSchema='false'
    ).schema(StructType([
        StructField('radio', StringType(), True),
        StructField('mcc', IntegerType(), True),
        StructField('net', IntegerType(), True),
        StructField('area', IntegerType(), True),
        StructField('cell', IntegerType(), True),
        StructField('unit', IntegerType(), True),
        StructField('lon', DoubleType(), True),
        StructField('lat', DoubleType(), True),
        StructField('range', IntegerType(), True),
        StructField('samples', IntegerType(), True),
        StructField('changeable', IntegerType(), True),
        StructField('created', IntegerType(), True),
        StructField('updated', IntegerType(), True),
        StructField('averageSignal', IntegerType(), True),
    ]))


def spark_final_reader(session):
    return session.read.parquet(TMP_DIRECTORY_PATH)


def calculate_identifier(frame):
    return frame.withColumn('identifier', hash(
        frame.radio,
        frame.mcc,
        frame.net,
        frame.area,
        frame.cell,
        frame.unit,
        frame.changeable,
        frame.created,
    ))


def final_columns(frame):
    return frame.select('identifier', 'radio', 'lat', 'lon', 'range')


def get_database_arguments(parser=argparse.ArgumentParser()):
    parser.add_argument("--postgres-user", default='postgres')
    parser.add_argument("--postgres-port", default='5432')
    parser.add_argument("--postgres-host", required=True)
    parser.add_argument("--postgres-password", required=True)

    return parser.parse_args()


def spark_writer(frame, postgres_config):
    values = ', '.join([f"'{technology}'" for technology in TECHNOLOGIES])

    mode = 'overwrite'
    frame = final_columns(frame).filter(f'radio IN ({values})')

    frame.printSchema()
    frame.count()
    frame.show()
    frame = frame.repartition('radio')

    frame.write.format('parquet').mode(mode).option(
        'path',
        FINAL_DIRECTORY_PATH
    ).partitionBy('radio').saveAsTable('cell_towers')

    frame.write.format('jdbc').options(
        url=f'jdbc:postgresql://{postgres_config.postgres_host}:{postgres_config.postgres_port}/{postgres_config.postgres_user}',
        driver='org.postgresql.Driver',
        dbtable=TABLE_NAME,
        user=postgres_config.postgres_user,
        password=postgres_config.postgres_password,
        createTableOptions=
        f'PARTITION BY LIST (radio);' + ' '.join([
            f"CREATE TABLE {TABLE_NAME}_{technology} PARTITION OF {TABLE_NAME} FOR VALUES IN ('{technology}');"
            for technology in TECHNOLOGIES
        ])
    ).mode(mode).save()
