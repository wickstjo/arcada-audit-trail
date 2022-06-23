import pika
import yaml
import json
from datetime import datetime
import base64
import hashlib

class rabbit_instance:
    def __init__(self, channels):

        # ESTABLISH CONNECTION
        rabbitmq = pika.BlockingConnection(pika.ConnectionParameters(
            host='localhost',
            heartbeat=0
        ))

        # ATTACH MQ CHANNEL
        self.channel = rabbitmq.channel()

        # INITIALIZE MQ CHANNELS
        for channel in channels:
            self.channel.queue_declare(queue=channel)

    # CONSUME CHANNEL EVENTS
    def consume(self, channel, callback):
        
        # SETUP CALLBACK
        self.channel.basic_consume(
            queue=channel,
            on_message_callback=callback,
            auto_ack=True
        )

        # SUBSCRIBE TO TOPIC
        self.channel.start_consuming()

    # PUBLISH CHANNEL EVENT
    def publish(self, channel, payload):
        self.channel.basic_publish(
            exchange='',
            routing_key=channel,
            body=payload
        )

# LOAD YAML DATA
def load_yaml(path):
    with open(path, mode='r') as file:
        return prettify_dict(yaml.load(file, Loader=yaml.FullLoader))

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

# ENCODE PAYLOAD
def encode_data(data):

    # ENCODE STRING
    if type(data) == str:
        to_bytes = str.encode(data)
    
    # ENCODE DICT
    elif type(data) == dict:
        stringified = json.dumps(data)
        to_bytes = str.encode(stringified)

    # RETURN AS BASE64
    return base64.b64encode(to_bytes)

# GENERATE EXECUTION HASH
def generate_hash(data):
    encoded = encode_data(data)
    return hashlib.sha256(encoded).hexdigest()

# DECODE PAYLOAD
def decode_data(data):
    to_bytes = base64.b64decode(data)
    
    # ATTEMPT TO BASE AS DICT
    try:
        return json.loads(to_bytes)
    
    # OTHERWISE, RETURN AS STRING
    except:
        return to_bytes.decode('UTF-8')

# FORMATTED PRINT FUNC
def log(msg):
    now = datetime.now().strftime("%H:%M:%S:%f")
    prefix = '[{}]'.format(now)
    print(prefix, msg, flush=True)

# BOOT UP WORKER
def launch(worker):
    try:
        worker()
    except KeyboardInterrupt:
        print()
        log('MANUALLY KILLED WORKER..')