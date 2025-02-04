import json
import unittest
from config_translator import ConfigTranslator
from conversor.subject_analysis import SubjectAnalysis
from helpers import get_graph, eprint
from transformer import transformer


class TestExpandNames(unittest.TestCase):
    def setUp(self) -> None:
        self.o = get_graph("examples/example-to-expand-names-nacho.ttl")
        ConfigTranslator("configs/test_config_no_transform.cfg")

    def test_expand_expanded(self):
        ngsild_result = {}
        ngsild_dict = {}

        with open("examples/result-expanded-names/example-expanded.json") as f:
            ngsild_result = json.load(f)

        for a in ngsild_result:
            ngsild_dict[a['id']] = a

        sa = SubjectAnalysis(self.o)

        for elem in sa:
            try:
                ngsild_id = elem['id']
                v = ngsild_dict[ngsild_id]
                print(f"{elem}")
                print(f"{v}")
                assert(elem['id'] == v['id'])
                assert(elem['type'] == v['type'])
            except KeyError:
                eprint(f"id {ngsild_id} not found in example-expanded.json fine")