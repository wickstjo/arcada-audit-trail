import math
from utils.worker import skeleton, launch
from utils.misc import log, create_secret, wrapper, timestamp

class storage_worker(skeleton):
    def created(self):
        self.log('STARTUP:\t\t' + 'STORAGE WORKER')
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
            self.log('ERROR:\t\t' + 'HANDSHAKE RESPONSE FROM NON-SERVICE')
            return

        # SOMETHING WENT WRONG, LOG ERROR
        if not data.payload.success:
            self.log('ERROR:\t\t{} ({} S)'.format(data.payload.reason, turnaround))
            return

        # OTHERWISE, LOG SUCCESS
        self.log('SUCCESS:\t\t' + 'SERVICE HANDSHAKE RESOLVED (time: {})'.format(turnaround))

    # WHITELIST EDGE DEVICE
    def edge_link(self, data):

        # MAKE SURE THE SENDER IS THE SERVICE
        if data.source != self.config.service.keys.public:
            self.log('ERROR:\t\t' + 'LINK REQUEST FROM NON-SERVICE')
            return

        # ADD LINK TO STATE
        self.edge_collection[data.payload.edge] = {
            'timestamp': timestamp(),
            'distance': data.payload.distance
        }

        # LOG SUCCESS
        self.log('SUCCESS\t\t' + 'EDGE LINK ESTABLISHED (distance: {})'.format(data.payload.distance))

    # PERMANENTLY STORE SYSLOG
    def store_anomalies(self, data):

        # TODO: MAKE SURE EDGE IS LINKED

        self.log('ACTION:\t\tRECEIVED {} ANOMALIES'.format(len(data.payload.anomalies)))

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

        self.log('ACTION:\t\tANOMALIES STORED')

# BOOT UP WORKER
launch(storage_worker)