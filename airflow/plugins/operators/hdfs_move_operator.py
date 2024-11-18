from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

from hooks.hdfs_premium_hook import HdfsPremiumHook


class HdfsMoveOperator(BaseOperator):
    template_fields = ('path', 'new_path', 'hdfs_conn_id')
    ui_color = '#fcdb03'

    @apply_defaults
    def __init__(
            self,
            path,
            new_path,
            hdfs_conn_id,
            *args, **kwargs):
        """
        :param path: which path to move
        :type path: string
        :param remote_path: the new path to move to
        :type remote_path: string
        :param hdfs_conn_id: airflow connection id of HDFS connection to be used
        :type hdfs_conn_id: string
        """

        super(HdfsMoveOperator, self).__init__(*args, **kwargs)
        self.path = path
        self.new_path = new_path
        self.hdfs_conn_id = hdfs_conn_id

    def execute(self, context):
        self.log.info("HdfsMoveOperator execution started.")

        self.log.info(f"Move '{self.path}' to '{self.new_path}'.")

        hh = HdfsPremiumHook(hdfs_conn_id=self.hdfs_conn_id)
        hh.move(self.path, self.new_path)

        self.log.info("HdfsMoveOperator done.")
