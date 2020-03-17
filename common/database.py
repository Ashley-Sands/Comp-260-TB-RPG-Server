import common.sql_query as sql
import hashlib
import time
import DEBUG

class Database:

    def __init__( self ):

        # make sure that the database has been set up
        self.database = sql.sql_query("tb_rpg", True)

        self.database.add_table( "active_users", ["uid", "nickname", "lobby_id", "game_id", "reg_key"],
                                 ["INT UNSIGNED NULL AUTO_INCREMENT KEY", "VARCHAR(255) NOT NULL",
                                  "INT NOT NULL DEFAULT '-1'", "INT NOT NULL DEFAULT '-1'",
                                  "VARCHAR(64) NOT NULL DEFAULT 'None'"]
                                 )

        DEBUG.DEBUG.print( "Database Inited Successfully!" )


    def add_new_client( self, nickname ):
        """Adds a new client

        :return:    tuple of the client id and reg_id tuple(cid, rid)
        """

        reg_key = hashlib.sha224("{0}{1}".format( nickname, time.time() ).encode() ).hexdigest()

        self.database.insert_row("active_users", ["nickname", "reg_key"], [nickname, reg_key])
        max_uid = self.database.select_from_table( "active_users", ["uid, reg_key"], ["reg_key"], [reg_key] )[0][0]

        client_id = "client-{0}".format(max_uid)

        print("max_uid", max_uid, "\nkey", reg_key)

        return client_id, reg_key
