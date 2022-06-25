from utils.worker import skeleton, launch
from utils.misc import log

class service_worker(skeleton):
    def created(self):
        log('SERVICE WORKER STARTED..')
        self.config = self.config.service

        # WHITELISTED CALLBACK ACTIONS
        self.actions = {
            'iot-connect': self.iot_connect,
            'edge-connect': self.edge_connect
        }

        # SUBSCRIBE TO MESSAGES
        self.subscribe(self.config.channel)

    def iot_connect(self, data):
        print('iot-conASDASDASDnect')
        self.unsub(self.config.channel)

    def edge_connect(self, data):
        print('edge-connect')

# BOOT UP WORKER
launch(service_worker)