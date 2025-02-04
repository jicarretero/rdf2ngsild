import unittest
from helpers import get_graph
from conversor.subject_analysis import SubjectAnalysis
from conversor.owl_to_context import Owl2Context
import os.path
from config_translator import ConfigTranslator

class TestOnthology(unittest.TestCase):
    def setUp(self) -> None:
        dir_path = os.path.dirname(os.path.realpath(__file__))
        ConfigTranslator(f"{dir_path}/configs/test_config_nameonly.cfg")
        self.g = get_graph(f"{dir_path}/onthologies/ontology-protege.ttl")

    def do_things_for(self):
        g = self.g
        o2c = Owl2Context(g)

    def test_onthology_protege(self):
        sa = SubjectAnalysis(self.g)
        assert(sa)

    def test_create_class_speed(self):
        import timeit
        print(timeit.timeit(self.do_things_for, number=1500))

    def test_context(self):
        o2f = Owl2Context(self.g)
        res = o2f.context()
        print(res)

if __name__ == '__main__':
    unittest.main()
