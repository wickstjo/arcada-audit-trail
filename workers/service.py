from utils.worker import skeleton, launch
from utils.misc import log, create_secret, wrapper, find_closest, timestamp

class service_worker(skeleton):
    def created(self):

        # INITIALIZE LOGGER
        self.init_logger('service', self.config.service)

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
        self.log({
            'message': 'Storage device created',
            'device': data.source
        })

    # PERFORM EDGE HANDSHAKE
    def edge_handshake(self, data):

        # FIND CLOSEST STORAGE DEVICE
        response = find_closest(
            data.payload,
            self.storage_collection
        )

        # ERROR, NO STORAGE DEVICES EXIST
        if not response:
            self.log({
                'message': 'No storage devices found',
            })

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
        self.log({
            'message': 'Relationship link created',
            'edge': data.source,
            'storage': response.node
        })

    # PERFORM IOT HANDSHAKE
    def iot_handshake(self, data):

        # FIND CLOSEST EDGE
        response = find_closest(
            data.payload,
            self.edge_collection
        )

        # ERROR, NO EDGE DEVICES EXIST
        if not response:
            self.log({
                'message': 'No edge devices found',
            })

            return self.publish(data.source, {
                'source': self.config.service.keys.public,
                'payload': {
                    'action': 'handshake_response',
                    'success': False,
                    'reason': 'No edge devices found',
                    'secret': data.payload.secret,
                }
            })

        # CONTACT EDGE
        self.publish(response.node, {
            'source': self.config.service.keys.public,
            'payload': {
                'action': 'iot_link',
                'iot': data.source,
                'distance': response.distance,
                'secret': data.payload.secret,
            }
        })

        # CONTACT IOT
        self.publish(data.source, {
            'source': self.config.service.keys.public,
            'payload': {
                'action': 'handshake_response',
                'success': True,
                'edge': response.node,
                'distance': response.distance,
                'secret': data.payload.secret,
            }
        })

        # LOG SUCCESS
        self.log({
            'message': 'Relationship link created',
            'iot': data.source,
            'edge': response.node
        })

# BOOT UP WORKER
launch(service_worker)