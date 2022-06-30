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
        return wrapper(data)

# WRAP DICT INTO A EASIER TO USE CLASS
class wrapper:
    def __init__(self, data_dict):
        self.data_dict = data_dict
        self.populate(data_dict)

    # POPULATE INSTANCE PROPS
    def populate(self, data):
        for key in data:
            if type(data[key]) == dict:
                setattr(self, key, wrapper(data[key]))
            else:
                setattr(self, key, data[key])

    # AUTO PRINTING
    def __str__(self):
        return json.dumps(self.data_dict, indent=2)

    def push(self, key, value):
        setattr(self, key, value)
        self.data_dict[key] = value

    def raw(self):
        return self.data_dict

# FORMATTED PRINT FUNC
def log(msg):
    now = datetime.now().strftime("%H:%M:%S:%f")
    prefix = '[{}]'.format(now)
    print(prefix, msg, flush=True)

# GENERATE RANDOM BITS OF DATA
def create_secret(length):
    return secrets.token_hex(nbytes=length)

# SLEEP FOR X SECONDS
def sleep(seconds):
    time.sleep(seconds)

# GENERATE CURRENT TIMESTAMP
def timestamp():
    return time.time()

# COMPUTE DELTA BETWEEN TIMESTAMPS
def time_delta(start):
    end = timestamp()
    return round(abs(end-start), 4)

# FIND CLOSEST EDGE DEVICE
def find_closest(target, nodes):
    best_node = None
    best_distance = float('inf')

    # NO EDGES EXIST
    if len(nodes) == 0:
        return best_node

    # FIND THE CLOSEST
    for current in nodes:
        node = nodes[current]

        # COMPUTE STRAIGHT LINE DISTANCE
        P1 = abs(target.location.x - node.location.x)**2
        P2 = abs(target.location.y - node.location.y)**2
        distance = math.sqrt(P1 + P2)

        # UPDATE WHEN A BETTER DISTANCE IS FOUND
        if distance < best_distance:
            best_node = current
            best_distance = distance

    return wrapper({
        'node': best_node,
        'distance': best_distance
    })