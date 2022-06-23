import utils

class create_edge:
    def __init__(self):
        log('EDGE STARTED..')

        self.rabbit = utils.rabbit_instance(['injectors', 'logging'])
        self.rabbit.consume('injectors', self.callback)

    # ON WORK ASSIGNMENT.. 
    def callback(self, channel, method, properties, body):
        print('callback')

# BOOT UP
create_edge()