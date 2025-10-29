import os
import traceback
import datetime
import math
import time

from geoscada.client import ConnectionManager
from geoscada.base.gs_logging import LogLevel
from geoscada.lib.variant import Variant, VariantType

def CreateTree(connection):
    folder = connection.find_object("SQL_DATA_TABLES.TestTables")
    if folder is None:
        SQL_DATA_Tables  = connection.create_object("CGroup",             0,                  "SQL_DATA_TABLES")
        TestTables       = connection.create_object("CGroup",             SQL_DATA_Tables.id, "TestTables"     )    
    folder = connection.find_object("SQL_DATA_TABLES")

    table = connection.create_object("CDataTable", folder.id, "MainTable")

    connection.set_property(table.id, "TableName", Variant(var_type = VariantType.BStr, value = "MainTable"))
    connection.set_property(table.id, "Title", Variant(var_type = VariantType.BStr, value ="MainTable"))    

    # Add time field
    connection.invoke_method(table.id, "AddField", [Variant(VariantType.BStr, "TimeStamp"), Variant(VariantType.I4, 2)])
    # Add string field
    connection.invoke_method(table.id, "AddField", [Variant(VariantType.BStr, "TestName"), Variant(VariantType.I4, 6)])
    # Set its length
    connection.invoke_method(table.id, "SetFieldSize", [Variant(VariantType.BStr, "TestName"), Variant(VariantType.I4, 16)])
    return

def CreateTable(connection, table_path, table_name, columns):
    table = connection.find_object(f"{table_path}.{table_name}")
    if table is None:
        folder = connection.find_object(table_path)
        table = connection.create_object("CDataTable", folder.id, table_name)
        #Create Fields (Columns)
        #0=byte, 1=word, 2=long, 3=float, 4=double, 5=reference, 6=string, 7=Boolean, 9=time, 10=color, 12=unsigned word, 13=unsigned long, 15=long long, 16=unsigned long long
        for col_name, col_type_code in columns:
            connection.invoke_method(table.id, "AddField", [Variant(VariantType.BStr, col_name), Variant(VariantType.I4, col_type_code)])
    #Assign ".TableName"   and ".Title"
    connection.set_property(table.id, "TableName", Variant(var_type = VariantType.BStr, value = table_name))
    connection.set_property(table.id, "Title", Variant(var_type = VariantType.BStr, value =table_name))
    return

SERVER_ADDRESS = "127.0.0.1"
SERVER_PORT = 5481
CLIENT_NAME = 'Python Automation Test' 
USERNAME = ""
PASSWORD = ""

# Main function uses ConnectionManager
if __name__ == "__main__":
    print(f"Connecting to GeoSCADA Server at {SERVER_ADDRESS}:{SERVER_PORT}...")
    try:
        with ConnectionManager(SERVER_ADDRESS, SERVER_PORT, CLIENT_NAME) as connection:
            print("Connection successful. Logging on...")
            connection.log_on(USERNAME, PASSWORD) # Log on using credentials
            
            CreateTree(connection)
            CreateTable(connection, "SQL_DATA_TABLES.TestTables", "Table_9",[
                                                                            ("TimeStamp"   , 2),    # Long
                                                                            ("ResultCode"  , 2),    # Long
                                                                            ("EdgeBootTime", 3)     # Float
                                                                        ])
        print("Disconnected from GeoSCADA server.")

    except Exception as e:
        print(f"\n*** An error occurred: {e} ***")
        traceback.print_exc()
        print(f"--- Script Finished with Errors ---")

