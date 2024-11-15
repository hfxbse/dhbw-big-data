import os.path

from hooks.hdfs_hook import HdfsHook


class HdfsPremiumHook(HdfsHook):
    def put_files(self, local_path, remote_path):
        """
        Put local files to HDFS (hadoop fs -put...)

        :param local_path: path to upload
        :type local_path: string
        :param remote_path: target path on HDFS
        :type remote_path: string
        """

        def full_path(path, local=True):
            return os.path.join(local_path if local else remote_path, path)

        if os.path.isdir(local_path):
            files = [path for path in os.listdir(local_path) if os.path.isfile(full_path(path))]
            for file in files:
                src = full_path(file)
                target = full_path(file, local=False)
                print(f'Upload file {src} to {target}')

                self.putFile(src, target)

            directories = [path for path in os.listdir(local_path) if os.path.isdir(full_path(path))]
            for directory in directories:
                target = full_path(directory, local=False)
                print(f'Move into {directory}')

                self.mkdir(target)
                self.put_files(full_path(directory), target)

        else:
            self.putFile(local_path, remote_path)
