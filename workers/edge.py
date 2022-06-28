from utils.worker import skeleton, launch
from utils.misc import log, create_secret

class edge_worker(skeleton):
    def created(self):
        log('EDGE WORKER STARTED..')
        self.state.connections = 0

        # WHITELISTED CALLBACK ACTIONS
        self.actions = {
            'signup': self.signup,
            'add_link': self.add_link,
            'log_dump': self.log_dump,
        }

        # RUN SERVICE QUERY & SUBSCRIBE TO CHANNEL
        self.service_query()
        self.subscribe(self.config.edge.public)

    # START CONNECTION PROCESS
    def service_query(self):

        # PUBLISH MSG TO SERVICE CHANNEL
        service_channel = self.config.service.public

        self.publish(service_channel, {
            'source': self.config.edge.public,
            'payload': {
                'action': 'edge_handshake',
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