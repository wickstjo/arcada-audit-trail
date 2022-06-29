from utils.worker import skeleton, launch
from utils.misc import log, create_secret, wrapper, find_closest, timestamp

class service_worker(skeleton):
    def created(self):
        log('STARTUP:\t\t' + 'SERVICE WORKER')

        # DEVICE COLLECTIONS
        self.storage_collection = {}
        self.edge_collection = {}
        self.iot_collection = {}

        # WHITELISTED CALLBACK ACTIONS
        self.actions = {
            'storage_handshake': self.storage_handshake,
            'edge_handshake': self.edge_handshake,
            'iot_handshake': self.iot_handshake,
        }

        # SUBSCRIBE TO SERVICE CHANNEL
        self.subscribe(self.config.service.keys.public)

    # PERFORM STORAGE HANDSHAKE
    def storage_handshake(self, data):
        print(data)

    # PERFORM EDGE HANDSHAKE
    def edge_handshake(self, data):

        # CREATE TYPE PROPERTY IF IT DOESNT EXIST
        if data.payload.type not in self.edge_collection:
            self.edge_collection[data.payload.type] = {}

        # SAVE EDGE COORDINATES IN STATE
        self.edge_collection[data.payload.type][data.source] = wrapper({
            'location': data.payload.location,
            'timestamp': timestamp()
        })

        # CONTACT EDGE
        self.publish(data.source, {
            'source': self.config.service.keys.public,
            'payload': {
                'action': 'handshake_response',
                'success': True,
            }
        })

    # PERFORM IOT HANDSHAKE
    def iot_handshake(self, data):

        # FIND CLOSEST EDGE
        response = find_closest(
            data.payload,
            self.collections['edge']
        )

        # NO EDGES, RESPOND WITH ERROR
        if not response:
            return self.publish(data.source, {
                'source': self.config.service.keys.public,
                'payload': {
                    'action': 'add_link',
                    'success': False,
                    'reason': 'No edge devices found',
                }
            })

        # CONTACT EDGE
        self.publish(response.edge, {
            'source': self.config.service.keys.public,
            'payload': {
                'action': 'add_link',
                'iot': {
                    'channel': data.source,
                    'distance': response.distance
                }
            }
        })

        # CONTACT IOT
        self.publish(data.source, {
            'source': self.config.service.keys.public,
            'payload': {
                'action': 'add_link',
                'success': True,
                'edge': {
                    'channel': response.node,
                    'distance': response.distance
                }
            }
        })

# BOOT UP WORKER
launch(service_worker)