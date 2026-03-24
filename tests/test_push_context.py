import unittest
from helpers import get_graph
from conversor.subject_analysis import SubjectAnalysis
from conversor.owl_to_context import Owl2Context
import json
from config_translator import ConfigTranslator


class TestAddContext(unittest.TestCase):
    def setUp(self) -> None:
        self.o = get_graph("onthologies/ontology-protege.ttl")
        self.g = get_graph("examples/containerlab-graph.nt")
        ConfigTranslator.instance = None
        ConfigTranslator("configs/test_config_nameonly.cfg")
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
            # self.print_curl(a)
            print(json.dumps(a))

    def test_transform_rdf_type(self):
        ids = ['clab-srlinux-openconfig-02-srl2','clab-srlinux-openconfig-02-srl1', 'srl1_e1-1-srl2_e1-1',
               'srlinux-openconfig-02', 'srl1-e1-1', 'srl2-e1-1']
        sa = SubjectAnalysis(self.g)
        for a in sa:
            match a['id']:
                case 'srl1_e1-1-srl2_e1-1':
                    assert a['type'] == 'Link'
                    assert a['connectsNode']['type'] == 'Relationship'
                    assert 'clab-srlinux-openconfig-02-srl1' in a['connectsNode']['object']
                    assert 'clab-srlinux-openconfig-02-srl2' in a['connectsNode']['object']
                    assert a['linkIdentifier']['type'] == 'Property'
                    assert a['linkIdentifier']['value'] == 'srl1_e1-1-srl2_e1-1'
                    print(json.dumps(a))
                case 'srlinux-openconfig-02':
                    assert a['type'] == 'Network'
                case 'clab-srlinux-openconfig-02-srl2':
                    assert a['type'] == 'Node'
                case 'clab-srlinux-openconfig-02-srl1':
                    assert a['type'] == 'Node'
                case 'clab-srlinux-openconfig-02-srl2':
                    assert a['type'] == 'Node'
                case 'srl1-e1-1':
                    assert a['type'] == 'Interface'
                case 'srl2-e1-1':
                    assert a['type'] == 'Interface'
                case other:
                    assert True


if __name__ == "__main__":
    unittest.main()
