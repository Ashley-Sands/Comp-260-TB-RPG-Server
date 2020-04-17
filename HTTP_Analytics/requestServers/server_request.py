
import Common.sql_query
import json


class ServerRequest:

    test_request = False
    force_200_status = False

    def post_request(self, page_request, query, data):
        """

        :param page_request:    page that is being requested
        :param query:           url query dict of query data (key=value)
        :param data:            data that has been posted
        :return: (int [status], str [responce] )
        """
        if self.test_request:
            return 200, json.dumps( self.new_response( 200, {"p": page_request,"q": query, "d": data} ) )
        else:
            return 404, "Error: Not Found"

    def get_request(self, page_request, query):
        """

        :param page_request:    page that is being requested
        :param query:           url query dict of query data (key=value)
        :return: (int [status], str [responce] )
        """
        if self.test_request:
            return 200, json.dumps( self.new_response( 200, {"p": page_request, "q": query} ) )
        else:
            return 404, "Error: Not Found"

    def new_response(self, status, response):
        """Creates a new response read for json convert
        :param status:      status code ie 200 or 404
        :param response:    the responce data
        :return:            a dict of response data {status, response}
        """
        response_dict = {}
        response_dict["status"] = status
        response_dict["response"] = response

        return response_dict

    def parse_response(self, response_data):
        """ parse dict to json string

        :param response_data:   response dict
        :return:                status, json str
        """
        json_response = json.dumps(response_data)
        if self.force_200_status:
            return 200, json_response
        else:
            return response_data["status"], json_response
