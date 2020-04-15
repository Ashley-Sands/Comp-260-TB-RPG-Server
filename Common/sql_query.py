# The has been taken from my comp-280 project and adapted for this project
# GitHub Repo: https://github.com/Ashley-Sands/Comp-280-PythonServer
import sqlite3
import Common.mysql_helpers as mysql_helpers
from Common.Globals import Global
from Common.Globals import GlobalConfig as Config
import os, os.path
import re  # regex
import random
import Common.DEBUG as DEBUG

class sql_query():

    def __init__(self, db_name, using_mysql=False):

        self.available = True

        self.using_mysql = using_mysql
        self.db_name = db_name

        # make sure that the db root is set
        if not Config.is_set( "db_root" ):
            Config.set("db_root", "")

        # if using MYSQL make sure that the user has set a host, username and password!
        if self.using_mysql:
            if not Config.is_set( "mysql_host"):
                Config.set("mysql_host", "localhost")

            if not Config.is_set( "mysql_user" ):
                Config.set("mysql_user", "root")

            if not Config.is_set( "mysql_pass" ):
                Config.set("mysql_pass", "")  # please set a password in some other file (that is not synced with public version control)

            DEBUG.LOGS.print( "mysql details:", Config.get("mysql_host"), Config.get("mysql_user"), "*" * random.randint( 6, 16 ), db_name )

        connection, cursor = self.connect_db()
        self.close_db(connection, cursor, commit=False)

    def test_connection( self ):

        if not self.using_mysql:
            DEBUG.LOGS.print("No support to test sqlite connection, use database exist instead", message_type=DEBUG.LOGS.MSG_TYPE_WARNING)
            return

        connection = mysql_helpers.MySqlHelpers._connect( Config.get( "mysql_host" ),
                                                          Config.get( "mysql_user" ),
                                                          Config.get( "mysql_pass" ) )[0]

        if connection is not None:
            connection.close()
            return True

        return False

    def connect_db(self):
        """ Connect to the SQLite DB, creates new if not exist
            :returns:  tuple (connection, cursor)
        """

        if self.using_mysql:
            connection, cursor = mysql_helpers.MySqlHelpers.mysql_connect(
                                                                                    Config.get("mysql_host"),
                                                                                    Config.get("mysql_user"),
                                                                                    Config.get("mysql_pass"),
                                                                                    self.db_name )
        else:
            connection = sqlite3.connect( Config.get("db_root")+self.db_name )
            cursor = connection.cursor()

        return connection, cursor

    def destroy_database(self):

        if not self.using_mysql:
            if os.path.exists( Config.get("db_root")+self.db_name ):
                os.remove( Config.get("db_root")+self.db_name )
        else:
            mysql_helpers.MySqlHelpers.mysql_destroy_database( Config.get("mysql_host"),
                                                               Config.get("mysql_user"),
                                                               Config.get("mysql_pass"),
                                                               self.db_name )

    def close_db(self, connection, cursor, commit=True):
        """Closes the db connection"""

        # check that the connection exists
        if connection is None and cursor is None:
            return

        # if not self.using_mysql and commit:
        if commit:
            connection.commit()

        # in mysql we must close the cursor and connection
        if self.using_mysql:
            cursor.close()

        connection.close()

        # necessary??
        del connection
        del cursor

    def get_all_tables(self, close_conn=True):
        """ Gets an list of tuples with all table names in database

        :return: list of table names [table_name, ...]
        """
        if self.using_mysql:
            query = "SHOW TABLES"
        else:
            query = "SELECT name FROM sqlite_master WHERE type='table'"

        data = self.execute(query, [], fetch=True, close_conn=close_conn)

        # get only the table names
        data = [ r[0] for r in data ]

        return data

    def get_table_columns(self, table_name):
        """ Gets a list of tuples with all column data for table

        :param table_name:  table to get column data from
        :return:            (sqlite) [(col_id, col_name, type, can_be_null, default_value, part_of_primary_key)...]
                            (mysql) [(type, null, key, default, extra)...]
        """

        table_name = re.sub("\s", "_", table_name ) # replace white space with underscores

        if self.using_mysql:
            query = "DESCRIBE "+table_name
        else:
            query = "pragma table_info("+table_name+")"

        try:
            data = self.execute( query, [], fetch=True )
        except Exception as e:
            DEBUG.LOGS.print(e, message_type=DEBUG.LOGS.MSG_TYPE_ERROR)
            data = []

        return data

    def get_table_column_names(self, table_name):
        """ Gets a list of all column names (in order)"""

        table_name = re.sub("\s", "_", table_name)  # replace white space with underscores

        if self.using_mysql:
            return [u[0] for u in self.get_table_columns(table_name)]
        else:
            return [u[1] for u in self.get_table_columns(table_name)]

    def table_exist(self, table_name, close_connect = True):
        """Check if table exist in database"""

        tables = self.get_all_tables()

        return table_name in tables

    ''' Check if table exist else creats it.
    @:param table_name: Name of the table to be created.
    @:param col_names: col string
    '''
    def add_table(self, table_name, col_names, data_types, data_lengths=None, default_values=None):
        """Adds new table to database

        :param col_names:       List of column names
        :param data_types:      list of data types (must match col names or none)
        :param data_lengths:    list of max column length (must match col names or none)
        :param default_values:  list of default values for column (must match col names or none)
        """

        table_name = re.sub("\s", "_", table_name)  # replace white space with underscores

        if self.table_exist( table_name ):
            DEBUG.LOGS.print("can not create table(", table_name, "), already exist",
                              message_type=DEBUG.LOGS.MSG_TYPE_WARNING)
            return 404, "table already exist"

        query = "CREATE TABLE "+table_name
        columns = []

        for i, v in enumerate(col_names):
            data_l = ""
            default_v = ""

            if data_lengths is not None and data_lengths[i] != "":
                data_l = "("+data_lengths[i]+")"

            if default_values is not None and default_values[i] != "":
                if self.using_mysql:
                    default_v = '"'+default_values[i]+'"'
                else:
                    default_v = ' DEFAULT "'+default_values[i]+'"'

            v = re.sub("\s", "_", v )  # replace white space with underscores

            # make sure the first character is not a number
            failed = False
            try:
                int(v[0])
            except: # add underscore at start if it does
                failed = True

            if not failed:
                v = "_"+v

            columns.append( v +" "+ data_types[i] + data_l + default_v )

        columns = ', '.join(columns)

        query += " ("+columns+")"

        self.execute(query, [])

        if DEBUG.LOGS.debug_sql:
            DEBUG.LOGS.print("SQL Query", query)

        return None, None

    def drop_table(self, table_name):
        """drops table from database"""
        if not self.table_exist( table_name ):
            DEBUG.LOGS.print("can not drop", table_name,"table, does not already exist",
                              message_type=DEBUG.LOGS.MSG_TYPE_WARNING)
            return

        query = "DROP TABLE " + table_name
        self.execute(query, [])

        DEBUG.LOGS.print(table_name, "Droped")

    def insert_row(self, table_name, value_columns, value_data):
        """Inserts rot into table"""
        if not self.table_exist(table_name):
            DEBUG.LOGS.print("Error: can not insert row into table, table does not exist",
                              message_type=DEBUG.LOGS.MSG_TYPE_ERROR)
            return

        if self.using_mysql:
            val_str = "%s"
        else:
            val_str = "?"

        col_name_str = ', '.join(value_columns)
        col_value_str = ', '.join([val_str] * len(value_data))

        query = "INSERT INTO " + table_name + " (" + col_name_str + ") VALUES (" + col_value_str + ") "

        if DEBUG.LOGS.debug_sql:
            DEBUG.LOGS.print("query: ", query, "Data", value_data)

        self.execute(query, value_data)

    def insert_rows(self, table_name, value_columns, value_data):
        """Inserts rots into table
        :param table_name:  name of table to insert data into
        :param value_columns: List of columns
        :param value_data:  list of list [[v1 col1, v1 col2...], [v2 col1, v2 col2...], ...]
        """
        if not self.table_exist(table_name):
            DEBUG.LOGS.print("Error: can not insert row into table, table does not exist",
                              message_type=DEBUG.LOGS.MSG_TYPE_ERROR)
            return

        if self.using_mysql:
            val_str = "%s"
        else:
            val_str = "?"

        val_len = len(value_columns)

        for val in value_data:
            col_name_str = ', '.join(value_columns)
            col_value_str = ', '.join([val_str] * val_len)

            query = "INSERT INTO " + table_name + " (" + col_name_str + ") VALUES (" + col_value_str + ") "
            if DEBUG.LOGS.debug_sql:
                DEBUG.LOGS.print(query, val)

            if Global.DEBUG:
                DEBUG.LOGS.print("query: ", query, "Data", val)

            self.execute(query, val)

    def remove_row(self, table_name, where_columns, where_data):
        """remove row from table"""
        if not self.table_exist(table_name):
            DEBUG.LOGS.print("Error: can not delete row from table, table does not exist")
            return

        where_str = self.sql_string_builder( where_columns, "AND " )

        query = " DELETE FROM "+table_name+" WHERE "+where_str

        if DEBUG.LOGS.debug_sql:
            DEBUG.LOGS.print(query, where_data)

        self.execute( query, where_data )

    def select_from_table(self, table_name, column_names, where_columns=[], where_data=[], order_data={}, override_where_cols = False):
        """ Selects rows of data from table

        :param table_name:          Name of table to select data from
        :param column_names:        list of column names to get data rom (* = all)
        :param where_columns:       list of where column names
        :param where_data:          list of where data (must match where column order)
        :param order_data:          dict of order data keys {"order_columns": list of strings, "sort_type": string (ASC || DESC)}
        :param override_where_cols: By default (False) where columns use '=' to compare, if another id need set to True to manuly add them.
                                    It must be done for all columns include '='
        :return:
        """
        if not self.table_exist(table_name):
            DEBUG.LOGS.print( "Error: can not select from table, table does not exist",
                              message_type=DEBUG.LOGS.MSG_TYPE_ERROR)
            return []

        # turn the lists of column names into a usable sql string
        col_str = self.sql_string_builder( column_names, ",", False )
        where_str = self.sql_string_builder(where_columns, "AND ", not override_where_cols, True )

        # create the where string
        if len(where_columns) > 0:
            where_str = " WHERE "+where_str
        else:
            where_str = ""

        # create the order by string
        if order_data is not None and "order_columns" in order_data and \
                "sort_type" in order_data and type(order_data["order_columns"] is list):
            order_str = ', '.join(order_data["order_columns"])
            order_str = "ORDER BY " + order_str + " " + order_data["sort_type"]
        else:
            order_str = ""

        query = "SELECT " + col_str + " FROM " + table_name + where_str + order_str

        if DEBUG.LOGS.debug_sql:
            DEBUG.LOGS.print (query)

        return self.execute( query, where_data, fetch=True )

    def update_row(self, table_name, set_columns, set_data, where_columns, where_data ):
        """ Updates table row

        :param table_name:      Name of table to update
        :param set_columns:     list or tuple of columns to set
        :param set_data:        list or tuple of data to set into columns (order must match set_str)
        :param where_columns:   list or tuple of wheres
        :param where_data:      list or tuple of where data (order must match where_str)
        :return:
        """
        if not self.table_exist(table_name):
            DEBUG.LOGS.print("can not update row in table, table does not exist",
                              message_type=DEBUG.LOGS.MSG_TYPE_ERROR)
            return

        set_str = self.sql_string_builder(set_columns, ",")
        where_str = self.sql_string_builder(where_columns, "AND ")
        data = (*set_data, *where_data)

        query = "UPDATE "+table_name+" SET "+set_str+" WHERE "+where_str

        if DEBUG.LOGS.debug_sql:
            DEBUG.LOGS.print( query, data )

        self.execute(query, data)

    def sql_string_builder(self, column_names, join, add_equals=True, add_value=False):
        """ build a list of column names in to sql query string for set and where ect...
         if add equals is true then add_value is ignored.

         """

        if self.using_mysql:
            str_val = "%s"
        else:
            str_val = "?"

        string = ""
        if add_equals is True:
            equals = "={0} ".format(str_val)
        elif add_value:
            equals = str_val
        else:
            equals = " "

        # make column string
        for s in column_names:
            string += s + equals + join

        # clear end ','
        if string[-len(join):] == join:
            string = string[:-len(join)]

        return string

    def execute( self, query, where_data, fetch=False, close_conn=True ):

        data = None

        try:
            connection, cursor = self.connect_db()

            if connection is None or cursor is None:
                DEBUG.LOGS.print( "Invalid connection or cursor", message_type=DEBUG.LOGS.MSG_TYPE_ERROR )
                return None

            cursor.execute( query, where_data )
            if fetch:
                # DEBUG.LOGS.print("Fetching.........................", query)
                data = cursor.fetchall()

            if close_conn:
                self.close_db( connection, cursor)
        except Exception as e:
            DEBUG.LOGS.print("Bad SQL", e, message_type=DEBUG.LOGS.MSG_TYPE_ERROR)
            return None

        return data
