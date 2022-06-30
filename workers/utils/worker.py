from utils.misc import load_yaml, wrapper, log, sleep, time_delta
from utils.rabbit import create_instance
import base64
import hashlib
import json

class skeleton:
    def __init__(self):

        # LOAD WORKER CONFIG & SAVE IT
        self.config = load_yaml('./config.yml')

        # AUXILLARY STATES
        self.rabbit = {}
        self.requests = {}
        self.links = {}

        # RUN PSEUDO CONSTRUCTOR FUNC
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

        # ADD PAYLOAD CHECKSUM
        message['checksum'] = self.hashify(message['payload'])
        
        instance = self.get_instance(channel)
        encoded = self.encode_data(message)
        instance.publish(channel, encoded)

        log('PUSHED MESSAGE TO:\t' + channel)

    # SUBSCRIBE TO RABBIT FEED
    def subscribe(self, channel):
        def callback(channel, method, properties, body):
            decoded = self.decode_data(body)

            # IF DECODING PROCESS WORKER OUT, CALL NEXT FUNC            
            if decoded:
                log('VALID MSG FROM:\t' + decoded.source)
                
                self.action(decoded)
                print()
                return
            
            # OTHERWISE, PRINT ERROR
            log('INVALID MSG FROM:\t' + decoded.source)
        log('SUBSCRIBED TO:\t' + channel)
        print()
        
        # SAVE CONNECTION IN STATE
        instance = self.get_instance(channel)
        instance.consume(channel, callback)

    # UNSUBSCRIBE FROM CHANNEL
    def leave(self, channel):
        instance = self.get_instance(channel)
        instance.cancel(channel)
        del self.rabbit[channel]

        log('UNSUBSCRIBED FROM:\t' + channel)

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
            return wrapper(data)
        
        # IF IT FAILS, RETURN NULL
        except:
            return None

    # ATTEMPT TO TRIGGER WORKER ACTION
    def action(self, data):

        # IF THE ACTION EXISTS, RUN IT
        if data.payload.action in self.actions:
            log('ACTION TRIGGERED:\t' + data.payload.action)
            self.actions[data.payload.action](data)
            return
        
        # OTHERWISE, THROW ERROR
        log('UNKNOWN ACTION:\t' + data.payload.action)

    # GENERATE EXECUTION 
    def hashify(self, data):
        encoded = self.encode_data(data)
        return hashlib.sha256(encoded).hexdigest()

    # VALIDATE REQUEST CONTAINING A SECRET
    def validate_secret(self, data):

        # ERROR, REQUEST SECRET DOES NOT EXIST
        if data.payload.secret not in self.requests:
            log('ERROR:\t\t' + 'SECRET DOES NOT EXIST')
            return None

        # ERROR, REQUEST SOURCE NOT CORRECT
        if self.requests[data.payload.secret].source != data.source:
            log('ERROR:\t\t' + 'REQUEST SECRET SOURCE IS INCORRECT')
            return None

        # COMPUTE TIME DELTA & DELETE THE REQUEST
        delta = time_delta(self.requests[data.payload.secret].timestamp)
        del self.requests[data.payload.secret]

        return delta

# BOOT UP WORKER
def launch(worker):
    try:
        worker()
    except KeyboardInterrupt:
        print()
        log('MANUALLY KILLED WORKER..')