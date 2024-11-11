from airflow import DAG
from airflow.models import Variable
from airflow.operators.bash_operator import BashOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.http_download_operations import HttpDownloadOperator
from airflow.operators.zip_file_operations import UnzipFileOperator
from airflow.operators.hdfs_operations import HdfsPutFileOperator, HdfsGetFileOperator, HdfsMkdirFileOperator
from airflow.operators.filesystem_operations import ClearDirectoryOperator
from datetime import datetime

from airflow.utils.trigger_rule import TriggerRule

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


RAW_DIRECTORY_PATH = '/user/hadoop/cell-coverage/raw'
DIFF_DIRECTORY_PATH = f'{RAW_DIRECTORY_PATH}/diffs'
TMP_DIR = '/tmp/cell-coverage'


# noinspection PyShadowingNames
def initial_data(dag):
    create_timestamp_file = BashOperator(
        task_id=f'create-timestamp-file',
        bash_command=f'date --iso-8601 >> {TMP_DIR}/timestamp',
        dag=dag
    )

    download_complete_data = HttpDownloadOperator(
        task_id='download-complete-data',
        download_uri=f'https://opencellid.org/ocid/downloads?'
                     f'token={Variable.get("OPEN_CELL_ID_API_KEY")}'
                     f'&type=full'
                     f'&file=cell_towers.csv.gz',
        save_to=f'{TMP_DIR}/cell_towers.csv.gz',
        dag=dag
    )

    unzip_complete_data = UnzipFileOperator(
        task_id='unzip-complete-data',
        zip_file=f'{TMP_DIR}/cell_towers.csv.gz',
        extract_to=f'{TMP_DIR}/cell_towers.csv',
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
        local_file=f'{TMP_DIR}/cell_towers.csv',
        remote_file=f'{RAW_DIRECTORY_PATH}/cell_towers.csv',
        dag=dag
    )

    put_timestamp = HdfsPutFileOperator(
        task_id='put-timestamp',
        hdfs_conn_id='hdfs',
        local_file=f'{TMP_DIR}/timestamp',
        remote_file=f'{RAW_DIRECTORY_PATH}/timestamp',
        dag=dag
    )

    create_timestamp_file >> download_complete_data >> unzip_complete_data >> create_raw_target_directories >> \
    put_initial_data >> put_timestamp

    return create_timestamp_file, put_timestamp


with cell_coverage_dag() as dag:
    load_initial_data = HdfsGetFileOperator(
        task_id='load-initial-data',
        hdfs_conn_id='hdfs',
        remote_file=f'{RAW_DIRECTORY_PATH}/cell_towers.csv',
        local_file=f'{TMP_DIR}/cell_towers.csv',
    )

    download_initial_data = DummyOperator(
        task_id='download-initial-data',
        trigger_rule=TriggerRule.ALL_FAILED,
    )

    create_tmp_dir = BashOperator(
        task_id='create-tmp-dir',
        bash_command=f'mkdir -p {TMP_DIR}',
    )

    clear_tmp_dir = ClearDirectoryOperator(
        task_id='clear-tmp-dir',
        directory=TMP_DIR,
        pattern='*'
    )

    download_initial_start, download_initial_end = initial_data(dag)

    create_tmp_dir >> clear_tmp_dir >> load_initial_data >> download_initial_data

    download_initial_data >> download_initial_start
