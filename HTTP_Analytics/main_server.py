from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse

from HTTP_Analytics.helpers import Helpers
from Common.Globals import Global, GlobalConfig

# config
GlobalConfig.set("http_host", "0.0.0.0")
GlobalConfig.set("http_port", 80)

class Server(BaseHTTPRequestHandler):
    # Both use the first part of path as key (ie if url = 'abc.com/path_p0/path_p1/page.html' key = 'path_p0' )
    post_callbacks = {}   # callback sig: (request, data   )
    get_callbacks  = {}   # callback sig: (request         )

    def do_POST(self):
        print( "POST request: ", self.path )

        # get the content from the post request
        content_len = int( self.headers['Content-Length'] )
        post_data = self.rfile.read(content_len)

        if Global.DEBUG:
            print("Data: ", post_data)

        # process request
        self.request = urlparse(self.path)
        status, response_data = self.process_callbacks(self.post_callbacks, post_data)

        # send headed
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.send_header('Access-Control-Allow-origin', '*')
        self.end_headers()
        # reply
        self.wfile.write(response_data.encode())

    def do_GET(self):
        print("GET request: " + self.path)

        # process request
        self.request = urlparse(self.path)
        status, response_data = self.process_callbacks(self.get_callbacks)

        # send headed
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.send_header('Access-Control-Allow-origin', '*')
        self.end_headers()
        # reply
        self.wfile.write(response_data.encode())

    def process_callbacks(self, callbacks, post_data=None):

        status = 404
        response_data = ()
        response = ""
        dir_root = self.request.path.split("/")[1]
        path = '/'.join( self.request.path.split("/")[2:] )
        path = "/" + path

        # remove all trailing '/' if any
        while len(path) > 0 and path[-1] == "/":
            path = path[:-1]

        if dir_root in callbacks:
            print("Directory Found!", dir_root, path)
            if post_data is None:
                response_data = callbacks[dir_root]( path, self.get_query_data() )
            else:
                response_data = callbacks[dir_root]( path, self.get_query_data(), post_data.decode('utf-8') )

            status = response_data[0]

            if status == 200:
                response = response_data[1]

        return status, response

    def get_query_data(self):

        query_data = {}
        querys = self.request.query.split("&")

        for q in querys:
            data = q.split("=", 1)
            if len(data) > 1:
                query_data[data[0]] = data[1]
            elif len(data) == 1:
                query_data[data[0]] = ""

        return query_data


if __name__ == "__main__":

    import server_setup

    print("- Run Test.py to test sql_query ")
    print("- Starting...")

    server_directories = server_setup.ServerSetup(Server)
    server_directories.setup()

    server = HTTPServer( (GlobalConfig.get("http_host"), GlobalConfig.get("http_port")), Server )

    print("- Waiting on you request...")

    while True:
        server.serve_forever()

    server.server_close()
