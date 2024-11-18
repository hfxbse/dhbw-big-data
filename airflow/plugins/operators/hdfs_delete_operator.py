from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

from hooks.hdfs_premium_hook import HdfsPremiumHook


class HdfsDeleteOperator(BaseOperator):
    template_fields = ('path', 'hdfs_conn_id')
    ui_color = '#fcdb03'

    @apply_defaults
    def __init__(
            self,
            path,
            hdfs_conn_id,
            *args, **kwargs):
        """
        :param path: which path to delete
        :type path: string
        :param hdfs_conn_id: airflow connection id of HDFS connection to be used
        :type hdfs_conn_id: string
        """

        super(HdfsDeleteOperator, self).__init__(*args, **kwargs)
        self.path = path
        self.hdfs_conn_id = hdfs_conn_id

    def execute(self, context):
        self.log.info("HdfsDeleteOperator execution started.")

        self.log.info(f"Delete '{self.path}' recursively")

        hh = HdfsPremiumHook(hdfs_conn_id=self.hdfs_conn_id)
        hh.delete(self.path)

        self.log.info("HdfsDeleteOperator done.")
