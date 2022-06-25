from utils.misc import load_yaml, prettify_dict, log
from utils.rabbit import create_instance
import base64
import hashlib
import json

class skeleton:
    def __init__(self):

        # LOAD WORKER CONFIG & CREATE RABBIT INSTANCE
        self.config = load_yaml('./config.yml')
        self.rabbit = create_instance()

        # RUN NEXT FUNC
        self.created()

    # PSEUDO CONSTRUCTOR -- MUST BE OVERLOADED
    def created(self):
        raise NotImplementedError
    
    # ENCODE RABBIT MESSAGE & PUBLISH IT
    def publish(self, channel, message):
        self.rabbit.publish(channel, message)
        log('PUSHED MESSAGE TO: ' + channel)

    # SUBSCRIBE TO RABBIT FEED
    def subscribe(self, channel, followup):
        def callback(channel, method, properties, body):
            log('RECEIVED MESSAGE')
            decoded = self.decode_data(body)

            # IF DECODING PROCESS WORKER OUT, CALL NEXT FUNC            
            if decoded:
                followup(decoded)
                return
            
            # OTHERWISE, PRINT ERROR
            log('COULD NOT DECIPHER PAYLOAD')

        log('JOINED CHANNEL: ' + channel)
        self.rabbit.consume(channel, callback)

    # ENCODE PAYLOAD
    def encode_data(self, data):

        # ENCODE STRING
        if type(data) == str:
            to_bytes = str.encode(data)
        
        # ENCODE DICT
        elif type(data) == dict:
            stringified = json.dumps(data)
            to_bytes = str.encode(stringified)

        # RETURN AS BASE64
        return base64.b64encode(to_bytes)

    # DECODE PAYLOAD
    def decode_data(self, data):
        
        # ATTEMPT TO DECODE
        try:
            stringified = base64.b64decode(data)
            data = json.loads(stringified)
            return prettify_dict(data)
        
        # IF IT FAILS, RETURN NULL
        except:
            return None

    # ATTEMPT TO TRIGGER WORKER ACTION
    def action(self, data):

        # IF THE ACTION EXISTS, RUN IT
        if data.payload.action in self.actions:
            self.actions[data.payload.action](data)
            return
        
        # OTHERWISE, THROW ERROR
        log('UNKNOWN PAYLOAD ACTION')

    # GENERATE EXECUTION 
    def hashify(self, data):
        encoded = encode_data(data)
        return hashlib.sha256(encoded).hexdigest()

# BOOT UP WORKER
def launch(worker):
    try:
        worker()
    except KeyboardInterrupt:
        print()
        log('MANUALLY KILLED WORKER..')