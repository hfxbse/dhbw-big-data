import gzip
import os

import requests
from airflow import DAG, AirflowException
from airflow.contrib.operators.spark_submit_operator import SparkSubmitOperator
from airflow.models import Variable
from airflow.operators.bash_operator import BashOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.http_download_operations import HttpDownloadOperator
from airflow.operators.python_operator import PythonOperator
from airflow.operators.zip_file_operations import UnzipFileOperator
from airflow.operators.hdfs_operations import HdfsPutFileOperator, HdfsGetFileOperator, HdfsMkdirFileOperator
from airflow.operators.hdfs_premium_operations import HdfsPutFilesOperator, HdfsMoveOperator, HdfsDeleteOperator
from datetime import datetime

from airflow.utils.trigger_rule import TriggerRule
from future.backports.datetime import timedelta

HADOOP_BASE_PATH = '/user/hadoop/cell-coverage'
FINAL_DIRECTORY_PATH = f'{HADOOP_BASE_PATH}/final'
RAW_DIRECTORY_PATH = '/user/hadoop/cell-coverage/raw'
DIFF_DIRECTORY_PATH = f'{RAW_DIRECTORY_PATH}/diffs'
TMP_DIRECTORY_PATH = '/tmp/cell-coverage'
OPEN_CELL_API_KEY = Variable.get("OPEN_CELL_ID_API_KEY")
SPARK_APPLICATIONS = '/home/airflow/airflow/python'

args = {
    'owner': 'airflow'
}


def cell_coverage_dag():
    return DAG(
        'cell-coverage',
        default_args=args,
        description='Collect cell coverage data from OpenCell',
        schedule_interval='56 18 * * *',
        start_date=datetime(2019, 10, 16),
        catchup=False,
        max_active_runs=1
    )


# noinspection PyShadowingNames
def put_timestamp(task_id, dag):
    return HdfsPutFileOperator(
        task_id=task_id,
        hdfs_conn_id='hdfs',
        local_file=f'{TMP_DIRECTORY_PATH}/timestamp',
        remote_file=f'{RAW_DIRECTORY_PATH}/timestamp',
        dag=dag
    )


# noinspection PyShadowingNames
def download_diffs(dag):
    def download_since_last_timestamp():
        now = datetime.now()
        patch_date = now.replace(hour=0, minute=0, second=0, microsecond=0)

        with open(f'{TMP_DIRECTORY_PATH}/timestamp', 'r') as timestamp:
            update_time = datetime.strptime(timestamp.read(), '%Y-%m-%d\n')

        os.makedirs(f'{TMP_DIRECTORY_PATH}/diffs', exist_ok=True)

        with open(f'{TMP_DIRECTORY_PATH}/diffs/updates', 'w') as dates:
            while patch_date > update_time:
                date = patch_date.strftime('%Y-%m-%d')
                dates.writelines(f'{date}\n')

                try:
                    response = requests.get(
                        f'https://opencellid.org/ocid/downloads?'
                        f'token={OPEN_CELL_API_KEY}&'
                        f'type=diff&'
                        f'file=OCID-diff-cell-export-{date}-T000000.csv.gz'
                    )

                    with open(f'{TMP_DIRECTORY_PATH}/diffs/{date}.csv', 'wb') as out:
                        out.write(gzip.decompress(response.content))

                except Exception as e:
                    raise AirflowException(f'Failed to download diff for date {date}: {e}', e)

                patch_date -= timedelta(days=1)

        with open(f'{TMP_DIRECTORY_PATH}/timestamp', 'w') as timestamp:
            timestamp.write(now.strftime('%Y-%m-%d\n'))

    get_timestamp = HdfsGetFileOperator(
        task_id='get-timestamp',
        hdfs_conn_id='hdfs',
        remote_file=f'{RAW_DIRECTORY_PATH}/timestamp',
        local_file=f'{TMP_DIRECTORY_PATH}/timestamp',
    )

    download = PythonOperator(
        task_id='download-diffs',
        python_callable=download_since_last_timestamp,
        dag=dag
    )

    put_diffs = HdfsPutFilesOperator(
        task_id='put-diffs',
        hdfs_conn_id='hdfs',
        local_path=f'{TMP_DIRECTORY_PATH}/diffs',
        remote_path=f'{RAW_DIRECTORY_PATH}/diffs',
        dag=dag
    )

    update_timestamp = put_timestamp('update-timestamp', dag)

    get_timestamp >> download >> put_diffs >> update_timestamp

    return get_timestamp, update_timestamp


# noinspection PyShadowingNames
def initial_data(dag):
    create_timestamp_file = BashOperator(
        task_id=f'create-timestamp-file',
        bash_command=f'date --iso-8601 >> {TMP_DIRECTORY_PATH}/timestamp',
        dag=dag
    )

    download_complete_data = HttpDownloadOperator(
        task_id='download-complete-data',
        download_uri=f'https://opencellid.org/ocid/downloads?'
                     f'token={OPEN_CELL_API_KEY}'
                     f'&type=full'
                     f'&file=cell_towers.csv.gz',
        save_to=f'{TMP_DIRECTORY_PATH}/cell_towers.csv.gz',
        dag=dag
    )

    unzip_complete_data = UnzipFileOperator(
        task_id='unzip-complete-data',
        zip_file=f'{TMP_DIRECTORY_PATH}/cell_towers.csv.gz',
        extract_to=f'{TMP_DIRECTORY_PATH}/cell_towers.csv',
        dag=dag
    )

    create_raw_target_directories = HdfsMkdirFileOperator(
        task_id='create_raw_target_directories',
        hdfs_conn_id='hdfs',
        directory=DIFF_DIRECTORY_PATH,
        dag=dag
    )

    put_initial_data = HdfsPutFileOperator(
        task_id='put-initial-data',
        hdfs_conn_id='hdfs',
        local_file=f'{TMP_DIRECTORY_PATH}/cell_towers.csv',
        remote_file=f'{RAW_DIRECTORY_PATH}/cell_towers.csv',
        dag=dag
    )

    put_initial_timestamp = put_timestamp('put-initial-timestamp', dag)

    create_timestamp_file >> download_complete_data >> unzip_complete_data >> create_raw_target_directories >> \
    put_initial_data >> put_initial_timestamp

    return create_timestamp_file, put_initial_timestamp


with cell_coverage_dag() as dag:
    check_for_initial_data = HdfsGetFileOperator(
        task_id='check-for-initial-data',
        hdfs_conn_id='hdfs',
        remote_file=f'{RAW_DIRECTORY_PATH}/cell_towers.csv',
        local_file='/dev/null',
    )

    download_initial_data = DummyOperator(
        task_id='download-initial-data',
        trigger_rule=TriggerRule.ALL_FAILED,
    )

    create_tmp_dir = BashOperator(
        task_id='create-tmp-dir',
        bash_command=f'mkdir -p {TMP_DIRECTORY_PATH}',
    )

    clear_tmp_dir = BashOperator(
        task_id='clear-tmp-dir',
        bash_command=f'rm -rf {TMP_DIRECTORY_PATH}/*',
    )

    download_all_diffs = DummyOperator(
        task_id=f'download-remaining-diffs',
        trigger_rule=TriggerRule.ALL_SUCCESS,
    )

    parse_initial_data = SparkSubmitOperator(
        task_id='parse-initial-data',
        conn_id='spark',
        application=f'{SPARK_APPLICATIONS}/init_data.py',
        verbose=True
    )

    move_previous = HdfsMoveOperator(
        task_id='move-previous',
        hdfs_conn_id='hdfs',
        path=FINAL_DIRECTORY_PATH,
        new_path=TMP_DIRECTORY_PATH,
        trigger_rule=TriggerRule.ALL_DONE
    )

    parse_diffs = SparkSubmitOperator(
        task_id='parse-diffs',
        conn_id='spark',
        application=f'{SPARK_APPLICATIONS}/diffs.py',
        verbose=True,
    )

    delete_left_overs = HdfsDeleteOperator(
        task_id='delete-left-overs',
        hdfs_conn_id='hdfs',
        path=FINAL_DIRECTORY_PATH,
        trigger_rule=TriggerRule.ALL_FAILED
    )

    restore_previous = HdfsMoveOperator(
        task_id='restore-previous',
        hdfs_conn_id='hdfs',
        path=TMP_DIRECTORY_PATH,
        new_path=FINAL_DIRECTORY_PATH
    )

    delete_tmp_dir = HdfsDeleteOperator(
        task_id='delete-tmp-previous',
        hdfs_conn_id='hdfs',
        path=TMP_DIRECTORY_PATH,
    )

    create_tmp_dir >> clear_tmp_dir >> check_for_initial_data >> [download_initial_data, download_all_diffs]

    download_initial_start, download_initial_end = initial_data(dag)
    download_initial_data >> download_initial_start
    download_initial_end >> parse_initial_data

    download_diffs_start, download_diffs_end = download_diffs(dag)
    download_all_diffs >> download_diffs_start
    download_diffs_end >> delete_tmp_dir >> move_previous >> parse_diffs >> delete_left_overs >> restore_previous