import os.path

class Helpers:

    @staticmethod
    def file_exist(file_name, path=None):
        """ checks if file exist

        :param file_name:   file name with extension (does not start with '/')
        :param path:        path to file (does not end with '/')
        :return:            true if file exist
        """
        full_path = file_name
        if path != None:
            full_path = path + "/" + file_name

        return os.path.isfile( full_path )

    @staticmethod
    def directory_exist(path):
        """ checks if directory exist

        :param path:     path to directory
        :return:        True if exist
        """

        return os.path.exists(path) and os.path.isdir(path)

    @staticmethod
    def create_directory(path):
        """ Creates directory if does not exist
        :param path: path to create
        :return:        True if path was created, else false if already exist
        """
        if not Helpers.directory_exist(path):
            os.mkdir(path)
            return True

        return False

    @staticmethod
    def check_keys(dict_, keys):
        """ search dict for all keys provided

        :param dict_:   dict to search
        :param keys:    keys to search for
        :return:        false if any key does not exist
        """

        for k in keys:
            if k not in dict_:
                return False

        return True
