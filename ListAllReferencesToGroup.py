# List references into a group - will help you understand the consequences of moving it.
from geoscada.client import ConnectionManager
from geoscada.lib.variant import *
from geoscada.client.types import HistoricTag, ExtendedSourceFilter
from datetime import datetime, timedelta
import sys

def GetRefs( MyObject, GroupName):
    c = 0
    # List references here
    ReferencedObjects = connection.get_references_to(MyObject.id)
    # for all referenced
    for RefObj in ReferencedObjects:
        # if the path lies outside our group
        if (not RefObj.full_name.startswith( GroupName + ".")):
            print( "Object: ", MyObject.full_name, "(" + MyObject.class_name +")")
            print( "  Reference: ", RefObj.full_name, "("+RefObj.class_name +")")
            c += 1
    return c

def ListReferences( GroupToRef, GroupName):
    c = 0
    # Get all child members of the root
    Children = connection.list_objects( "", "", GroupToRef.id, True)

    # get all children
    for ChildObj in Children:
        c += GetRefs( ChildObj, GroupName)
        # recurse down groups
        if (ChildObj.class_name == "CGroup"):
            c += ListReferences(ChildObj, GroupName)
    return c

with ConnectionManager('localhost', 5481, 'ConnectionManager example') \
     as connection:
    #Log on
    #user = input('Enter Geo SCADA Username: ')
    #We suggest using the pwinput module to hide the password
    #passw = input('Enter Geo SCADA Password: ')
    user, passw = '', ''
    connection.log_on(user, passw)

    #Type the group to be reference-checked here
    #We also prompt user for this
    GroupName = "Presentation"

    e = input( "Enter group for reference check [" + GroupName + "]: ")
    if (e != ""):
        GroupName = e

    GroupToRef = connection.find_object(GroupName )
    c = ListReferences( GroupToRef, GroupName )
    print( "Found: " + str(c) + " references.")
