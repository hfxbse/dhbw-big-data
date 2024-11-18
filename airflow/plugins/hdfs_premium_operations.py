from airflow.plugins_manager import AirflowPlugin
from operators.hdfs_put_files_operator import HdfsPutFilesOperator
from operators.hdfs_move_operator import HdfsMoveOperator
from operators.hdfs_delete_operator import HdfsDeleteOperator
from hooks.hdfs_premium_hook import HdfsPremiumHook


class HdfsPlugin(AirflowPlugin):
    name = "hdfs_premium_operations"
    operators = [HdfsPutFilesOperator, HdfsMoveOperator, HdfsDeleteOperator]
    hooks = [HdfsPremiumHook]
    executors = []
    macros = []
    admin_views = []
    flask_blueprints = []
    menu_links = []
