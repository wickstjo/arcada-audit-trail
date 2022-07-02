from utils.worker import skeleton, launch
from utils.misc import log, create_secret, wrapper, timestamp

class edge_worker(skeleton):
    def created(self):
        
        # INITIALIZE LOGGER
        self.init_logger('edge', self.config.edge)

        # WHITELISTED CALLBACK ACTIONS
        self.actions = {
            'handshake_response': self.handshake_response,
            'iot_link': self.iot_link,
            'log_dump': self.log_dump,
        }

        # RUN SERVICE QUERY & SUBSCRIBE TO CHANNEL
        self.service_handshake()
        self.subscribe(self.config.edge.keys.public)

    # START CONNECTION PROCESS
    def service_handshake(self):

        # CREATE ID FOR REQUEST
        request_id = create_secret(6)

        self.publish(self.config.service.keys.public, {
            'source': self.config.edge.keys.public,
            'payload': {
                'action': 'edge_handshake',
                'type': self.config.edge.type,
                'location': self.config.edge.location.raw(),
                'secret': request_id,
            }
        })

        # STORE REQUEST ID FOR VERIFICATION
        self.requests[request_id] = wrapper({
            'source': self.config.service.keys.public,
            'timestamp': timestamp(),
        })

    # EDGE ADDED EVENT
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
                'turnaround': turnaround,
            })

        # OTHERWISE, SAVE STORAGE DEVICE IN STATE
        self.storage_device = data.payload.storage

        # LOG SUCCESS
        self.log({
            'message': 'Handshake process completed',
            'turnaround': turnaround,
        })

    # ADD IOT LINK
    def iot_link(self, data):

        # IF THE CALLER WASNT THE SERVICE CHANNEL
        if data.source != self.config.service.keys.public:
            return self.log({
                'message': 'Link request from non-service channel blocked',
                'caller': data.source
            })

        # OTHERWISE, LOG SUCCESS
        self.log({
            'message': 'IOT relationship link created',
            'iot': data.payload.distance,
            'distance': data.payload.distance
        })

    # RECEIVE SYSLOGS FROM IOT
    def log_dump(self, data):

        # TODO: MAKE SURE IOT DEVICE IS LINKED

        # FIND & LOG ANOMALIES
        anomalies = self.find_anomalies(data.payload.logs)
        # percentage = len(anomalies) / len(data.payload.logs) * 100

        # LOG INTERCEPTION
        self.log({
            'message': 'Parsed syslogs from iot',
            'rows': len(data.payload.logs),
            'anomalies': len(anomalies),
            'caller': data.source,
        })

        # NO ANOMALIES FOUND -- STOP HERE 
        if len(anomalies) > 0:
            self.publish(self.storage_device, {
                'source': self.config.edge.keys.public,
                'payload': {
                    'action': 'store_anomalies',
                    'anomalies': anomalies,
                }
            })

    # FIND ANOMALIES FROM SYSLOGS
    def find_anomalies(self, logs):
        container = []

        # FIND ANOMALIES
        for string in logs:
            if 'a' in string:
                container.append(string)

        return container

# BOOT UP WORKER
launch(edge_worker)