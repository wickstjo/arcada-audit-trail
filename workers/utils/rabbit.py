import pika
from utils.misc import log

class create_instance:
    def __init__(self):

        # ESTABLISH CONNECTION
        rabbitmq = pika.BlockingConnection(pika.ConnectionParameters(
            host='localhost',
            heartbeat=0
        ))

        # ATTACH MQ CHANNEL
        self.channel = rabbitmq.channel()

    # CONSUME CHANNEL EVENTS
    def consume(self, channel, callback):

        # INITIALIZE THE CHANNEL
        self.channel.queue_declare(queue=channel)
        
        # SETUP CALLBACK & SAVE CONSUMER TAG FOR LATER
        self.consumer_tag = self.channel.basic_consume(
            queue=channel,
            on_message_callback=callback,
            auto_ack=True
        )

        # SUBSCRIBE TO TOPIC
        self.channel.start_consuming()

    # PUBLISH CHANNEL EVENT
    def publish(self, channel, payload):
        self.channel.basic_publish(
            exchange='',
            routing_key=channel,
            body=payload
        )
        
    def unsub(self, channel):
        # print(self.channel.consumer_tags)
        self.channel.basic_cancel(self.consumer_tag)