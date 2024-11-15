from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

from hooks.hdfs_premium_hook import HdfsPremiumHook


class HdfsPutFilesOperator(BaseOperator):
    template_fields = ('local_path', 'remote_path', 'hdfs_conn_id')
    ui_color = '#fcdb03'

    @apply_defaults
    def __init__(
            self,
            local_path,
            remote_path,
            hdfs_conn_id,
            *args, **kwargs):
        """
        :param local_path: which path to upload to HDFS
        :type local_path: string
        :param remote_path: where on HDFS upload path to
        :type remote_path: string
        :param hdfs_conn_id: airflow connection id of HDFS connection to be used
        :type hdfs_conn_id: string
        """

        super(HdfsPutFilesOperator, self).__init__(*args, **kwargs)
        self.local_path = local_path
        self.remote_path = remote_path
        self.hdfs_conn_id = hdfs_conn_id

    def execute(self, context):
        self.log.info("HdfsPutFilesOperator execution started.")

        self.log.info(f"Upload path '{self.local_path}' recursively to HDFS '{self.remote_path}'.")

        hh = HdfsPremiumHook(hdfs_conn_id=self.hdfs_conn_id)
        hh.put_files(self.local_path, self.remote_path)

        self.log.info("HdfsPutFilesOperator done.")
