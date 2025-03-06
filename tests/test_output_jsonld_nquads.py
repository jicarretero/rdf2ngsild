import unittest

from config_translator import ConfigTranslator
from conversor.subject_analysis import SubjectAnalysis
from helpers import get_graph, get_graph_from_message


class TestJSONLDNQuads(unittest.TestCase):
    def setUp(self):
        ConfigTranslator("configs/test_config_as_with_k8s.cfg")

    def test_load_different_formats(self):
        with open("examples/jsonld-and-nquads/push1.ttl") as f:
            message = f.read()

        g0 = get_graph_from_message(message)
        json_message = g0.serialize(format='json-ld')

        get_graph_from_message(json_message)

        xml_message = g0.serialize(format='xml')
        get_graph_from_message(xml_message)

    def test_load_owl(self):
        with open("examples/containerlab-graph.nt") as f:
            message = f.read()

        get_graph_from_message(message)

    def test_load_jsonld(self):
        with open("examples/jsonld-and-nquads/push1.jsonld") as f:
            message = f.read()
        g0 = get_graph_from_message(message)

    def test_load_ontology(self):
        with open("onthologies/ontology-protege.ttl") as f:
            message = f.read()
        get_graph_from_message(message)


if __name__ == '__main__':
    unittest.main()
