from rdflib import Graph
from conversor.subjects import Subject

def get_graph_from_message(message) -> Graph:
    g = Graph()
    g.parse(data=message)
    return g

def get_graph(filename) -> Graph:
    """
    Helper function which opens a RDF file and returns its RDF Graph

    :param filename:
    :return: rdflib.Graph
    """
    g = Graph()
    with open(filename, "r", encoding='UTF-8') as f:
        g.parse(file=f)
    return g


def encode_url(uri_string: str) -> str:
    result = ''
    accepted = [c for c in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-._~'.encode('utf-8')]
    for char in uri_string.encode('utf-8'):
        result += chr(char) if char in accepted else '%{}'.format(hex(char)[2:]).upper()
    return result


def apply_filters(subject: Subject, filter: set) -> bool:
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

