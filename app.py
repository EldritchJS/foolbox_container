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
from PIL import Image
import requests
from io import BytesIO

def main(args):
    logging.info('model={}'.format(args.model))
    model = zoo.get_model(url=args.model)
    logging.info('finished acquiring model')

    logging.info('creating attack {}'.format(args.attack))
    attack = foolbox.attacks.FGSM(model)
    logging.info('finished creating attack')

    logging.info('brokers={}'.format(args.brokers))
    logging.info('topic={}'.format(args.topic))
    logging.info('creating kafka consumer')
    consumer = KafkaConsumer(
            args.topic,
            bootstrap_servers=args.brokers,
            value_deserializer=lambda val: loads(val.decode('utf-8')))
    logging.info('finished creating kafka consumer')

    while True:
        for message in consumer:
            image_uri = message.value['url']
            label = message.value['label']
            logging.info('received URI {}'.format(image_uri))
            logging.info('received label {}'.format(label))
            logging.info('downloading image')
            response = requests.get(image_uri)
            img = Image.open(BytesIO(response.content))
            image = np.array(img.getdata()).reshape(img.size[0], img.size[1], 3)
            logging.info('downloaded image')
            images = np.ndarray(shape=(2,32,32,3), dtype=np.float32)
            images[0] = image
            adversarial = attack(image, label)
            images[1] = adversarial
            preds = model.forward(images)
            orig_inf = np.argmax(preds[0])
            adv_inf = np.argmax(preds[1])
            logging.info('original inference: {}  adversarial inference: {}'.format(orig_inf, adv_inf))

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
            default='kafka:9092')
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
            default='https://github.com/EldritchJS/cifar10_challenge')
    args = parse_args(parser)
    main(args)
    logging.info('exiting')

