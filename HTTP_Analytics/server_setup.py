from HTTP_Analytics.requestServers import TEST_mysql

class ServerSetup:

    def __init__(self, server):
        self.server = server

    def setup(self):
        # start TEST mysql
        test_sql = TEST_mysql.TEST_mysql()
        test_sql.force_200_status = True
        self.add_callback("testSQL", test_sql)


    def add_callback(self, root_dir, _server_request):
        """ Adds the get and post function to the callbacks on server

        :param root_dir:        the root directory of the modules (/my_directory/)
        :param _server_request: instances of server request class
        :return:
        """
        self.server.post_callbacks[root_dir] = _server_request.post_request
        self.server.get_callbacks[root_dir] = _server_request.get_request
