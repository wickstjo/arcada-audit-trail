from utils.worker import skeleton, launch
from utils.misc import log, create_secret

class iot_worker(skeleton):
    def created(self):
        log('IOT WORKER STARTED..')

        # WHITELISTED CALLBACK ACTIONS
        self.actions = {
            'iot-connect': self.iot_connect,
        }

        # RUN SERVICE QUERY
        self.service_query()

    # START CONNECTION PROCESS
    def service_query(self):

        # RELEVANT CHANNELS
        target_channel = self.config.service.channel
        response_channel = create_secret()

        # CREATE & ENCODE MESSAGE
        message = self.encode_data({
            'source': self.config.iot.keys.public,
            'payload': {
                'action': 'iot-connect',
                'channel': response_channel
            }
        })

        # PUBLISH & SUBSCRIBE
        self.publish(target_channel, message)
        self.subscribe(response_channel, self.action)

    def iot_connect(self, data):
        log('iot-connect')

# BOOT UP WORKER
launch(iot_worker)