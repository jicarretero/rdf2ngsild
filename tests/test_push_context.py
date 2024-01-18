import unittest
from helpers import get_graph
from conversor.subject_analysis import SubjectAnalysis
from conversor.owl_to_context import Owl2Context
import json


class TestAddContext(unittest.TestCase):
    def setUp(self) -> None:
        self.o = get_graph("onthologies/ontology-protege.ttl")
        self.g = get_graph("examples/containerlab-graph.nt")
        # self.g = get_graph("examples/simple-sample-relationship.ttl")

    @staticmethod
    def print_curl(j_data):
        print(f"curl -iX POST 'http://localhost:1026/ngsi-ld/v1/entities/' \
     -H 'Content-Type: application/ld+json' \
     --data-raw '{json.dumps(j_data)}'")

    def test_add_context(self):
        context = Owl2Context(self.o)
        t = context.context()
        sa = SubjectAnalysis(self.g)
        sa.add_context(t)

        for a in sa:
            self.print_curl(a)
            # print(json.dumps(a))


if __name__ == "__main__":
    unittest.main()
