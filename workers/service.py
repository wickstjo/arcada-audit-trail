import utils

class service_worker:
    def __init__(self):
        utils.log('SERVICE WORKER STARTED..')

        # LOAD WORKER CONFIG FROM YAML
        self.config = utils.load_yaml('config.yml').service

        # CREATE RABBIT INSTANCE
        self.rabbit = utils.rabbit_instance()

        # SUBSCRIBE TO MESSAGES
        self.rabbit.consume(
            self.config.channel,
            self.callback
        )

    # HANDLE INCOMING MESSAGES
    def callback(self, channel, method, properties, body):
        decoded = utils.decode_data(body)
        utils.log('RECEIVED MESSAGE')

        # IF THE BODY CAN BE DECODED
        if (decoded):
            print(decoded)

            # TODO: DECRYPT PAYLOAD
            # TODO: CHECK STATE FOR SOURCE CONNECTION

        
        # OTHERWISE, PRINT ERROR
        else:
            utils.log('COULD NOT DECIPHER PAYLOAD')

# BOOT UP WORKER
utils.launch(service_worker)