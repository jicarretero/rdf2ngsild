#!/usr/bin/env python3

import json
import time

import logging

from helpers import get_graph, encode_url, get_graph_from_message
from conversor.subject_analysis import SubjectAnalysis
from conversor.owl_to_context import Owl2Context
import argparse
from rdflib import Graph
from config_translator import ConfigTranslator
from southbound.kafka_reader import KafkaReader
from southbound.kafka_writer import KafkaWriter
from northbound.orionld import OrionLD, AlreadyExistException, NotExistsException

logger = logging.getLogger(__name__)


def out_subject_analysis_json(sa):
    j_data = []
    for a in sa:
        j_data.append(a)

    print(json.dumps(j_data) if len(j_data) > 1 else json.dumps(j_data[0]))


def out_get_curl(sa):
    for a in sa:
        url = encode_url(a['id'])
        print(f"curl 'http://localhost:1026/ngsi-ld/v1/entities/{url}'")


def out_subject_analysis_curl(sa, print_get=False):
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
    parser = argparse.ArgumentParser(
        description='Converts rdf file to ngsi-ld')

    parser.add_argument('filename', metavar='filename', type=str, nargs='*',
                        help='Filename containg RDF data to be processed')
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
    parser.add_argument('--to-orionld', required=False,
                        action='store_true',
                        help='If this parameter is set, data will be sent to Orion-LD')
    parser.add_argument('--from-kafka', required=False,
                        action='store_true',
                        help='Data intake will be from Kafka servers.')
    parser.add_argument('--to-kafka-demo', required=False,
                        action='store_true',
                        help='Demo writer to send messages to kafka for testing. It needs some files as parameters')

    return parser.parse_args()


def process_file_inputs(args):
    if args.filename is None:
        return

    for filename in args.filename:
        g = get_graph(filename)

        if args.owl:
            display_owl(args, g)
        else:
            display_rdf(args, g, context)


def send_to_orionld(g: Graph) -> None:
    ld = OrionLD.instance()
    sa = SubjectAnalysis(g)
    for data in sa:
        try:
            ld.send(data)
        except (NotExistsException, AlreadyExistException) as e:
            ld.send(data)


def batch_processing_from_kafka(args):
    logger.debug("batch_processing_from_kafka")
    reader = KafkaReader()

    for msg in reader.consume_messages():
        logger.debug("Estoy aqui, consumiendo...")
        g = get_graph_from_message(msg)

        if args.owl:
            display_owl(args, g)
        if args.to_orionld:
            send_to_orionld(g)
        else:
            display_rdf(args, g, context)


def write_to_kafka_files(args):
    if args.filename is None:
        return

    logger.debug("TO KAFKA DEMO - ", args.filename)

    writer = KafkaWriter()
    max_messages = ConfigTranslator().get_interger("kafka-demo", "max_messages_sent")
    sleep_time = ConfigTranslator().get_float(
        "kafka-demo", "wait_between_messages")
    sent = 0

    while max_messages < 0 or sent < max_messages:
        print(sent)
        print(args.filename)
        for filename in args.filename:
            with open(filename, "r") as f:
                data = f.read()
            writer.produce_message(data)
            sent = sent + 1
            if sent > max_messages:
                break
            print(f"... to sleep {sleep_time}")
            time.sleep(sleep_time)


if __name__ == "__main__":
    ConfigTranslator("config.cfg")
    logger.debug(type(OrionLD.instance()))
    logger.debug(type(OrionLD()))

    args = parse_args()
    context = None

    if args.from_kafka:
        batch_processing_from_kafka(args)
    elif args.to_kafka_demo:
        write_to_kafka_files(args)
    else:
        if args.owl_file:
            g = get_graph(args.owl_file)
            context = Owl2Context(g).context()
        process_file_inputs(args)
