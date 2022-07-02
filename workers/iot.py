from utils.worker import skeleton, launch
from utils.misc import log, create_secret, sleep, wrapper, timestamp
import random

class iot_worker(skeleton):
    def created(self):
        
        # INITIALIZE LOGGER
        self.init_logger('iot', self.config.iot)

        # WHITELISTED CALLBACK ACTIONS
        self.actions = {
            'handshake_response': self.handshake_response,
        }

        # RUN SERVICE QUERY & SUBSCRIBE TO IOT CHANNEL
        self.service_handshake()
        self.subscribe(self.config.iot.keys.public)

    # START CONNECTION PROCESS
    def service_handshake(self):

        # CREATE ID FOR REQUEST
        request_id = create_secret(6)

        self.publish(self.config.service.keys.public, {
            'source': self.config.iot.keys.public,
            'payload': {
                'action': 'iot_handshake',
                'location': self.config.iot.location.raw(),
                'secret': request_id,
            }
        })

        # STORE REQUEST ID FOR VERIFICATION
        self.requests[request_id] = wrapper({
            'source': self.config.service.keys.public,
            'timestamp': timestamp(),
        })

    # FIND EDGE RESPONSE
    def handshake_response(self, data):
        turnaround = self.validate_secret(data)

        # VALIDATION FAILED
        if not turnaround:
            return

        # MAKE SURE THE SENDER IS THE SERVICE
        if data.source != self.config.service.keys.public:
            return self.log({
                'message': 'Handshake response from non-service channel blocked',
                'caller': data.source
            })

        # SOMETHING WENT WRONG
        if not data.payload.success:
            return self.log({
                'message': 'Handshake process could not be completed',
                'reason': data.payload.reason,
                'turnaround': turnaround,
            })

        # OTHERWISE, SAVE EDGE DEVICE IN STATE
        self.edge_device = data.payload.edge

        # LOG SUCCESS
        self.log({
            'message': 'Handshake process completed',
            'edge': data.payload.edge,
            'turnaround': turnaround,
        })
        print()

        # DUMP TESTLOGS WITH INTERVAL X TIMES
        for _ in range(10):
            sleep(2)
            self.dump_logs()

    # DUMP LOGS
    def dump_logs(self):
        # rows = random.randint(3, 30)
        rows = 20

        # SEND LOGS
        self.publish(self.edge_device, {
            'source': self.config.iot.keys.public,
            'payload': {
                'action': 'log_dump',
                'logs': [create_secret(5) for x in range(rows)]
            }
        })

        # LOG MSG
        self.log({
            'message': 'Submitted log batch to edge',
            'edge': self.edge_device,
            'rows': rows,
        })

        print()

# BOOT UP WORKER
launch(iot_worker)