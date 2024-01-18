import json
from helpers import get_graph, encode_url
from conversor.subject_analysis import SubjectAnalysis
from conversor.owl_to_context import Owl2Context
import argparse
from rdflib import Graph

def out_subject_analysis_json(sa):
    j_data = []
    for a in sa:
        j_data.append(a)

    print(json.dumps(j_data) if len(j_data)>1 else json.dumps(j_data[0]))

def out_get_curl(sa):
    for a in sa:
        url = encode_url(a['id'])
        print(f"curl 'http://localhost:1026/ngsi-ld/v1/entities/{url}'")


def out_subject_analysis_curl(sa, print_get = False):
    for a in sa:
        # print("....... url:", encode_url(a['id']))
        js = json.dumps(a)
        print(f"curl -iX POST 'http://localhost:1026/ngsi-ld/v1/entities/' \
-H 'Content-Type: application/ld+json' \
--data-raw '{js}'")
        if print_get:
            url = encode_url(a['id'])
            print(f"curl 'http://localhost:1026/ngsi-ld/v1/entities/{url}'")


def display_owl(args, g : Graph):
    ctx = Owl2Context(g)
    print(json.dumps(ctx.context()))

def display_rdf(args, g : Graph, context):
    sa = SubjectAnalysis(g)
    sa.add_context(context)
    if args.curl:
        out_subject_analysis_curl(sa, args.get_curl)
    elif args.get_curl:
        out_get_curl(sa)
    else:
        out_subject_analysis_json(sa)


def parse_args():
    parser = argparse.ArgumentParser(description='Converts rdf file to ngsi-ld')

    parser.add_argument('filename', metavar='filename', type=str, nargs='+',
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

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    context = None

    if args.owl_file:
        g = get_graph(args.owl_file)
        context = Owl2Context(g).context()

    for filename in args.filename:
        g = get_graph(filename)

        if args.owl:
            display_owl(args, g)
        else:
            display_rdf(args, g, context)