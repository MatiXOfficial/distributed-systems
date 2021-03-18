import pika
import sys
import threading

from utils import EXCHANGE_NAME


class Admin:

    def __init__(self):
        self.connection = None
        self.channel = None

    def start(self):
        # connect and declare an exchange
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters('localhost'))
        self.channel = self.connection.channel()

        self.channel.exchange_declare(
            exchange=EXCHANGE_NAME, exchange_type='topic')

        # admin queue
        admin_queue = self.channel.queue_declare(queue='', exclusive=True).method.queue
        self.channel.queue_bind(
            exchange=EXCHANGE_NAME, queue=admin_queue, routing_key=f'sys.#')
        self.channel.basic_consume(
            queue=admin_queue, auto_ack=True, on_message_callback=self.__message_callback)

        # listening thread
        threading.Thread(
            target=lambda: self.channel.start_consuming(), daemon=True).start()

        print('Welcome! Press CTRL+C to exit.')
        print('Types of messages: T - to all the teams, S - to all the suppliers, \
A - to all the teams and suppliers')

        while True:
            print('Type the message type and then the message.')

            # choose the type
            type = input()
            if type == 'T':
                key = 'admin.teams'
                name = 'all the teams'
            elif type == 'S':
                key = 'admin.suppliers'
                name = 'all the suppliers'
            elif type == 'A':
                key = 'admin'
                name = 'all the teams and suppliers'
            else:
                print('Wrong message type. Use T, S or A.')
                continue

            # send the message
            message = input()
            self.channel.basic_publish(
                exchange=EXCHANGE_NAME, routing_key=key, body=message)
            print(f"Sent '{message}' to {name}.")

    @staticmethod
    def __message_callback(ch, method, properties, body):
        # sys.team.<name> or sys.item.<item name>
        topic = method.routing_key.split('.')

        if topic[1] == 'item':      # team made an order
            team = body.decode()
            item = topic[2]

            print(f'{team} made an order for {item}.')

        elif topic[1] == 'team':    # delivery confirmation
            team = topic[2]

            meta = body.decode().split(',')
            id = meta[0]
            item = meta[1]
            supplier = meta[2]

            print(
                f'{supplier} confirms the delivery of {item} to {team} (order id: {id}).')


if __name__ == '__main__':
    try:
        admin = Admin()
        admin.start()
    except KeyboardInterrupt:
        print('Closed the connection.')
        sys.exit()
