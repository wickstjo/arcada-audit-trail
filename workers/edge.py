from utils.worker import skeleton, launch
from utils.misc import log, create_secret

class edge_worker(skeleton):
    def created(self):
        log('STARTUP:\t\t' + 'EDGE WORKER')

        # WHITELISTED CALLBACK ACTIONS
        self.actions = {
            'signup': self.signup,
            'add_link': self.add_link,
            'log_dump': self.log_dump,
        }

        # RUN SERVICE QUERY & SUBSCRIBE TO CHANNEL
        self.service_handshake()
        self.subscribe(self.config.edge.keys.public)

    # START CONNECTION PROCESS
    def service_handshake(self):

        # PUBLISH MSG TO SERVICE CHANNEL
        service_channel = self.config.service.keys.public

        self.publish(service_channel, {
            'source': self.config.edge.keys.public,
            'payload': {
                'action': 'edge_handshake',
                'type': self.config.edge.type,
                'location': self.config.edge.location.raw()
            }
        })

    # EDGE ADDED EVENT
    def signup(self, data):

        # SUCCESS
        if data.payload.success:
            log('SUCCESS:\t\t' + 'DEVICE REGISTERED')

        # ERROR
        else:
            log('ERROR:\t\t' + data.payload.reason)

    # CONNECTION ADDED
    def add_link(self, data):
        log('LINKED WITH IOT:\t{}'.format(data.payload.iot.channel))

    def log_dump(self, data):
        log('RECEIVED LOGS:\t{} ROWS'.format(len(data.payload.logs)))

# BOOT UP WORKER
launch(edge_worker)