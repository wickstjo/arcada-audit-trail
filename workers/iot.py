from utils.worker import skeleton, launch
from utils.misc import log, create_secret, sleep
import random

class iot_worker(skeleton):
    def created(self):
        self.log('STARTUP:\t\t' + 'IOT WORKER')

        # WHITELISTED CALLBACK ACTIONS
        self.actions = {
            'handshake_response': self.handshake_response,
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
    def handshake_response(self, data):

        # SOMETHING WENT WRONG
        if not data.payload.success:
            self.log('ERROR:\t\t' + data.payload.reason)
            return

        # SAVE EDGE DEVICE IN STATE
        self.edge_device = data.payload.edge

        # OTHERWISE, PROCEDE NORMALLY
        self.log('SUCCESS:\t\tEDGE LINK ESTABLISHED (distance: {})'.format(data.payload.distance))
        print()

        # DUMP TESTLOGS WITH INTERVAL X TIMES
        for _ in range(10):
            sleep(2)
            self.dump_logs()

    # DUMP LOGS
    def dump_logs(self):
        # rows = random.randint(3, 30)
        rows = 20

        self.publish(self.edge_device, {
            'source': self.config.iot.keys.public,
            'payload': {
                'action': 'log_dump',
                'logs': [create_secret(5) for x in range(rows)]
            }
        })

        self.log('ACTION:\t\tDUMPED {} ROWS OF LOGS'.format(rows))
        print()

# BOOT UP WORKER
launch(iot_worker)