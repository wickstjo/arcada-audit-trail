from utils.worker import skeleton, launch
from utils.misc import log, create_secret, wrapper, timestamp

class edge_worker(skeleton):
    def created(self):
        log('STARTUP:\t\t' + 'EDGE WORKER')

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
            log('ERROR:\t\t{} (time: {})'.format(data.payload.reason, turnaround))
            return

        # OTHERWISE, LOG SUCCESS
        log('SUCCESS:\t\t' + 'SERVICE HANDSHAKE RESOLVED (time: {})'.format(turnaround))

    # ADD IOT LINK
    def iot_link(self, data):
        log('SUCCESS:\t\tIOT LINK ESTABLISHED (distance: {})'.format(data.payload.distance))

    def log_dump(self, data):
        log('RECEIVED LOGS:\t{} ROWS'.format(len(data.payload.logs)))

# BOOT UP WORKER
launch(edge_worker)