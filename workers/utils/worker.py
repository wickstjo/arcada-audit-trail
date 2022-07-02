from utils.misc import load_yaml, wrapper, log, sleep, time_delta, formatted_timestamp, timestamp, save_yaml
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

        self.logger = {}

        # RUN PSEUDO CONSTRUCTOR FUNC
        self.created()

    # PSEUDO CONSTRUCTOR -- MUST BE OVERLOADED
    def created(self, name, params):
        raise NotImplementedError

    def init_logger(self, name, params):

        # STITCH TOGETHER LOG FILE
        now = int(timestamp())
        self.log_file = 'logs/{}-{}.yml'.format(now, name)

        # SAVE INIT CONFIG
        details = { **params.raw() }
        details['worker'] = name

        # PUSH DATA
        self.logger['details'] = details
        self.logger['logs'] = {}
        
        # LOG WORKER START
        self.log({
            'message': '{} worker started'.format(name.capitalize())
        })
    
    def log(self, params):
        # entry = {**params}
        # entry['timestamp'] = formatted_timestamp()
        
        # self.logger['logs'].append(entry)

        now = formatted_timestamp()
        self.logger['logs'][now] = params
        
        prefix = '[{}]'.format(now)
        print(prefix, params['message'], flush=True)

        # SAVE LOGFILE
        save_yaml(self.log_file, self.logger)
    
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

        self.log({
            'message': 'Pushed message to channel',
            'channel': channel
        })

    # SUBSCRIBE TO RABBIT FEED
    def subscribe(self, channel):
        def callback(channel, method, properties, body):
            decoded = self.decode_data(body)

            # IF DECODING PROCESS WORKER OUT, CALL NEXT FUNC            
            if decoded:
                self.log({
                    'message': 'Valid message received',
                    'caller': decoded.source
                })
                
                self.action(decoded)
                print()
                return
            
            # OTHERWISE, PRINT ERROR
            self.log({
                'message': 'Undecipherable message intercepted',
                'caller': decoded.source
            })

        # LOG SUBSCRIPTION
        self.log({
            'message': 'Subscribed to channel feed',
            'channel': channel
        })
        print()
        
        # SAVE CONNECTION IN STATE
        instance = self.get_instance(channel)
        instance.consume(channel, callback)

    # UNSUBSCRIBE FROM CHANNEL
    def leave(self, channel):
        instance = self.get_instance(channel)
        instance.cancel(channel)
        del self.rabbit[channel]

        # LOG ACTION
        self.log({
            'message': 'Unsubscribed from channel feed',
            'channel': channel
        })

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

        # ERROR, ACTION DOESNT EXIST
        if data.payload.action not in self.actions:
            return self.log({
                'message': 'Unknown action trigger blocked',
                'action': data.payload.action,
                'caller': data.source
            })

        # ACTION EXISTS!
        self.log({
            'message': 'Action triggered',
            'action': data.payload.action,
            'caller': data.source
        })

        # CALL ACTION
        self.actions[data.payload.action](data)

    # GENERATE EXECUTION 
    def hashify(self, data):
        encoded = self.encode_data(data)
        return hashlib.sha256(encoded).hexdigest()

    # VALIDATE REQUEST CONTAINING A SECRET
    def validate_secret(self, data):

        # ERROR, REQUEST SECRET DOES NOT EXIST
        if data.payload.secret not in self.requests:
            self.log({
                'message': 'Unexistent secret',
                'action': data.payload.action,
                'caller': data.source
            })
            return None

        # ERROR, REQUEST SOURCE NOT CORRECT
        if self.requests[data.payload.secret].source != data.source:
            self.log({
                'message': 'Incorrect secret',
                'action': data.payload.action,
                'caller': data.source
            })
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