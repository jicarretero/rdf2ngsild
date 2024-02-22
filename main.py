#!/usr/bin/env python3

import json
import time

from itertools import count, cycle, product
import argparse
import asyncio
from multiprocessing import Pool
import logging
from rdflib import Graph
from helpers import get_graph, encode_url, get_graph_from_message
from conversor.subject_analysis import SubjectAnalysis
from conversor.owl_to_context import Owl2Context
from config_translator import ConfigTranslator
from southbound.kafka_reader import KafkaReader
from southbound.kafka_writer import KafkaWriter
from northbound.northbound import Northbound

logging.basicConfig(filename="/tmp/logfile.log",
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.ERROR)

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)


def out_subject_analysis_json(sa: SubjectAnalysis):
    """
    Outputs the json data produced by a SubjectAnalysis

    :param sa: SubjectAnalysis to transvers and show the result in terminal
    :return:
    """
    j_data = []
    for a in sa:
        j_data.append(a)

    print(json.dumps(j_data) if len(j_data) > 1 else json.dumps(j_data[0]))


def out_get_curl(sa: SubjectAnalysis):
    """
    Outputs the json data produced y a SubjectAnalysis in the format of "curl" commands which can be
    used later to test against the ngsi-ld broker

    :param sa:  SubjectAnalysis to transvers and show the result in terminal
    :return:
    """
    for a in sa:
        url = encode_url(a['id'])
        print(f"curl 'http://localhost:1026/ngsi-ld/v1/entities/{url}'")


def out_subject_analysis_curl(sa: SubjectAnalysis, print_get=False):
    """
    Outputs a commodity format in the form of "curl" string which could be useful to copy/paste it
    and run it on the terminal. Just for testing purposes.
    """
    for a in sa:
        # print("....... url:", encode_url(a['id']))
        js = json.dumps(a)
        print(f"curl -iX POST 'http://localhost:1026/ngsi-ld/v1/entities/' \
-H 'Content-Type: application/ld+json' \
--data-raw '{js}'")
        if print_get:
            url = encode_url(a['id'])
            print(f"curl 'http://localhost:1026/ngsi-ld/v1/entities/{url}'")


def display_owl(args, g: Graph):
    ctx = Owl2Context(g)
    logger.debug(json.dumps(ctx.context()))


def display_rdf(args, g: Graph, context):
    sa = SubjectAnalysis(g)
    sa.add_context(context)
    if args.curl:
        out_subject_analysis_curl(sa, args.get_curl)
    elif args.get_curl:
        out_get_curl(sa)
    else:
        out_subject_analysis_json(sa)


def parse_args():
    """
    Function which defines the arguments to be parsed in this case.
    """
    parser = argparse.ArgumentParser(
        description='Converts rdf file to ngsi-ld')

    parser.add_argument('filename', metavar='filename', type=str, nargs='*',
                        help='Filename containg RDF data to be processed')
    parser.add_argument('--print', required=False,
                        action='store_true',
                        help='Outputs json data')  # on/off flag
    parser.add_argument('--curl', required=False,
                        action='store_true',
                        help='Outputs as CURL commands, not json')  # on/off flag
    parser.add_argument('--get-curl', required=False,
                        action='store_true',
                        help='Outputs as CURL commands, not json')  # on/off flag
    parser.add_argument('--owl', required=False,
                        action='store_true',
                        help='Input is a onthology file. The input is treated as an onthology')
    parser.add_argument('--owl-file', required=False, type=str,
                        help='Add an onthology file as context to the output of json-ld')
    parser.add_argument('--to-ngsild-broker', required=False,
                        action='store_true',
                        help='If this parameter is set, data will be sent to NGSI-LD Broker')
    parser.add_argument('--to-null', required=False,
                        action='store_true',
                        help='If this parameter is set, data will be "discarded" after processing it')
    parser.add_argument('--from-kafka', required=False,
                        action='store_true',
                        help='Data intake will be from Kafka servers.')
    parser.add_argument('--feed-kafka-demo', required=False,
                        action='store_true',
                        help='Demo writer to send messages to kafka for testing. It needs some files as parameters')
    parser.add_argument('--benchmark', required=False,
                        action='store_true',
                        help='This benchmark will read from Kaka at most (from config file) kafka-demo.max_messages_sent')
    parser.add_argument('--async-run', required=False,
                        action='store_true',
                        help='Run the processing of messages in asyncronous mode to increase performance')

    return parser.parse_args()


def process_file_inputs(args):
    if args.filename is None:
        return

    for filename in args.filename:
        g = get_graph(filename)
        context = None

        if args.owl:
            display_owl(args, g)
        else:
            display_rdf(args, g, context)


def send(g: Graph):
    """
    Sends a message to the Northbound.

    :param g:
    :return:
    """
    nb = Northbound()
    sa = SubjectAnalysis(g)
    for data in sa:
        nb.send(data)


def use_graph(msg):
    """
    Gets the RDF Graph from the message received in Kafka and sends it.

    :param msg:
    :return:
    """
    g = get_graph_from_message(msg)
    send(g)


def thr_processing_from_kafka(args):
    """
    Writing to kafka the messages read in the KafkaReader. It spawns some processes to do the processing
    of the messages read.

    :param args:
    :return:
    """
    logger.debug("batch_processing_from_kafka")
    print("batch-process!")
    reader = KafkaReader()
    reader.is_benchmark = args.benchmark
    pool_size = ConfigTranslator().get_interger("brokerld", "pool_size")
    if pool_size == 0:
        pool_size = 1

    try:
        with Pool(pool_size) as p:
            for m in p.imap_unordered(use_graph, reader.consume_messages()):
                pass
    except Exception as e:
        print(e)


def batch_processing_from_kafka(args):
    """
    Secuential writing to Kafka - Really slow and should not be used.

    :param args:
    :return:
    """
    logger.debug("batch_processing_from_kafka")
    reader = KafkaReader()

    kafka_demo = args.benchmark
    max_nread = ConfigTranslator().get_interger("kafka-demo", "max_messages_sent")

    for n_read, msg in enumerate(reader.consume_messages()):
        use_graph(msg)

        if kafka_demo and n_read >= max_nread:
            break


def iterate_on(base_iterator, name_array):
    """
    Iterates on base iterator and yields the counter iterator and a value of the array. When the base_iterator
    is over, the function exits. It yields a value of the array after another and starts in the beginning once
    reached the last element

    :param base_iterator:
    :param name_array:
    :return:
    """
    l = len(name_array)
    for j in base_iterator:
        yield j, name_array[j % l]


def write_to_kafka_files(args):
    if args.filename is None:
        return

    logger.debug("TO KAFKA DEMO - ")

    writer = KafkaWriter()
    max_messages = ConfigTranslator().get_interger("kafka-demo", "max_messages_sent")
    sleep_time = ConfigTranslator().get_float(
        "kafka-demo", "wait_between_messages")

    # cond_out is a number of elements (max_messages) or a counter forever.
    cond_out = range(max_messages) if max_messages >= 0 else count(
        start=0, step=1)

    for sent, filename in iterate_on(cond_out, args.filename):
        print(sent, filename)
        with open(filename, "r", encoding='UTF-8') as f:
            data = f.read()
        writer.produce_message(data)
        if sleep_time > 0:
            logger.debug("simulator sleeping... %d", (sleep_time))
            time.sleep(sleep_time)


def main():
    args = parse_args()
    context = None
    Northbound(args)

    start = time.time()
    if args.from_kafka:
        if args.async_run:
            thr_processing_from_kafka(args)
        else:
            batch_processing_from_kafka(args)
    elif args.feed_kafka_demo:
        write_to_kafka_files(args)
    else:
        if args.owl_file:
            g = get_graph(args.owl_file)
            context = Owl2Context(g).context()
        process_file_inputs(args)
    end = time.time()
    if args.benchmark:
        print()
        print(f"TIME: {end - start}")


if __name__ == "__main__":
    ConfigTranslator("config.cfg")
    main()
