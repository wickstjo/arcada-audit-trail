from utils.worker import skeleton, launch
from utils.misc import log, create_secret, sleep
import random

class iot_worker(skeleton):
    def created(self):
        log('STARTUP:\t\t' + 'IOT WORKER')

        # WHITELISTED CALLBACK ACTIONS
        self.actions = {
            'add_link': self.add_link,
        }

        # RUN SERVICE QUERY & SUBSCRIBE TO IOT CHANNEL
        self.service_handshake()
        self.subscribe(self.config.iot.keys.public)

    # START CONNECTION PROCESS
    def service_handshake(self):

        # PUBLISH MSG TO SERVICE CHANNEL
        service_channel = self.config.service.keys.public

        self.publish(service_channel, {
            'source': self.config.iot.keys.public,
            'payload': {
                'action': 'iot_handshake',
                'location': self.config.iot.location.raw()
            }
        })

    # FIND EDGE RESPONSE
    def add_link(self, data):

        # IF EVERYTHING WENT OK
        if data.payload.success:
            log('LINKED WITH EDGE:\t' + data.payload.edge.channel)

            for _ in range(5):
                sleep(5)
                self.dump_logs(data.payload.edge.channel)

        # OTHERWISE, RENDER ERROR
        else:
            log('ERROR:\t\t' + data.payload.reason)
            # log('TRYING AGAIN IN 5 SECONDS')
            # sleep(5)
            # self.service_query()

    def dump_logs(self, edge):
        rows = random.randint(3, 30)

        self.publish(edge, {
            'source': self.config.iot.keys.public,
            'payload': {
                'action': 'log_dump',
                'logs': [create_secret() for x in range(rows)]
            }
        })

        log('DUMPED LOGS:\t\t{} ROWS'.format(rows))

# BOOT UP WORKER
launch(iot_worker)