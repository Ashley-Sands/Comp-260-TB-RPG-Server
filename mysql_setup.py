# this should be run once to setup the database,
# or whenever the database needs changing.
import Common.sql_query as sql

RUN_SQL_TEST = False


def setup():
    database = sql.sql_query( "tb_rpg", True )

    database.add_table( "active_users", [ "uid", "nickname", "lobby_id", "reg_key" ],
                             [ "INT UNSIGNED NULL AUTO_INCREMENT KEY",
                               "VARCHAR(255) NOT NULL",
                               "INT NOT NULL DEFAULT '-1'",
                               "VARCHAR(64) NOT NULL DEFAULT 'None'" ]
                             )

    database.add_table( "lobbies", [ "uid", "level_id", "game_id" ],
                             [ "INT UNSIGNED NULL AUTO_INCREMENT KEY",
                               "INT NOT NULL DEFAULT '-1'",
                               "INT NOT NULL DEFAULT '-1'" ]
                             )

    database.add_table( "games", [ "uid", "available", "ip", "port" ],
                             [ "INT UNSIGNED NULL AUTO_INCREMENT KEY",
                               "BOOL NOT NULL DEFAULT TRUE",
                               "VARCHAR(16) NOT NULL DEFAULT '0.0.0.0'",
                               "INT NOT NULL DEFAULT '-1'" ]
                             )

    database.add_table( "levels", [ "uid", "name", "min_players", "max_players" ],
                             [ "INT UNSIGNED NULL AUTO_INCREMENT KEY",
                               "VARCHAR(255) NOT NULL",
                               "INT NOT NULL DEFAULT '1'",
                               "INT NOT NULL DEFAULT '2'" ]
                             )

    print( "Database Setup Finished!" )


def mysql_test():
    pass


if __name__ == "__main__":

    setup()

    if RUN_SQL_TEST:
        mysql_test()
