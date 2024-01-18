import unittest
from helpers import get_graph
from conversor.subject_analysis import SubjectAnalysis
from conversor.owl_to_context import Owl2Context


class TestOnthology(unittest.TestCase):
    def setUp(self) -> None:
        self.g = get_graph("onthologies/ontology-protege.ttl")

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
        o2f.context()

if __name__ == '__main__':
    unittest.main()
