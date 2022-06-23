import utils

class service_worker:
    def __init__(self, params={}):
        utils.log('SERVICE STARTED..')

        # LOAD WORKER CONFIG FROM YAML
        self.config = utils.load_yaml('config.yml').service

        # CREATE RABBIT INSTANCE & INIT CHANNELS
        self.rabbit = utils.rabbit_instance(
            self.config.channels
        )

        # SUBSCRIBE TO MESSAGES
        self.rabbit.consume(
            self.config.channels[0],
            self.callback
        )

    # HANDLE INCOMING MESSAGES
    def callback(self, channel, method, properties, body):
        print('callback')
        print(body)

# BOOT UP WORKER
utils.launch(service_worker)