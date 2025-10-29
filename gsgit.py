# Example showing how to export Geo SCADA configuration as JSON and store updates in GIT
import json
import datetime
import os.path

from geoscada.client import ConnectionManager, RequestError
from geoscada.comms.misc import ConnectFlags
from geoscada.lib.variant import Variant
from geoscada.client.types import PropertyType
from git import Repo

# Edit your path here
repo_location = r'C:\Dev\Python\GSGit\repo'

class GSEEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime.datetime):
            return o.isoformat()

        return super().default(o)

def get_properties(obj_id: int, class_name: str) -> list[tuple[str, list[tuple[str, Variant]]]]:
    metadata = interface.get_class(class_name)
    # Add filter to restrict to Configuration items only (PropertyType.Configuration = 0)

    property_names = [p.name for p in metadata.properties if p.is_writable and p.property_type == PropertyType.Configuration]
    #print( property_names)
    property_values = []
    while len(property_names) > 0 and len(property_values) == 0:
        try:
            property_values = interface.get_properties(obj_id, property_names)
        except RequestError as ex:
            if ex.exception_type == 'PropertyException':
                for n, v in ex.properties:
                    if n == 'PropertyName':
                        print("Not including property " + v.value)
                        property_names.remove(v.value)
                        break

    this_class = [(class_name, list(zip(property_names, property_values)))]

    # Read Aggregate names
    aggregateslist = [a.name for a in metadata.aggregates]
    print( aggregateslist)
    # Read Aggregate type instantiated
    # Aggregate metadata depends on the type deployed
    for a in aggregateslist:
        print( a)
        print( interface.get_property( obj_id, a + ".AggrName") )

    if metadata.base_class != '':
        base_properties = get_properties(obj_id, metadata.base_class)
        return base_properties + this_class
    else:
        return this_class


def process_object(obj_id: int, is_new_repo: bool):
    constrained, object_list = interface.list_objects_ex(obj_id, False, [], '', True, 10000)

    for obj in object_list:
        data = {'id': obj.id, 'name': obj.name, 'class_name': obj.class_name, 'properties': []}

        properties = get_properties(obj.id, obj.class_name)
        data['properties'] = [(class_name, {n: v.value for n, v in props}) for class_name, props in properties]

        data_path = os.path.join(repo_location, f'{obj.full_name}.txt')
        with open(data_path, 'w') as f:
            json.dump(data, f, indent=2, cls=GSEEncoder)

        if is_new_repo:
            repo.index.add([data_path])

        if obj.is_group():
            process_object(obj.id, is_new_repo)


new_repo = os.path.exists(repo_location)

if new_repo:
    repo = Repo.init(repo_location)
else:
    repo = Repo(repo_location)


with ConnectionManager('localhost', 5481, 'gsgit', ConnectFlags.IsCompressedLink) as interface:
    # Add connection credentials as required
    
    o = interface.find_object("Example Projects.Oil and Gas")
    process_object(o.id, new_repo)


if repo.is_dirty():
    repo.index.commit("")
