import utils

class edge_worker:
    def __init__(self):
        utils.log('EDGE WORKER STARTED..')

        # LOAD WORKER CONFIG FROM YAML
        self.config = utils.load_yaml('config.yml').edge

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
utils.launch(edge_worker)