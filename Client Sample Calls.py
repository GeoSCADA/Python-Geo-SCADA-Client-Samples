from geoscada.client import ConnectionManager
from geoscada.lib.variant import *
from geoscada.client.types import HistoricTag, ExtendedSourceFilter
from datetime import datetime, timedelta
import sys
   
with ConnectionManager('localhost', 5481, 'ConnectionManager example') \
     as connection:
    #Log on
    #user = input('Enter Geo SCADA Username: ')
    #We suggest using the pwinput module to hide the password
    #passw = input('Enter Geo SCADA Password: ')
    user, passw = '', ''
    connection.log_on(user, passw)

    #Root group status
    status = connection.get_object_status(0)
    for stat in status:
        print(f'{stat.name}: {stat.value.get_value_as_string()}')

    #Find and create a group    
    R = connection.find_object('WeatherPoints')
    if (R == None):
        print('Creating group')
        try:
            connection.create_object( "CGroup", 0, "WeatherPoints")
        except Exception as e:
            print("Can't create group " + str(e) )
            quit
    R = connection.find_object('WeatherPoints')
    print( "Group id: " + str(R.id) + " name: " + R.name + ", " + R.class_name)

    #Find and create a point
    P = connection.find_object('WeatherPoints.Temperature')
    if (P == None):
        print('Creating point')
        try:
            connection.create_object( "CPointAlgManual", R.id, "Temperature")
        except Exception as e:
            print("Can't create point " + str(e) )
            quit
    P = connection.find_object('WeatherPoints.Temperature')
    print( "Point id: " + str(P.id) + " name: " + P.name + ", " + P.class_name)

    #Get the children in a group
    CH = connection.list_objects( "", "", R.id, False)
    for ch in CH:
        print( "Child of group: " + str(ch.name) )

    #Set point properties
    #Requires from geoscada.lib.variant import Variant, VariantType
    connection.set_properties( P.id, [
            ("Units", Variant(VariantType.BStr, "degC")),
            ("FullScale", Variant(VariantType.R8, 60.0)),
            ("ZeroScale", Variant(VariantType.R8, -20.0))
        ] )
    
    #Set historic aggregate
    H = connection.set_aggregate( P.id, "Historic", "CHistory")
    #print( H)
    #print( P)
    
    #Get historic aggregate property
    print( "Historic Compress:" + str( connection.get_property( P.id, "Historic.Compress").value) )

    #Create Geo Location Aggregate Configuration
    G = connection.set_aggregate( P.id, "GISLocationSource", "CGISLocationSrcStatic")
    print( "Aggregate: " + connection.get_property( P.id, "GISLocationSource.AggrName").value )
    print( G)
    #Set Geo location
    connection.set_properties( P.id, [
            ("GISLocationSource.Latitude", Variant(VariantType.R8, 30.0)),
            ("GISLocationSource.Longitude", Variant(VariantType.R8, 1.0))
        ] )

    #Set point value
    connection.invoke_method( P.id, "CurrentValue", [Variant(VariantType.R8, 27.2)] )

    #Alternative - Set value with preset point quality and time
    connection.set_properties( P.id, [
            ("PresetQuality", Variant(VariantType.I4, 88)),
            ("PresetTimestamp", Variant(VariantType.Date, datetime.now())),
            ("CurrentValue", Variant(VariantType.R8, 25.1))
        ] )

    #Get point value and time
    result = connection.get_properties( P.id, ["CurrentValue", "CurrentTime", "CurrentQuality"] )
    print( f"Values: {result[0].value}, {result[1].value}, {result[2].value}")

    result = connection.get_properties( P.id, ["GISLocationSource.Latitude",
                                               "GISLocationSource.Longitude"] )
    latitude, longitude = result[0].value, result[1].value
    print( f"Location: {latitude}, {longitude}")

    #Read history
    #Requires: from geoscada.client.types import * for this and other method calls
    tags = [HistoricTag( P.full_name + ".Historic",ExtendedSourceFilter.Raw,0,0) ]
    #requires from datetime import datetime, timedelta
    result = connection.read_raw_history( datetime.now() - timedelta(days=1),
                             datetime.now(),
                             100, True, tags)
    print( f"Raw History: {result[3][0].samples[0].timestamp} {result[3][0].samples[0].value.value}")
    print( f"Raw History: {result[3][0].samples[1].timestamp} {result[3][0].samples[1].value.value}")
    print( f"Raw History: {result[3][0].samples[2].timestamp} {result[3][0].samples[2].value.value}")
    
    arguments = [ Variant(VariantType.Date, datetime.now() - timedelta(hours=1)),
                  Variant(VariantType.Date, datetime.now() ),
                  Variant(VariantType.I4, 0),
                  Variant(VariantType.I4, 1000),
                  Variant(VariantType.Bool, True),
                  Variant(VariantType.BStr, "") ]
    vresult = connection.invoke_method( P.id, "Historic.RawValues", arguments )
    
    # Returns a variant which is an array of variant numbers
    print( vresult.value[0] ) # First
    print( [ x.value for x in vresult.value ]) # All values

    tresult = connection.invoke_method( P.id, "Historic.RawTimeStamps", arguments )
    
    # Returns a variant which is an array of datetime
    print( tresult) # All
    print( tresult.value[0] ) # First
    print( [ str(x) for x in tresult.value ] ) # All time values, converted to strings

    # Create a Geo SCADA Forecast Item
    #Find and create a point
    F = connection.find_object('WeatherPoints.TempForecast')
    if (F == None):
        print('Creating forecast')
        try:
            connection.create_object( "CForecast", R.id, "TempForecast")
        except Exception as e:
            print("Can't create forecast " + str(e) )
            quit
    F = connection.find_object('WeatherPoints.TempForecast')
    print( "Forecast id: " + str(F.id) + " name: " + F.name + ", " + F.class_name)
    #Set forecast properties
    #Requires from geoscada.lib.variant import Variant, VariantType
    connection.set_properties( F.id, [
            ("Units", Variant(VariantType.BStr, "degC")),
            ("TrendMaximum", Variant(VariantType.R8, 60.0)),
            ("TrendMinimum", Variant(VariantType.R8, -20.0))
        ] )
    #Defaults to 8 forecasts and 15 minute period

    #Load forecast data
    #Set Forecast...	Insert a new set of fixed-interval forecast data into the forecast object.
    #Args: Name, StartTime, Values
    shorttime = datetime.now().strftime("%d-%b %H:%M")
    arguments = [ Variant(VariantType.BStr, "FixedIntervalForecast "+shorttime),
                  Variant(VariantType.Date, datetime.now() ),
                  Variant(CombinedVariantType( VariantType.R8, VariantFlags.Array), [-10.0, 0.0, 10.0, 20.0]) ]
    connection.invoke_method( F.id, "SetForecast", arguments)

    #Load forecast data 2
    #Set ForecastEx...	Insert a new set of fixed-interval forecast data into the forecast object.
    #Args: Name, Array of Time, Array of Values, Array of Qualities
    arguments = [ Variant(VariantType.BStr, "VariableIntervalForecast "+shorttime),
                  Variant(CombinedVariantType( VariantType.Date, VariantFlags.Array),
                          [datetime.now(), datetime.now()+timedelta(minutes=15),
                           datetime.now()+timedelta(minutes=20),datetime.now()+timedelta(minutes=35)]),
                  Variant(CombinedVariantType( VariantType.R8, VariantFlags.Array), [-5.0, 0.0, 5.0, 15.0]),
                  Variant(CombinedVariantType( VariantType.I4, VariantFlags.Array), [192, 192, 192, 192]) ]
    connection.invoke_method( F.id, "SetForecastEx", arguments)



