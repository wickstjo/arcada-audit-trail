from utils.worker import skeleton, launch
from utils.misc import log, create_secret

class iot_worker(skeleton):
    def created(self):
        log('IOT WORKER STARTED..')
        self.service_channel = self.config.service.channel
        self.config = self.config.iot

        # WHITELISTED CALLBACK ACTIONS
        self.actions = {
            'iot-connect': self.iot_connect,
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
                'action': 'iot-connect',
                'channel': response_channel
            }
        })

        # PUBLISH & SUBSCRIBE
        self.publish(self.service_channel, message)
        self.subscribe(response_channel)

    def iot_connect(self, data):
        log('iot-connect')

# BOOT UP WORKER
launch(iot_worker)