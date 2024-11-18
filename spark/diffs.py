from pyspark.sql.types import DateType

from spark_io import *
from spark_io import final_columns

DIFF_DIRECTORY_PATH = f'{RAW_DIRECTORY_PATH}/diffs'

if __name__ == "__main__":
    session = spark_session()
    date_rows = session.read.format('csv').options(
        header='false',
        inferSchema='false',
    ).schema(StructType([
        StructField('date', DateType(), True),
    ])).load(f'{DIFF_DIRECTORY_PATH}/updates').collect()

    dates = [row.date.strftime('%Y-%m-%d') for row in date_rows]

    diffs = calculate_identifier(
        spark_raw_reader(session).load(path=[f'{DIFF_DIRECTORY_PATH}/{date}.csv' for date in dates])
    )

    # Only keep the last update for a specific sender
    last_update_dates = diffs.groupBy([
        diffs.identifier
    ]).agg({'updated': 'max'}).withColumnRenamed('max(updated)', 'last_updated')

    changes = final_columns(
        diffs.join(last_update_dates, ['identifier']).filter(diffs.updated == last_update_dates.last_updated)
    )

    # Merge with old data
    previous = spark_final_reader(session)
    unchanged_identifiers = previous.select(previous.identifier).subtract(changes.select(changes.identifier))
    unchanged = previous.join(unchanged_identifiers, ['identifier'], how='left_semi')

    spark_writer(unchanged.unionByName(changes), override=True)
