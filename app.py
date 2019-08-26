import argparse
import logging
import os
import time
import urllib.request as urllib
from json import loads
from kafka import KafkaConsumer
import foolbox
import numpy as np
from foolbox import zoo

def main(args):
    logging.info('brokers={}'.format(args.brokers))
    logging.info('topic={}'.format(args.topic))
    logging.info('creating kafka producer')
    consumer = KafkaConsumer(
            args.topic,
            bootstrap_servers=args.brokers,
            value_deserializer=lambda val: loads(val.decode('utf-8')))
    logging.info('finished creating kafka producer')

    logging.info('model={}'.format(args.model))
    model = zoo.get_model(url=args.model)
    logging.info('finished acquiring model')

    logging.info('creating attack {}'.format(args.attack))
    attack = foolbox.attacks.FGSM(model)
    logging.info('finished creating attack')
    
    for message in consumer:
        message = message.value
        logging.info('received URI {}'.format(message))
        logging.info('downloading image')
        dl = urllib.urlretrieve(message)
        logging.info('downloaded image')
        adversarial = attack(image[:,:,::-1], label

def get_arg(env, default):
    return os.getenv(env) if os.getenv(env, '') is not '' else default


def parse_args(parser):
    args = parser.parse_args()
    args.brokers = get_arg('KAFKA_BROKERS', args.brokers)
    args.topic = get_arg('KAFKA_TOPIC', args.topic)
    args.attack = get_arg('ATTACK', args.attack)
    args.model = get_arg('MODEL_URI', args.model)
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
            default='images')
    parser.add_argument(
            '--attack',
            help='Attack type, env variable ATTACK',
            default='FGSM')
    parser.add_argument(
            '--model',
            help='Foolbox zoo model uri MODEL_URI',
            default='https://github.com/EldritchJS/mnist_challenge')
    args = parse_args(parser)
    main(args)
    logging.info('exiting')

