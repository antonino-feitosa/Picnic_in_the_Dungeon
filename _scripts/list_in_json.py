
import os
import json

path = "../_resources"


resources = os.listdir(path)
resources.sort()
#resources = ['_resouces/' + x for x in resources]

with open('resources.json', 'w') as store_data:
    json.dump(resources, store_data)
