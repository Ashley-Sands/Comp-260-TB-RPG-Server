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

        self.database.add_table( "levels", ["uid", "level_name", "min_players", "max_players"],
                                 [ "INT UNSIGNED NULL AUTO_INCREMENT KEY",
                                   "VARCHAR(255) NOT NULL",
                                   "INT NOT NULL DEFAULT '1'",
                                   "INT NOT NULL DEFAULT '2'" ]
                                 )

        DEBUG.DEBUG.print( "Database Inited Successfully!" )


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

        return self.database.select_from_table("lobbies", ["*"], ["game_id<"], ["0"], override_where_cols=True)










