# List the access control list attributes set at each group

from geoscada.client import ConnectionManager
from geoscada.lib.variant import *
from geoscada.client.types import HistoricTag, ExtendedSourceFilter
from datetime import datetime, timedelta
import sys

# Functions to iterate over all groups and return permissions applied
# Note that for a large database this can take a long time to run and
# could affect other operations.

def ListACLs( DBObjid, name):
    inheritedV = connection.get_property(DBObjid, "ACLInherited")
    if (inheritedV.value == False):
        ACL = connection.get_security(DBObjid)
        print( "Object", name)
        print( "    ACL", len(ACL), "entries")
        for acl in ACL:
            print( "        User:", acl.user_name, ", ", acl.permissions),
        return len(ACL)
    else:
        return 0

def RecurseACLs( groupid):
    c = 0
    # Get all child members of the root
    Children = connection.list_objects( "", "", groupid, True)

    # get all children
    for ChildObj in Children:
        c += ListACLs( ChildObj.id, ChildObj.full_name)
        # recurse down groups
        ##print(f"{ChildObj.full_name} <{ChildObj.class_name}>")
        if (ChildObj.class_name == "CGroup"):
            c += RecurseACLs(ChildObj.id)
    return c

with ConnectionManager('localhost', 5481, 'ConnectionManager example') \
     as connection:
    #Log on
    #user = input('Enter Geo SCADA Username: ')
    #We suggest using the pwinput module to hide the password
    #passw = input('Enter Geo SCADA Password: ')
    user, passw = '', ''
    connection.log_on(user, passw)
    R = connection.find_object("$Root")
    c = ListACLs( R.id, R.name)
    c += RecurseACLs( R.id)
    print( "Found: " + str(c) + " ACLs.")
