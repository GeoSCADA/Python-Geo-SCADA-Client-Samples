###########################################################################
# SIMPLE CONFIGURATION UTILITY FUNCTIONS
# YOU CAN USE THESE DIRECTLY, AND FUTURE FUNCTIONS MAY BE ADDED HERE
###########################################################################

from geoscada.client import ConnectionManager
from geoscada.lib.variant import Variant, VariantType
from geoscada.client.types import HistoricTag
from datetime import datetime, timedelta
import sys

# Create an object of the specified type
def gs_create_object( connection, parentname, objectname, objecttype):
    # Find parent and create an object
    if (parentname == '' or parentname == '$Root'):
        parentid = 0
        fullname = objectname
    else:
        P = connection.find_object( parentname)
        parentid = P.id
        fullname = parentname + '.' + objectname
    G = connection.find_object( fullname)
    if (G == None):
        try:
            connection.create_object( objecttype, parentid, objectname)
        except Exception as e:
            print(f"Can't create {objecttype} {fullname} {str(e)}", file=sys.stderr)
            return None
        G = connection.find_object(fullname)
    return G


# Create a group
def gs_create_group( connection, parentname, groupname):
    return gs_create_object( connection, parentname, groupname, "CGroup" )


# Instance a template
def gs_instance_template( connection, instancepath, instancename, templatepath):
    # Find template
    T = connection.find_object( templatepath)
    if (T == None):
        print(f"Can't find instance {templatepath} {str(e)}", file=sys.stderr)
        return None

    # Find parent
    if (parentname == '' or parentname == '$Root'):
        parentid = 0
        fullname = objectname
    else:
        P = connection.find_object( parentname)
        parentid = P.id
        fullname = parentname + '.' + objectname
    G = connection.find_object( fullname)
    if (G == None):
        try:
            connection.create_instance( T.id, parentid, instancename)
        except Exception as e:
            print(f"Can't create instance {fullname} {str(e)}", file=sys.stderr)
            return None
        G = connection.find_object(fullname)
    return G


# Set a property of an object
def gs_update_object( connection, objectpath, objectname, propertyname, propertyvalue):
    # Find parent
    if (parentname == '' or parentname == '$Root'):
        fullname = objectname
    else:
        fullname = parentname + '.' + objectname
    G = connection.find_object( fullname)
    if (G == None):
        print(f"Can't find {fullname} {str(e)}", file=sys.stderr)
        return None
    try:
        # This is limited at present - needs expanding, possibly into its own function
        t = type(propertyvalue)
        if t == "str":
            vt = VariantType.BStr
        elif t == "float":
            vt = VariantType.R8
        elif t == "int":
            vt = VariantType.I4
        else:
            vt = VariantType.FileTime

        # Does not as yet resolve a string into a reference
        connection.set_properties( G.id, [ (propertyname, Variant( vt, propertyvalue)) ])
    except Exception as e:
        print(f"Can't set {propertyvalue} property of {fullname}" + str(e), file=sys.stderr)


# Copy an object
def gs_copy_object( connection, parentname, objectname, sourcefullname):
    # Find source
    S = connection.find_object( sourcefullname)
    if (S == None):
        print(f"Can't find instance {templatepath} {str(e)}", file=sys.stderr)
        return None

    # Find parent and create an object
    if (parentname == '' or parentname == '$Root'):
        parentid = 0
        fullname = objectname
    else:
        P = connection.find_object( parentname)
        parentid = P.id
        fullname = parentname + '.' + objectname
    G = connection.find_object( fullname)
    if (G == None):
        try:
            connection.copy_object( S.id, parentid, objectname)
        except Exception as e:
            print(f"Can't copy {objecttype} " + fullname + " " + str(e), file=sys.stderr)
            return None
        G = connection.find_object(fullname)
    return G


# Set the fixed location of an object
def gs_set_static_location( connection, full_name, lat, long):
    O = connection.find_object( full_name)
    # Set Geo Location Aggregate Configuration
    A = connection.set_aggregate( O.id, "GISLocationSource", "CGISLocationSrcStatic")
    # Set Geo location
    connection.set_properties( O.id, [
            ("GISLocationSource.Latitude", Variant(VariantType.R8, lat)),
            ("GISLocationSource.Longitude", Variant(VariantType.R8, long))
        ] )


# Deletes the named item. Returns a list of error messages if error, True if success and False if not found
def gs_delete_object( connection, full_name):
	O = connection.find_object( full_name)
	if (O != None):
		force = True
		result = connection.delete_object(O.id, force)
		if (len(result) > 0):
			return False # Error condition
		else:
			return True
	else:
		return False
