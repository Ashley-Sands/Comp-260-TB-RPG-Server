from HTTP_Analytics.requestServers import server_request
import Common.sql_query as sql

class TEST_mysql( server_request.ServerRequest  ):

    def __init__( self ):

        # connect to data
        self.database = sql.sql_query("py_test", using_mysql=True)
        self.litedb = sql.sql_query("pytest")

        #self.database.connect_db()

        tables = self.database.get_all_tables()
        cols = self.database.get_table_columns("test")
        cols_names = self.database.get_table_column_names("test")
        table_exist = self.database.table_exist("test")
        table_not_exist = self.database.table_exist("test__")

        self.database.add_table("test_add_table", ["col_1", "col_2"], ["INT UNSIGNED NULL AUTO_INCREMENT KEY", "INT NOT NULL"])
        self.database.insert_row("test_add_table", ["col_1", "col_2"], ["NULL", 5432])
        self.database.insert_row("test_add_table", ["col_1", "col_2"], ["NULL", 5433])
        self.database.insert_row("test_add_table", ["col_1", "col_2"], ["NULL", 5434])
        self.database.remove_row("test_add_table", ["col_2"], [5432])
        table_Select = self.database.select_from_table("test_add_table", ["*"], ["col_2"], [5433])
        self.database.update_row("test_add_table", ["col_2"], [33], ["col_2"], [5434])
        table_Select_2 = self.database.select_from_table("test_add_table", ["*"], ["col_2"], [33])

        #self.database.drop_table("test_add_table")

        '''
        self.litedb.add_table("test_lite", ["a", "b"], ["INT", "INT"])
        self.litedb.add_table("test_lite2", ["a", "b"], ["INT", "INT"])

        tables_lite = self.litedb.get_all_tables()
        cols_lite = self.litedb.get_table_columns("test_lite")
        cols_names_lite = self.litedb.get_table_column_names("test_lite")
        table_exist_l = self.litedb.table_exist("test_lite")
        table_not_exist_l = self.litedb.table_exist("test__")
        self.litedb.add_table("test_add_table", ["col_1", "col_2"], ["INT", "INT"])
        self.litedb.drop_table("test_add_table")
        '''
        # destroy and close
        #self.database.destroy_database()
        #self.database.close_db()

        print(tables, cols, cols_names,  table_exist, table_not_exist)
        print(table_Select)
        print(table_Select_2)
        #print("lite:", tables_lite, cols_lite, cols_names_lite, table_exist_l, table_not_exist_l)
