import functools
import json
import sys
from rdflib import Graph

from conversor.subjects import Subject
import xml.etree.ElementTree as ET

@functools.cache
def is_json(myjson):
    try:
        json.loads(myjson)
    except ValueError:
        return False
    return True

@functools.cache
def is_xml(myxml):
    try:
        ET.fromstring(myxml)
    except ET.ParseError:
        return False
    return True


@functools.cache
def get_graph_from_message(message) -> Graph:
    """
    Given a message in a String, this function will return a Graph parsing the message. It will be used to read data
    from Kakfa.

    :param message: message to be parsed as RDF
    :return: Graph representation of the RDF input data.
    """
    g = Graph()
    try:
        g.parse(data=message)
    except Exception as e:
        if is_json(message):
            g.parse(data=message, format="json-ld")
        elif is_xml(message):
            g.parse(data=message, format="xml")
        else:
            raise e

    # Skolemize graph to transform BNodes into URIRef
    skol_g = g.skolemize()
    return skol_g


def get_graph(filename) -> Graph:
    """
    Helper function which opens a RDF file and returns its RDF Graph

    :param filename:
    :return: rdflib.Graph
    """
    g = Graph()
    with open(filename, "r", encoding='UTF-8') as f:
        g.parse(file=f)
    # Skolemize graph to transform BNodes into URIRef
    skol_g = g.skolemize()
    return skol_g

def encode_url(uri_string: str) -> str:
    """
    This function will provide an URL properly encoded to be sent as a paramater in the HTTP repests.

    :param uri_string:
    :return:
    """
    result = ''
    accepted = [c for c in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-._~'.encode('utf-8')]
    for char in uri_string.encode('utf-8'):
        result += chr(char) if char in accepted else '%{}'.format(hex(char)[2:]).upper()
    return result

def apply_filters(subject: Subject, filter: set) -> bool:
    """
    Whis function will filter a Subject according to a set of conditions.

    :param subject:
    :param filter:
    :return: boolean - Whether if it is valid or not.
    """
    if filter is None:
        return True
    r = True
    if len(filter) > 0:
        for f in filter:
            prefix = subject.prefix
            r = r and eval(f)
            if not r:
                break
    return r

def eprint(*args, **kwargs):
    """
    Prints message (same as print) to stderr.

    :param args:
    :param kwargs:
    :return:
    """
    print(*args, file=sys.stderr, **kwargs)