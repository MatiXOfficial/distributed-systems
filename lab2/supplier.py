import pika
import sys
import threading
import time

from utils import EXCHANGE_NAME, ITEMS_DICT


class Supplier:

    def __init__(self, name, items):
        self.name = name
        if ',' in self.name:
            raise ValueError(
                "Cannot use a comma (,) in a name. Type the name again: ")

        self.accepted_items = items.split(',')
        for item in self.accepted_items:
            if item not in ITEMS_DICT:
                raise ValueError(f'Wrong item: {item}')

        self.connection = None
        self.channel = None
        self.order_id = 1
        self.lock = threading.Lock()

    def start(self):
        # connect and declare an exchange
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters('localhost'))
        self.channel = self.connection.channel()

        self.channel.exchange_declare(
            exchange=EXCHANGE_NAME, exchange_type='topic')

        # declare item queues
        for item in self.accepted_items:
            self.channel.queue_declare(queue=item)
            self.channel.queue_bind(
                exchange=EXCHANGE_NAME, queue=item, routing_key=f'sys.item.{item.lower()}')
            self.channel.basic_consume(
                queue=item, auto_ack=False, on_message_callback=self.__receive_order_callback)

        # declare an admin queue
        admin_queue = self.channel.queue_declare(queue='', exclusive=True).method.queue
        self.channel.queue_bind(exchange=EXCHANGE_NAME,
                                queue=admin_queue, routing_key='admin.suppliers')
        self.channel.queue_bind(
            exchange=EXCHANGE_NAME, queue=admin_queue, routing_key='admin')
        self.channel.basic_consume(
            queue=admin_queue, auto_ack=True, on_message_callback=self.__admin_message_callback)

        # self.channel.basic_qos(prefetch_count=1)

        print('Waiting for orders...')
        self.channel.start_consuming()

    def __receive_order_callback(self, ch, method, properties, body):
        team = body.decode()
        item = method.routing_key.split('.')[2]

        # thread safe id incrementing
        self.lock.acquire()
        id = self.order_id
        self.order_id += 1
        self.lock.release()

        print(f'New order (id: {id}): {item} from {team}.')

        # Prepare the order
        time.sleep(ITEMS_DICT[item])

        # publich a confirmation of the delivery
        print(f'Delivered {item} to {team} (order id: {id}).')
        self.channel.basic_publish(
            exchange=EXCHANGE_NAME, routing_key=f'sys.team.{team}', body=f'{id},{item},{self.name}')
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def __admin_message_callback(self, ch, method, properties, body):
        message = body.decode()
        print(f"Received a message from admin: '{message}'")


if __name__ == '__main__':
    try:
        if len(sys.argv) != 3:
            raise ValueError(
                'Wrong number of arguments. Try python supplier.py <name> <items in format: item1,item2,...>')

        supplier = Supplier(sys.argv[1], sys.argv[2])
        supplier.start()
    except ValueError as err:
        print(err)
    except KeyboardInterrupt:
        print('Closed the connection.')
    finally:
        sys.exit()
