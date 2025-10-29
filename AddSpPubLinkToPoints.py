# Example: Link points to a Sparkplug Publisher
from geoscada.client import ConnectionManager
from geoscada.lib.variant import *
from geoscada.client.types import QueryStatus
from geoscada.client.interface_scx import InterfaceScx
from typing import Optional
import sys

# Import a linked library
from GSConfigFunc import *

###################################################################################################
#      This program shows how to query the database and then modify selected configuration
#
# It will find points in Example Projects and add a historic export link to the Sp Publisher.
###################################################################################################


with ConnectionManager('localhost', 5481, 'ConnectionManager example') \
     as connection:
    #Log on
    #user = input('Enter Geo SCADA Username: ')
    #We suggest using the pwinput module to hide the password
    #passw = input('Enter Geo SCADA Password: ')
    user, passw = '', ''
    connection.log_on(user, passw)

    # Query all objects with historic data
    q = connection.prepare_query("SELECT WITH TEMPLATES H.ID, P.FULLNAME, H.HISTORICEXPORTIDS FROM CHISTORY AS H LEFT JOIN CDBOBJECT AS P USING ( ID ) WHERE P.FULLNAME LIKE 'Example Projects.%'", False)
    result = q.execute_sync()
    print(result.status == QueryStatus.Succeeded, file=sys.stderr)
    if result.status == QueryStatus.Succeeded:
        print(result.rows_affected, file=sys.stderr)

    # Get the export object
    exportobj = connection.find_object( "Sp Publisher.Sparkplug Publisher")
    exportid = exportobj.id
    
    for queryrow in result.rows:
        id = queryrow.data[0].value
        # Get current export ids
        exportidsvar = connection.get_property( id, "Historic.HistoricExportIDs")
        # Does it contain ours?
        if ( exportid not in [int(id) for id in exportidsvar.value]):
            exportidsvar.value.append( exportid)
            # If creating the variant: = Variant(CombinedVariantType(VariantType.I4, VariantFlags.Array), exportids)
            try:
                connection.set_property( id, "Historic.HistoricExportIDs", exportidsvar)
                print(f"OK {queryrow.data[1].value}", file=sys.stderr)
            except Exception as e:
                print(f"Fail {queryrow.data[1].value} {e.args[0]}", file=sys.stderr)

