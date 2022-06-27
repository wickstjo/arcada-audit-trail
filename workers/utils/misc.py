import yaml
import json
from datetime import datetime
import secrets
import time
import math

# LOAD YAML DATA
def load_yaml(path):
    with open(path, mode='r') as file:
        data = yaml.load(file, Loader=yaml.FullLoader)
        return prettify_dict(data)

# WRAP DICT INTO A EASIER TO USE CLASS
class prettify_dict:
    def __init__(self, data_dict):
        self.data_dict = data_dict

        for key in data_dict:
            if type(data_dict[key]) == dict:
                setattr(self, key, prettify_dict(data_dict[key]))
            else:
                setattr(self, key, data_dict[key])

    # AUTO PRINTING
    def __str__(self):
        return json.dumps(self.data_dict, indent=2)

    def raw(self):
        return self.data_dict

# FORMATTED PRINT FUNC
def log(msg):
    now = datetime.now().strftime("%H:%M:%S:%f")
    prefix = '[{}]'.format(now)
    print(prefix, msg, flush=True)

# GENERATE RANDOM BITS OF DATA
def create_secret(prefix=''):
    return secrets.token_hex(nbytes=16)

# SLEEP FOR X SECONDS
def sleep(seconds):
    time.sleep(seconds)

# COMPUTE STRAIGHT LINE DISTANCE
def straight_distance(edge, iot):
    foo = abs(iot.x - edge.location.x)**2
    bar = abs(iot.y - edge.location.y)**2

    return math.sqrt(foo + bar)