import pika
import sys
import threading

from utils import EXCHANGE_NAME, ITEMS_DICT


class Team:

    def __init__(self, name):
        self.connection = None
        self.channel = None
        self.name = name

    def start(self):
        # connect and declare an exchange
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters('localhost'))
        self.channel = self.connection.channel()

        self.channel.exchange_declare(
            exchange=EXCHANGE_NAME, exchange_type='topic')

        # declare a queue for confirmations and admin messages
        team_queue = self.channel.queue_declare(queue='', exclusive=True).method.queue
        self.channel.queue_bind(
            exchange=EXCHANGE_NAME, queue=team_queue, routing_key=f'sys.team.{self.name}')
        self.channel.queue_bind(
            exchange=EXCHANGE_NAME, queue=team_queue, routing_key='admin.teams')
        self.channel.queue_bind(
            exchange=EXCHANGE_NAME, queue=team_queue, routing_key='admin')
        self.channel.basic_consume(
            queue=team_queue, auto_ack=True, on_message_callback=self.__message_callback)

        # listening thread
        threading.Thread(
            target=lambda: self.channel.start_consuming(), daemon=True).start()

        print('Welcome! Press CTRL+C to exit. What would you like to order?')

        # read and publish orders
        while True:
            item = input()
            if item not in ITEMS_DICT:
                print(f'Wrong item: {item}. Try again.')
                continue

            self.channel.basic_publish(
                exchange=EXCHANGE_NAME, routing_key=f'sys.item.{item.lower()}', body=self.name)
            print(f'Ordered: {item}. What would you like to order now?')

    def close(self):
        self.connection.close()

    @staticmethod
    def __message_callback(ch, method, properties, body):
        if method.routing_key[:3] == 'sys':     # delivery confirmation
            meta = body.decode().split(',')
            id = meta[0]
            item = meta[1]
            supplier = meta[2]

            print(f'Received {item} from {supplier} (order id: {id}).')

        else:   # message from admin
            message = body.decode()
            print(f"Received a message from admin: '{message}'")


if __name__ == '__main__':
    try:
        if len(sys.argv) != 2:
            raise ValueError(
                'Wrong number of arguments. Try python team.py <name>')
        team = Team(sys.argv[1])
        team.start()
    except ValueError as err:
        print(err)
    except KeyboardInterrupt:
        team.close()
        print('Closed the connection.')
    finally:
        sys.exit()
