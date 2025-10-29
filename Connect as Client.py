from geoscada.client import ConnectionManager

with ConnectionManager('localhost', 5481, 'ConnectionManager example') as connection:
    #Log on
    #user = input('Enter Geo SCADA Username: ')
    #We suggest using the pwinput module to hide the password
    #passw = input('Enter Geo SCADA Password: ')
    user, passw = '', ''
    connection.log_on(user, passw)
    status = connection.get_object_status(0)

    for OSD in status:
        print(f'{OSD.name}: {OSD.value.get_value_as_string()}')
