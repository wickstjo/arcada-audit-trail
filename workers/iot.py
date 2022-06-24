import utils

class iot_worker:
    def __init__(self):
        utils.log('IOT WORKER STARTED..')

        # LOAD WORKER CONFIG FROM YAML
        config = utils.load_yaml('config.yml')

        # SAVE RELEVANT INFO
        self.config = config.iot
        self.service_channel = config.service.channel

        # CREATE RABBIT INSTANCE & MAKE SERVICE QUERY
        self.rabbit = utils.rabbit_instance()
        self.service_query()

    # START CONNECTION PROCESS
    def service_query(self):

        # CREATE NEW CHANNEL FOR RESPONSE
        response_channel = utils.create_secret()

        # ENCODE DATASET
        message = utils.encode_data({
            'source': self.config.keys.public,
            'payload': {
                'type': 'iot-connect',
                'channel': response_channel
            }
        })

        # PUBLISH MESSAGE & SUBSCRIBE TO RESPONSE CHANNEL
        self.rabbit.publish(self.service_channel, message)
        self.rabbit.consume(response_channel, self.callback)

    # HANDLE INCOMING MESSAGES
    def callback(self, channel, method, properties, body):
        utils.log('RECEIVED MESSAGE')
        print('callback')
        print(body)

# BOOT UP WORKER
utils.launch(iot_worker)