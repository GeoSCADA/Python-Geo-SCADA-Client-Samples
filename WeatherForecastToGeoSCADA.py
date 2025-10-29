from geoscada.client import ConnectionManager
from geoscada.lib.variant import *
from geoscada.client.types import HistoricTag, ExtendedSourceFilter
from datetime import datetime, timedelta

import sys
with ConnectionManager('localhost', 5481, 'ConnectionManager example') \
     as connection:
    #Log on
    #user = input('Enter Geo SCADA Username: ')
    #We suggest installing the pwinput module to hide the password
    #passw = input('Enter Geo SCADA Password: ')
    user, passw = '', ''
    connection.log_on(user, passw)
    
    # This is the location of SE offices in Coventry, UK
    latitude, longitude = 52.388578, -1.557237
    
    #############################################################
    # SETUP SECTION - CREATE GROUP, POINT AND FORECAST
    #############################################################

    #Find and create a group    
    R = connection.find_object('Python Samples.WeatherPoints')
    if (R == None):
        print('Creating group')
        try:
            PS = connection.find_object('Python Samples')
            connection.create_object( "CGroup", PS.id, "WeatherPoints")
        except Exception as e:
            print("Can't create group " + str(e) )
            quit
    R = connection.find_object('Python Samples.WeatherPoints')
    print( "Group id: " + str(R.id) + " name: " + R.name + ", " + R.class_name)

    #Find and create a point
    P = connection.find_object('Python Samples.WeatherPoints.Temperature')
    if (P == None):
        print('Creating point')
        try:
            connection.create_object( "CPointAlgManual", R.id, "Temperature")
        except Exception as e:
            print("Can't create point " + str(e) )
            quit
    P = connection.find_object('Python Samples.WeatherPoints.Temperature')
    print( "Point id: " + str(P.id) + " name: " + P.name + ", " + P.class_name)

    #Set point properties
    #Requires from geoscada.lib.variant import Variant, VariantType
    connection.set_properties( P.id, [
            ("Units", Variant(VariantType.BStr, "degC")),
            ("FullScale", Variant(VariantType.R8, 60.0)),
            ("ZeroScale", Variant(VariantType.R8, -20.0))
        ] )
    #Set historic aggregate
    H = connection.set_aggregate( P.id, "Historic", "CHistory")

    #Create Geo Location Aggregate Configuration
    G = connection.set_aggregate( P.id, "GISLocationSource", "CGISLocationSrcStatic")
    #print( "Aggregate: " + connection.get_property( P.id, "GISLocationSource.AggrName").value )
    #print( G)
    #Set Geo location
    connection.set_properties( P.id, [
            ("GISLocationSource.Latitude", Variant(VariantType.R8, latitude)),
            ("GISLocationSource.Longitude", Variant(VariantType.R8, longitude))
        ] )

    # Create a Geo SCADA Forecast Item
    F = connection.find_object('Python Samples.WeatherPoints.TempForecast')
    if (F == None):
        print('Creating forecast')
        try:
            connection.create_object( "CForecast", R.id, "TempForecast")
        except Exception as e:
            print("Can't create forecast " + str(e) )
            quit
    F = connection.find_object('Python Samples.WeatherPoints.TempForecast')
    print( "Forecast id: " + str(F.id) + " name: " + F.name + ", " + F.class_name)
    #Set forecast properties
    #Requires from geoscada.lib.variant import Variant, VariantType
    connection.set_properties( F.id, [
            ("Units", Variant(VariantType.BStr, "degC")),
            ("TrendInterval", Variant(VariantType.BStr, "7 Days")),
            ("TrendMaximum", Variant(VariantType.R8, 60.0)),
            ("TrendMinimum", Variant(VariantType.R8, -20.0))
        ] )
    #Defaults to 8 forecasts and 15 minute period

    #############################################################
    # RUN SECTION - READ FROM WEB WEATHER AND WRITE TO GEO SCADA
    #############################################################

    # Web request library - needs "pip install requests"
    import requests

    # Get the key by registering at openweathermap.org
    API_key = "" #"your openweathermap key"

    # Make the web requests
    current_base_url = "http://api.openweathermap.org/data/2.5/weather?"
    Final_url = current_base_url + "appid=" + API_key + "&lat=" + str(latitude) + "&lon=" + str(longitude)
    current_weather_data = requests.get(Final_url).json()
    forecast_base_url = "http://api.openweathermap.org/data/2.5/forecast?"
    Final_url = forecast_base_url + "appid=" + API_key + "&lat=" + str(latitude) + "&lon=" + str(longitude)
    forecast_weather_data = requests.get(Final_url).json()

    # Print out when testing
    #print(current_weather_data)
    # Get just one parameter, convert K to C
    temperature = current_weather_data["main"]["temp"] - 273.15
    print(f"Temperature now: {temperature}")

    #Set point value
    P = connection.find_object('Python Samples.WeatherPoints.Temperature')
    connection.invoke_method( P.id, "CurrentValue", [Variant(VariantType.R8, temperature)] )

    # Print out when testing
    #print(forecast_weather_data)
    
    #Get forecast data - hourly and daily
    hourlydata = forecast_weather_data["list"]
    fcfirsttime = hourlydata[0]["dt"]
    fclasttime = fcfirsttime
    fcvalues = []
    fctimes = []
    fcqualities = []
    for i in hourlydata:
        print ("Data: ", i["dt"], i["main"]["temp"]-273.15  )
        fclasttime = i["dt"]
        fcvalues.append( float( i["main"]["temp"]-273.15 ) )
        fctimes.append( datetime.fromtimestamp(fclasttime) )
        fcqualities.append( 192)
    print(f"Forecast from: {datetime.fromtimestamp(fclasttime)} to {datetime.fromtimestamp(fcfirsttime)}")
    #Load forecast data
    F = connection.find_object('Python Samples.WeatherPoints.TempForecast')

    #Set ForecastEx...	Insert a new set of fixed-interval forecast data into the forecast object.
    #Args: Name, Array of Time, Array of Values, Array of Qualities
    shorttime = datetime.now().strftime("%d-%b %H:%M") #Time of getting the forecast
    arguments = [ Variant(VariantType.BStr, "OpenWeather Forecast "+shorttime),
                  Variant(CombinedVariantType( VariantType.Date, VariantFlags.Array), fctimes),
                  Variant(CombinedVariantType( VariantType.R8, VariantFlags.Array), fcvalues),
                  Variant(CombinedVariantType( VariantType.I4, VariantFlags.Array), fcqualities) ]
    connection.invoke_method( F.id, "SetForecastEx", arguments)

    #Done.
