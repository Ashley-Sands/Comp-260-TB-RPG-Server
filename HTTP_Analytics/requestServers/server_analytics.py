import HTTP_Analytics.requestServers.server_request as serverRequest
import Common.sql_query as sql
import json
import random

class ServerAnalytics( serverRequest.ServerRequest ):

    def __init__(self):
        self.database = sql.sql_query( "tb_rpg", True )

    def get_request(self, page_request, query):
        """

        :param page_request:    page that is being requested
        :param query:           url query dict of query data (key=value)
        :return: (int [status], str [responce] )
        """
        page_request = page_request.split("/")
        lobby, game, player = None, None, None

        if len(page_request) > 1:
            page_request = page_request[1:]
            for pr in page_request:
                v = pr.split("!")
                if len(v) > 1:
                    if v[0] == "lobby":
                        lobby = v[1]
                    elif v[0] == "game":
                        game = v[1]
                    elif v[0] == "player":
                        player = v[1]

        page = self.get_lobbies() + str(page_request)
        javascript = self.get_map(lobby, game, player)

        if self.test_request:
            return 200, ServerAnalytics.makeHTML(javascript, str(page))
        else:
            return 404, "Error: Not Found"

    def get_lobbies( self ):

        query = "SELECT lobby_id FROM analytics GROUP BY lobby_id"
        query_games = "SELECT game_id FROM analytics WHERE lobby_id = %s GROUP BY game_id"
        query_players = "SELECT player_id FROM analytics WHERE lobby_id = %s AND game_id = %s GROUP BY player_id"
        data = self.database.execute( query, [], fetch=True )
        links = ""

        links += self.get_link( "ALL", -1 )

        if data is not None and len(data) > 0:
            print("hi")
            for d in data:
                links += self.get_link( "lobby", d[0], indent=2 )
                game_data = self.database.execute( query_games, [d[0]], fetch=True )

                if game_data is not None and len( game_data) > 0:
                    for gd in game_data:
                        links += self.get_link( "lobby!"+str(d[0])+"/game", gd[0], indent=4 )
                        player_data = self.database.execute( query_players, [d[0], gd[0]], fetch=True )

                        if player_data is not None and len(player_data) > 0:
                            for pd in player_data:
                                links += self.get_link(  "lobby!"+str(d[0])+"/game!"+str(gd[0])+"/player", pd[0], indent=6)

        else:
            links = "No Lobbies :("

        return links

    def get_link( self, name, id, indent=0 ):
        indent = "-"*indent
        _name = name.replace("!", " - ")
        return '<a href="/analytics/{3}!{1}">{2}{0} - {1}</a><br>'.format( _name, id, indent, name )
        #return str(name) +"::"+ str(id)

    def get_map( self, lobby_id=None, game_id=None, player_id=None ):

        p = ""
        sql_data = ['#']

        if lobby_id is not None:
            p += " AND lobby_id = %s"
            sql_data.append( lobby_id )

        if game_id is not None:
            p += " AND game_id = %s"
            sql_data.append( game_id )

        if player_id is not None:
            p += " AND player_id = %s"
            sql_data.append( player_id )

        query = "SELECT data, lobby_id, game_id, player_id FROM analytics WHERE data_type = %s" + p + " ORDER BY time"

        data = self.database.execute( query, sql_data, fetch=True )

        print(query, sql_data)

        canvas = {}

        for d in data:
            key = str(d[1])+str(d[2])+str(d[3])
            json_data = json.loads( d[0] )

            if key in canvas:
                canvas[key] += "ctx.lineTo("+self.get_pos(json_data["x"])+","+self.get_pos(json_data["z"])+");"
            else:
                colour = "#"+hex(random.randint(16, 225))[2:]+hex(random.randint(16, 225))[2:]+hex(random.randint(16, 225))[2:]
                canvas[key] = 'ctx.lineWidth=1;ctx.lineJoin = "round";ctx.strokeStyle = "'+colour+'";ctx.beginPath();' \
                              "ctx.moveTo("+self.get_pos(json_data["x"])+","+self.get_pos(json_data["z"])+");"

        print( canvas )
        javascript = 'ctx.stroke();\n\n'.join( list(canvas.values()) ) + "ctx.stroke();"
        javascript = 'var c = document.getElementById("map"); c.width = 800; c.height = 600; var ctx = c.getContext("2d");' + javascript

        if data is not None and len(data) > 0:
            return javascript
        else:
            return "/* No data to append */"

    def get_pos( self, pos ):

        mult = 1000
        min = -90
        max = 100
        range = max - min
        dif = pos - min
        print(min, max, range, dif, pos, (dif / range), (dif / range) * mult)
        return str((dif / range) * mult)

    @staticmethod
    def makeHTML( javascript, body ):

        canvas = '<canvas id="map" ></canvas>'
        return"<!DOCTYPE HTML><html><head><title>stats</title></head><body>{1}{2}<script>{0}</script></body></html>".format( javascript, body, canvas )

