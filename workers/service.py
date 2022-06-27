from utils.worker import skeleton, launch
from utils.misc import log, create_secret, straight_distance, prettify_dict

class service_worker(skeleton):
    def created(self):
        log('SERVICE WORKER STARTED..')
        self.edge = self.config.edge
        self.config = self.config.service

        # REGISTGERED EDGES
        self.edges = {}

        # WHITELISTED CALLBACK ACTIONS
        self.actions = {
            'iot_handshake': self.iot_handshake,
            'edge_handshake': self.edge_handshake
        }

        # SUBSCRIBE TO MESSAGES
        self.subscribe(self.config.channel)

    # PERFORM EDGE HANDSHAKE
    def edge_handshake(self, data):

        # GENERATE RESPONSE CHANNEL
        response_channel = create_secret()

        # SAVE EDGE IN STATE
        self.edges[data.source] = prettify_dict({
            'location': data.payload.location.raw(),
            'channel': response_channel
        })
        
        # CREATE & ENCODE MESSAGE
        message = self.encode_data({
            'source': self.config.keys.public,
            'payload': {
                'encryption': {
                    'public': data.source,
                    'private': self.config.keys.private,
                },
                'action': 'log_exchange',
                'channel': response_channel
            }
        })

        # PUBLISH MSG TO SERVICE CHANNEL
        self.publish(data.payload.channel, message)
        self.leave(data.payload.channel)

    # FIND CLOSEST EDGE DEVICE
    def closest_edge(self, iot):
        best_edge = None
        best_distance = float('inf')

        # NO EDGES EXIST
        if len(self.edges) == 0:
            return best_edge

        # FIND THE CLOSEST
        for name in self.edges:
            edge = self.edges[name]
            distance = straight_distance(edge, iot)

            # UPDATE WHEN A BETTER DISTANCE IS FOUND
            if distance < best_distance:
                best_edge = edge
                best_distance = distance

        return best_edge.channel, best_distance

    # PERFORM IOT HANDSHAKE
    def iot_handshake(self, data):

        # FIND CLOSEST EDGE
        iot_coords = data.payload.location
        response = self.closest_edge(iot_coords)
        
        # DEFAULT RESPONSE MESSAGE
        message = self.encode_data({
            'source': self.config.keys.public,
            'payload': {
                'success': False,
                'reason': 'No edge devices found',
                'action': 'log_exchange',
            }
        })

        # EDGE FOUND, UPDATE MESSAGE
        if response:
            message = self.encode_data({
                'source': self.config.keys.public,
                'payload': {
                    'success': True,
                    'action': 'log_exchange',
                    'edge': {
                        'channel': response[0],
                        'distance': response[1]
                    }
                }
            })

        # PUBLISH RESPONSE TO SOURCE
        self.publish(data.payload.channel, message)
        self.leave(data.payload.channel)

# BOOT UP WORKER
launch(service_worker)