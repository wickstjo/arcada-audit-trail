from utils.worker import skeleton, launch
from utils.misc import log, create_secret

class iot_worker(skeleton):
    def created(self):
        log('IOT WORKER STARTED..')
        self.service = self.config.service
        self.config = self.config.iot

        # WHITELISTED CALLBACK ACTIONS
        self.actions = {
            'log_exchange': self.log_exchange,
        }

        # RUN SERVICE QUERY
        self.service_query()

    # START CONNECTION PROCESS
    def service_query(self):

        # GENERATE RESPONSE CHANNEL
        response_channel = create_secret()

        # CREATE & ENCODE MESSAGE
        message = self.encode_data({
            'source': self.config.keys.public,
            'payload': {
                'encryption': {
                    'public': self.service.keys.public,
                    'private': self.config.keys.private
                },
                'location': {
                    'x': 8,
                    'y': 5
                },
                'task': 'log_audit',
                'action': 'iot_handshake',
                'channel': response_channel
            }
        })

        # PUBLISH MSG TO SERVICE CHANNEL
        self.publish(self.service.channel, message)
        self.leave(self.service.channel)

        # SUBSCRIBE TO RESPONSE CHANNEL
        self.subscribe(response_channel)

    def log_exchange(self, data):
        log(data)

# BOOT UP WORKER
launch(iot_worker)