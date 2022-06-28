import math
from utils.worker import skeleton, launch
from utils.misc import log, create_secret, prettify_dict

class service_worker(skeleton):
    def created(self):
        log('SERVICE WORKER STARTED..')
        self.state.edges = {}

        print(create_secret())

        # WHITELISTED CALLBACK ACTIONS
        self.actions = {
            'edge_handshake': self.edge_handshake,
            'iot_handshake': self.iot_handshake,
        }

        # SUBSCRIBE TO SERVICE CHANNEL
        self.subscribe(self.config.service.public)

    # PERFORM EDGE HANDSHAKE
    def edge_handshake(self, data):

        # SAVE EDGE COORDINATES IN STATE
        self.state.edges[data.source] = data.payload.location

        # CONTACT EDGE
        self.publish(data.source, {
            'source': self.config.service.public,
            'payload': {
                'action': 'signup',
                'success': True,
            }
        })

    # FIND CLOSEST EDGE DEVICE
    def closest_edge(self, iot):
        best_edge = None
        best_distance = float('inf')

        # NO EDGES EXIST
        if len(self.state.edges) == 0:
            return best_edge

        # FIND THE CLOSEST
        for current in self.state.edges:
            edge = self.state.edges[current]

            # COMPUTE STRAIGHT LINE DISTANCE
            P1 = abs(iot.x - edge.x)**2
            P2 = abs(iot.y - edge.y)**2
            distance = math.sqrt(P1 + P2)

            # UPDATE WHEN A BETTER DISTANCE IS FOUND
            if distance < best_distance:
                best_edge = current
                best_distance = distance

        return prettify_dict({
            'edge': best_edge,
            'distance': best_distance
        })

    # PERFORM IOT HANDSHAKE
    def iot_handshake(self, data):

        # FIND CLOSEST EDGE
        iot_coords = data.payload.location
        response = self.closest_edge(iot_coords)

        # NO EDGES, RESPOND WITH ERROR
        if not response:
            return self.publish(data.source, {
                'source': self.config.service.public,
                'payload': {
                    'action': 'add_link',
                    'success': False,
                    'reason': 'No edge devices found',
                }
            })

        # CONTACT EDGE
        self.publish(response.edge, {
            'source': self.config.service.public,
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
            'source': self.config.service.public,
            'payload': {
                'action': 'add_link',
                'success': True,
                'edge': {
                    'channel': response.edge,
                    'distance': response.distance
                }
            }
        })

# BOOT UP WORKER
launch(service_worker)