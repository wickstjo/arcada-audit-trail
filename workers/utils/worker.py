from utils.misc import load_yaml, prettify_dict, log, sleep
from utils.rabbit import create_instance
import base64
import hashlib
import json

class skeleton:
    def __init__(self):

        # LOAD WORKER CONFIG & CREATE RABBIT CONNECTION CONTAINER
        self.config = load_yaml('./config.yml')
        self.rabbit = {}

        # RUN NEXT FUNC
        self.created()

    # PSEUDO CONSTRUCTOR -- MUST BE OVERLOADED
    def created(self):
        raise NotImplementedError
    
    # GET RABBIT INSTANCE
    def get_instance(self, channel):
        if channel not in self.rabbit:
            self.rabbit[channel] = create_instance()

        return self.rabbit[channel]

    # ENCODE RABBIT MESSAGE & PUBLISH IT
    def publish(self, channel, message):
        sleep(1)
        instance = self.get_instance(channel)
        instance.publish(channel, message)

        log('PUSHED MESSAGE TO: ' + channel)

    # SUBSCRIBE TO RABBIT FEED
    def subscribe(self, channel):
        def callback(channel, method, properties, body):
            decoded = self.decode_data(body)

            # IF DECODING PROCESS WORKER OUT, CALL NEXT FUNC            
            if decoded:
                log('VALID MSG INTERCEPTED')
                self.action(decoded)
                return
            
            # OTHERWISE, PRINT ERROR
            log('INVALID MSG INTERCEPTED')

        log('JOINED CHANNEL: ' + channel)
        
        # SAVE CONNECTION IN STATE
        instance = self.get_instance(channel)
        instance.consume(channel, callback)

    # UNSUBSCRIBE FROM CHANNEL
    def leave(self, channel):
        instance = self.get_instance(channel)
        instance.cancel(channel)
        del self.rabbit[channel]

        log('LEFT CHANNEL: ' + channel)

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
            log('ACTION FOUND: ' + data.payload.action)
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