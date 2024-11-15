from airflow.plugins_manager import AirflowPlugin
from operators.hdfs_put_files_operator import HdfsPutFilesOperator
from hooks.hdfs_premium_hook import HdfsPremiumHook


class HdfsPlugin(AirflowPlugin):
    name = "hdfs_premium_operations"
    operators = [HdfsPutFilesOperator]
    hooks = [HdfsPremiumHook]
    executors = []
    macros = []
    admin_views = []
    flask_blueprints = []
    menu_links = []
