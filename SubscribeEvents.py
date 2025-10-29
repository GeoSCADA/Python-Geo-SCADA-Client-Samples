import threading

from geoscada.lib.variant import Variant, VariantType

from geoscada.client import ConnectionManager
from geoscada.client.event_args import EventsUpdatedEventArgs
from geoscada.client.event_code import EventCode

# Edit in some credentials
username = ''
password = ''
# Specify the point you want to watch, by Id
point_id = 1561
new_value = 2.0

obj_details = None

event_received = threading.Event()


def on_event_received(event_code: EventCode, args: EventsUpdatedEventArgs):
    print("Event received")
    for update in args.updates:
        print(update.source," -", update.message)

        #if update.source == obj_details.full_name:
            #event_received.set()


with ConnectionManager('localhost', 5481, 'Example Python client') as connection:
    if username != '':
        connection.log_on(username, password)

    obj_details = connection.lookup_object(point_id)
    connection.set_event_handler(EventCode.EventsChanged, on_event_received)

    connection.add_event_subscription('EventsExample', '', [])

    try:
        connection.set_property(point_id, 'CurrentValue', Variant(VariantType.R8, new_value))
        event_received.wait(25)
    finally:
        connection.remove_event_subscription('EventsExample')
