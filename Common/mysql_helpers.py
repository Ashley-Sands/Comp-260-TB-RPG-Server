import Common.DEBUG as DEBUG

class MySqlHelpers:
    import mysql.connector as MYSQL

    @staticmethod
    def _connect( host, user, passwd ):
        """Intended for internal use only!"""

        try:
            db_connection = MySqlHelpers.MYSQL.connect( host=host, user=user, passwd=passwd)
            db_cursor = db_connection.cursor()
            DEBUG.LOGS.print( "mysql: Connected" )
        except Exception as err:
            DEBUG.LOGS.print("mysql:", err, message_type=DEBUG.LOGS.MSG_TYPE_ERROR)
            return None, None

        return db_connection, db_cursor


    @staticmethod
    def mysql_connect( host, user, passwd, db_name ):
        """ The is to mimic the sqlite3.connect function with the addison of returning the cursor as well
        so if the db does not exist it is created!
        :return: the connection to the database, and the cursor. None if error
        """

        # check that we can connect to the database.
        db_connection, db_cursor = MySqlHelpers._connect(host, user, passwd)

        if db_connection is None:
            return None, None # there was an error

        # select the database otherwise create it!
        try:
            db_cursor.execute("USE "+db_name)
        except:
            DEBUG.LOGS.print("mysql: Creating new database,", db_name,
                              message_type=DEBUG.LOGS.MSG_TYPE_ERROR)
            db_cursor.execute( "CREATE DATABASE " + db_name )
            db_cursor.execute("USE "+db_name)

        DEBUG.LOGS.print("mysql: database", db_name, "selected")

        return db_connection, db_cursor

    @staticmethod
    def mysql_destroy_database( host, user, passwd, db_name ):
        """Destroys the database in mysql
        WARNING: this will permanently remove all data from the DB
        """

        # check that we can connect to the database.
        db_connection, db_cursor = MySqlHelpers._connect(host, user, passwd)

        if db_connection is None:
            return # there was an error

        try:
            db_cursor.execute( "DROP DATABASE "+db_name )
            DEBUG.LOGS.print("mysql: Database", db_name, "dropped successfully")
        except Exception as e:
            DEBUG.LOGS.print("mysql", e, message_type=DEBUG.LOGS.MSG_TYPE_ERROR)
