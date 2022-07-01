from utils.worker import skeleton, launch
from utils.misc import log, create_secret, wrapper, find_closest, timestamp

class service_worker(skeleton):
    def created(self):
        self.log('STARTUP:\t\t' + 'SERVICE WORKER')

        # DEVICE COLLECTIONS
        self.storage_collection = {}
        self.edge_collection = {}

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

        # SAVE DEVICE IN STATE
        self.storage_collection[data.source] = wrapper({
            'type': data.payload.type,
            'location': data.payload.location,
            'timestamp': timestamp()
        })

        # CONTACT DEVICE
        self.publish(data.source, {
            'source': self.config.service.keys.public,
            'payload': {
                'action': 'handshake_response',
                'secret': data.payload.secret,
                'success': True,
            }
        })

        # LOG SUCCESS
        self.log('SUCCESS:\t\t' + 'STORAGE DEVICE CREATED')

    # PERFORM EDGE HANDSHAKE
    def edge_handshake(self, data):

        # FIND CLOSEST STORAGE DEVICE
        response = find_closest(
            data.payload,
            self.storage_collection
        )

        # ERROR, NO STORAGE DEVICES EXIST
        if not response:
            self.log('ERROR:\t\t' + 'NO STORAGE DEVICES FOUND')

            return self.publish(data.source, {
                'source': self.config.service.keys.public,
                'payload': {
                    'action': 'handshake_response',
                    'success': False,
                    'reason': 'No storage devices found',
                    'secret': data.payload.secret,
                }
            })

        # SAVE DEVICE IN STATE
        self.edge_collection[data.source] = wrapper({
            'type': data.payload.type,
            'location': data.payload.location,
            'timestamp': timestamp()
        })

        # CONTACT STORAGE
        self.publish(response.node, {
            'source': self.config.service.keys.public,
            'payload': {
                'action': 'edge_link',
                'edge': data.source,
                'distance': response.distance
            }
        })

        # CONTACT EDGE
        self.publish(data.source, {
            'source': self.config.service.keys.public,
            'payload': {
                'action': 'handshake_response',
                'storage': response.node,
                'secret': data.payload.secret,
                'success': True,
            }
        })

        # LOG SUCCESS
        self.log('SUCCESS:\t\t' + 'EDGE => STORAGE LINK ESTABLISHED')

    # PERFORM IOT HANDSHAKE
    def iot_handshake(self, data):

        # FIND CLOSEST EDGE
        response = find_closest(
            data.payload,
            self.edge_collection
        )

        # ERROR, NO EDGE DEVICES EXIST
        if not response:
            self.log('ERROR:\t\t' + 'NO EDGE DEVICES FOUND')

            return self.publish(data.source, {
                'source': self.config.service.keys.public,
                'payload': {
                    'action': 'handshake_response',
                    'success': False,
                    'reason': 'No edge devices found',
                }
            })

        # CONTACT EDGE
        self.publish(response.node, {
            'source': self.config.service.keys.public,
            'payload': {
                'action': 'iot_link',
                'iot': data.source,
                'distance': response.distance
            }
        })

        # CONTACT IOT
        self.publish(data.source, {
            'source': self.config.service.keys.public,
            'payload': {
                'action': 'handshake_response',
                'success': True,
                'edge': response.node,
                'distance': response.distance
            }
        })

        # LOG SUCCESS
        self.log('SUCCESS:\t\t' + 'IOT => EDGE LINK ESTABLISHED')

# BOOT UP WORKER
launch(service_worker)