import common.sql_query as sql
import hashlib
import time
import DEBUG

class Database:

    def __init__( self ):

        # make sure that the database has been set up
        self.database = sql.sql_query("tb_rpg", True)

        # todo this should be moved into a setup script

        self.database.add_table( "active_users", ["uid", "nickname", "lobby_id", "reg_key"],
                                 ["INT UNSIGNED NULL AUTO_INCREMENT KEY",
                                  "VARCHAR(255) NOT NULL",
                                  "INT NOT NULL DEFAULT '-1'",
                                  "VARCHAR(64) NOT NULL DEFAULT 'None'"]
                                 )

        self.database.add_table( "lobbies", ["uid", "level_id", "game_id"],
                                 ["INT UNSIGNED NULL AUTO_INCREMENT KEY",
                                  "INT NOT NULL DEFAULT '-1'",
                                  "INT NOT NULL DEFAULT '-1'"]
                                 )

        self.database.add_table( "games", ["uid", "available", "ip", "port"],
                                 [ "INT UNSIGNED NULL AUTO_INCREMENT KEY",
                                   "BOOL NOT NULL DEFAULT TRUE",
                                   "VARCHAR(16) NOT NULL DEFAULT '0.0.0.0'",
                                   "INT NOT NULL DEFAULT '-1'"]
                                 )

        self.database.add_table( "levels", ["uid", "name", "min_players", "max_players"],
                                 [ "INT UNSIGNED NULL AUTO_INCREMENT KEY",
                                   "VARCHAR(255) NOT NULL",
                                   "INT NOT NULL DEFAULT '1'",
                                   "INT NOT NULL DEFAULT '2'" ]
                                 )

        DEBUG.DEBUG.print( "Database Inited Successfully!" )

        self.join_lobby(1, 2)


    def add_new_client( self, nickname ):
        """Adds a new client

        :return:    tuple of the client id and reg_id tuple(cid, rid)
        """

        reg_key = hashlib.sha224("{0}{1}".format( nickname, time.time() ).encode() ).hexdigest()

        self.database.insert_row("active_users", ["nickname", "reg_key"], [nickname, reg_key])
        uid = self.database.select_from_table( "active_users", ["uid, reg_key"], ["reg_key"], [reg_key] )[0][0]

        client_id = "client-{0}".format(uid)

        return client_id, reg_key

    def add_new_lobby( self ):

        self.database.insert_row("lobbies", ["level_id"], ["1"])    # TODO: this should just select a level at random.

    def available_lobby_count( self ):

        return self.database.select_from_table("lobbies", ["COUNT(game_id)"], ["game_id<"], ["0"], override_where_cols=True)[0][0]

    def select_all_available_lobbies( self ):
        """

        :return: (tuple) (list (a row) of tuples (the columns), list of current players)
                        [(lobby id, level name, min players, max players), ...],
                        [current_players]...
        """
        query = "SELECT lobbies.uid, levels.uid, levels.name, levels.min_players, levels.max_players" \
                " FROM lobbies JOIN levels ON lobbies.level_id=levels.uid WHERE lobbies.game_id < 0"

        # stitch the current_players count
        lobbies = self.database.execute(query, [])
        current_players = []

        for l in lobbies:
            current_players.append( self.get_lobby_player_count( l[0] ) )

        return lobbies, current_players

    def get_lobby_player_count( self, lobby_id ):

        return self.database.select_from_table("active_users", ["COUNT(lobby_id)"], ["lobby_id"], [lobby_id])[0][0]

    def join_lobby( self, client_id, lobby_id ):

        # check that the user can join the lobby
        query = "SELECT levels.max_players " \
                "FROM lobbies JOIN levels ON lobbies.level_id = levels.uid " \
                "WHERE lobbies.game_id < 0 AND lobbies.uid = %s"

        lobby = self.database.execute( query, [lobby_id] )
        current_players = self.get_lobby_player_count( lobby_id )

        if len(lobby) != 1:  # error not found
            return  # TODO: send error

        if current_players < lobby[0][0]:
            self.database.update_row( "active_users", ["lobby_id"], [lobby_id], ["uid"], [client_id] )

