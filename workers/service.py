from utils.worker import skeleton, launch
from utils.misc import log, create_secret

class service_worker(skeleton):
    def created(self):
        log('SERVICE WORKER STARTED..')
        self.edge = self.config.edge
        self.config = self.config.service

        # WHITELISTED CALLBACK ACTIONS
        self.actions = {
            'iot_handshake': self.iot_handshake,
            'edge_handshake': self.edge_handshake
        }

        # SUBSCRIBE TO MESSAGES
        self.subscribe(self.config.channel)

    # PERFORM IOT HANDSHAKE
    def iot_handshake(self, data):

        # GENERATE RESPONSE CHANNEL
        response_channel = create_secret()
        
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

    # PERFORM EDGE HANDSHAKE
    def edge_handshake(self, data):

        # GENERATE RESPONSE CHANNEL
        response_channel = create_secret()
        
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

# BOOT UP WORKER
launch(service_worker)