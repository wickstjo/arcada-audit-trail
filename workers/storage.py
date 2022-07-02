import math
from utils.worker import skeleton, launch
from utils.misc import log, create_secret, wrapper, timestamp

class storage_worker(skeleton):
    def created(self):

        # INITIALIZE LOGGER
        self.init_logger('storage', self.config.storage)

        self.edge_collection = {}
        self.database = {}

        # WHITELISTED CALLBACK ACTIONS
        self.actions = {
            'handshake_response': self.handshake_response,
            'edge_link': self.edge_link,
            'store_anomalies': self.store_anomalies,
        }

        # SHAKE HANDS WITH SERVICE & AWAIT RESPONSE
        self.service_handshake()
        self.subscribe(self.config.storage.keys.public)

    # PERFORM SERVICE HANDSHAKE
    def service_handshake(self):

        # CREATE ID FOR REQUEST
        request_id = create_secret(6)

        # PUSH MESSAGE
        self.publish(self.config.service.keys.public, {
            'source': self.config.storage.keys.public,
            'payload': {
                'action': 'storage_handshake',
                'type': self.config.storage.type,
                'location': self.config.storage.location.raw(),
                'secret': request_id,
            }
        })

        # STORE REQUEST ID FOR VERIFICATION
        self.requests[request_id] = wrapper({
            'source': self.config.service.keys.public,
            'timestamp': timestamp(),
        })

    # HANDSHAKE RESPOONSE
    def handshake_response(self, data):
        turnaround = self.validate_secret(data)

        # VALIDATION FAILED
        if not turnaround:
            return

        # MAKE SURE THE SENDER IS THE SERVICE
        if data.source != self.config.service.keys.public:
            return self.log({
                'message': 'Handshake response from non-service channel blocked',
                'caller': data.source
            })

        # SOMETHING WENT WRONG, LOG ERROR
        if not data.payload.success:
            return self.log({
                'message': 'Handshake process could not be completed',
                'reason': data.payload.reason,
                'turnaround': turnaround
            })

        # OTHERWISE, LOG SUCCESS
        self.log({
            'message': 'Handshake process completed',
            'turnaround': turnaround
        })

    # WHITELIST EDGE DEVICE
    def edge_link(self, data):

        # MAKE SURE THE SENDER IS THE SERVICE
        if data.source != self.config.service.keys.public:
            return self.log({
                'message': 'Link request from non-service channel blocked',
                'channel': data.source
            })

        # ADD LINK TO STATE
        self.edge_collection[data.payload.edge] = {
            'timestamp': timestamp(),
            'distance': data.payload.distance
        }

        # LOG SUCCESS
        self.log({
            'message': 'Edge relationship link created',
            'edge': data.payload.edge,
            'distance': data.payload.distance,
        })

    # PERMANENTLY STORE SYSLOG
    def store_anomalies(self, data):

        # TODO: MAKE SURE EDGE IS LINKED



        # MAKE SURE THE EDGE PROP EXISTS
        if data.source not in self.database:
            self.database[data.source] = []

        # CREATE STORAGE ENTRY
        entry = wrapper({
            'data': data.payload.anomalies,
            'timestamp': timestamp()
        })

        # PUSH IT TO DB
        self.database[data.source].append(entry)

        # LOG SUCCESS
        self.log({
            'message': 'Stored syslog anomalies',
            'amount': len(data.payload.anomalies),
            'caller': data.source,
        })

# BOOT UP WORKER
launch(storage_worker)