import argparse
import logging
import os
import time
import urllib.request as urllib
from json import loads
from kafka import KafkaConsumer


def main(args):
    logging.info('brokers={}'.format(args.brokers))
    logging.info('topic={}'.format(args.topic))
    logging.info('creating kafka producer')

    consumer = KafkaConsumer(
            args.topic,
            bootstrap_servers=args.brokers,
            value_deserializer=lambda val: loads(val.decode('utf-8')))
    logging.info('finished creating kafka producer')

    for message in consumer:
        message = message.value
        logging.info('Received URI {}'.format(message))
        logging.info('Downloading Image')
        dl = urllib.urlretrieve(message)

def get_arg(env, default):
    return os.getenv(env) if os.getenv(env, '') is not '' else default


def parse_args(parser):
    args = parser.parse_args()
    args.brokers = get_arg('KAFKA_BROKERS', args.brokers)
    args.topic = get_arg('KAFKA_TOPIC', args.topic)
    return args


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logging.info('starting kafka-python consumer')
    parser = argparse.ArgumentParser(description='consume some stuff on kafka')
    parser.add_argument(
            '--brokers',
            help='The bootstrap servers, env variable KAFKA_BROKERS',
            default='localhost:9092')
    parser.add_argument(
            '--topic',
            help='Topic to read from, env variable KAFKA_TOPIC',
            default='image-uris')
    args = parse_args(parser)
    main(args)
    logging.info('exiting')

