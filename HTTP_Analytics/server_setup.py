import HTTP_Analytics.requestServers.server_analytics as server_analytics

class ServerSetup:

    def __init__(self, server):
        self.server = server

    def setup(self):

        analytics = server_analytics.ServerAnalytics()
        analytics.force_200_status = False
        analytics.test_request = True
        self.add_callback("analytics", analytics)


    def add_callback(self, root_dir, _server_request):
        """ Adds the get and post function to the callbacks on server

        :param root_dir:        the root directory of the modules (/my_directory/)
        :param _server_request: instances of server request class
        :return:
        """
        self.server.post_callbacks[root_dir] = _server_request.post_request
        self.server.get_callbacks[root_dir] = _server_request.get_request
