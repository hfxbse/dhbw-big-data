from pyspark.sql.types import StructField, StructType, DateType

from spark_io import spark_session, spark_reader, spark_writer, RAW_DIRECTORY_PATH

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

    print(dates)

    raw = spark_reader(session).load(path=[f'{DIFF_DIRECTORY_PATH}/{date}.csv' for date in dates])

    # Only keep the last update for a specific sender
    last_update_dates = raw.groupBy([
        raw.radio,
        raw.mcc,
        raw.net,
        raw.area,
        raw.cell,
        raw.lat,
        raw.lon
    ]).agg({"updated": "max"}).withColumnRenamed("max(updated)", "last_updated")

    frame = raw.join(last_update_dates, [
        "radio",
        "mcc",
        "net",
        "area",
        "cell",
        "lat",
        "lon"
    ]).filter(raw.updated == last_update_dates.last_updated)

    spark_writer(raw, override=False)
