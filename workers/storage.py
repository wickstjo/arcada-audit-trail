import math
from utils.worker import skeleton, launch
from utils.misc import log, create_secret, prettify_dict

class storage_worker(skeleton):
    def created(self):
        log('STARTUP:\t\t' + 'STORAGE WORKER')

        # INITIALIZE STATE
        self.state.service_connection = 'pending'
        self.state.links = {}

        # WHITELISTED CALLBACK ACTIONS
        self.actions = {
            'handshake_response': self.handshake_response
            'store_data': self.store_data,
        }

        # SHAKE HANDS WITH SERVICE & SUBSCRIBE TO STORAGE CHANNEL
        self.service_handshake()
        self.subscribe(self.config.storage.keys.public)

    # PERFORM SERVICE HANDSHAKE
    def service_handshake(self):
        self.publish(self.config.service.keys.public, {
            'source': self.config.storage.keys.public,
            'payload': {
                'action': 'storage_handshake',
                'type': self.config.storage.type,
            }
        })

    def handshake_response(self, data):
        print(data)

    # UPLOAD LOGS
    def store_data(self, data):
        print(data)

# BOOT UP WORKER
launch(storage_worker)