from utils.worker import skeleton, launch
from utils.misc import log

class service_worker(skeleton):
    def created(self):
        log('SERVICE WORKER STARTED..')

        # WHITELISTED CALLBACK ACTIONS
        self.actions = {
            'iot-connect': self.iot_connect,
            'edge-connect': self.edge_connect
        }

        # SUBSCRIBE TO MESSAGES
        target_channel = self.config.service.channel
        self.subscribe(target_channel, self.action)

    def iot_connect(self, data):
        print('iot-conASDASDASDnect')

    def edge_connect(self, data):
        print('edge-connect')

# BOOT UP WORKER
launch(service_worker)