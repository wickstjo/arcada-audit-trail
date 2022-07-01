from utils.worker import skeleton, launch
from utils.misc import log, create_secret, wrapper, timestamp

class edge_worker(skeleton):
    def created(self):
        self.log('STARTUP:\t\t' + 'EDGE WORKER')

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

        # SOMETHING WENT WRONG, LOG ERROR
        if not data.payload.success:
            self.log('ERROR:\t\t{} (time: {})'.format(data.payload.reason, turnaround))
            return

        # OTHERWISE, SAVE STORAGE DEVICE IN STATE
        self.storage_device = data.payload.storage

        # LOG SUCCESS
        self.log('SUCCESS:\t\t' + 'SERVICE HANDSHAKE RESOLVED (time: {})'.format(turnaround))

    # ADD IOT LINK
    def iot_link(self, data):
        self.log('SUCCESS:\t\tIOT LINK ESTABLISHED (distance: {})'.format(data.payload.distance))

    # RECEIVE SYSLOGS FROM IOT
    def log_dump(self, data):

        # TODO: MAKE SURE IOT DEVICE IS LINKED

        self.log('ACTION:\t\tRECEIVED {} ROWS OF LOGS'.format(len(data.payload.logs)))

        # FIND & LOG ANOMALIES
        anomalies = self.find_anomalies(data.payload.logs)
        percentage = len(anomalies) / len(data.payload.logs) * 100
        self.log('ACTION:\t\tDETECTED {} ANOMALIES ({}%)'.format(len(anomalies), percentage))

        # SUBMIT ANONMALIES FOR STORAGE
        if len(anomalies) > 0:
            self.publish(self.storage_device, {
                'source': self.config.edge.keys.public,
                'payload': {
                    'action': 'store_anomalies',
                    'anomalies': anomalies,
                }
            })

            self.log('ACTION:\t\tSUBMITTED ANOMALIES FOR STORAGE')
    # 
    def find_anomalies(self, logs):
        container = []

        # FIND ANOMALIES
        for string in logs:
            if 'a' in string:
                container.append(string)

        return container

# BOOT UP WORKER
launch(edge_worker)