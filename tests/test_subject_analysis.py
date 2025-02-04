import unittest
from rdflib import Graph
from conversor.predicates import Predicates
from conversor.subjects import Subject, BNodeFoundException
from config_translator import ConfigTranslator

class TestSubjectAnalysis(unittest.TestCase):

    def __get_graph(self, filename) -> Graph:
        g = Graph()
        with open(filename, "r", encoding='UTF-8') as f:
            g.parse(file=f)
        return g

    def test_predicates_add_value(self):
        g  = self.__get_graph("examples/simple-sample-00.ttl")
        i = 0
        kv = []
        pred_obj = None
        for sub, pred, obj in g:
            print(f"{str(sub)} | {str(pred)} | {str(obj)}")

            if pred_obj is None:
                pred_obj = Predicates(g, pred)
            pred_obj.add_value(obj)
            if i == 0:
                assert pred_obj.value == str(obj)
                kv.append(str(obj))
                i = i + 1
            else:
                assert type(pred_obj.value) is list
                kv.append(str(obj))
                assert kv == pred_obj.value

        assert kv == pred_obj.value

    def test_predicates_bnode_value(self):
        ConfigTranslator("./configs/test_config.cfg")
        g = self.__get_graph("examples/simple-sample-bnode.ttl")
        subjects = {}
        for sub, pred, obj in g:
            s_id = str(sub)
            print(f"{str(sub)} | {str(pred)} | {str(obj)}")
            if s_id not in subjects:
                subjects[s_id] = Subject(g, sub)

            try:
                subjects[s_id].push_data(pred, obj)
            except BNodeFoundException:
                bnode_id = str(obj)
                if bnode_id not in subjects:
                    subjects[bnode_id] = Subject(g, obj)
                subjects[s_id].push_bnode(pred, subjects[bnode_id])

        assert len(subjects.keys()) == 2
        print(subjects.keys())
        assert "http://learningsparql.com/ns/addressbook#i0432" in subjects
        v = subjects["http://learningsparql.com/ns/addressbook#i0432"]
        print(v)
        assert not v.is_bnode
        assert str(v.bnode.subject) in subjects.keys()

        print("-----------------------------------------")
        for k, v in subjects.items():
            if not v.is_bnode:
                for pr_k, pr_v,_ in v:
                    print(pr_k, pr_v)


if __name__ == '__main__':
    unittest.main()
