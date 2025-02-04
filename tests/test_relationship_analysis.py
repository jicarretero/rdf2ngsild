import unittest
from conversor.subject_analysis import SubjectAnalysis
from conversor.subjects import Subject
from conversor.predicates import Predicates
from helpers import get_graph
import json
import os
from config_translator import ConfigTranslator

class TestRelationships(unittest.TestCase):
    def setUp(self) -> None:
        dir_path = os.path.dirname(os.path.realpath(__file__))
        ConfigTranslator(f"{dir_path}/configs/test_config_nameonly.cfg")
    def test_simple_relationship(self):
        g = get_graph("examples/simple-sample-relationship.ttl")
        sa = SubjectAnalysis(g)
        assert(len(sa.subjects) == 2)

        subject_cindy = sa.subjects.get('http://learningsparql.com/ns/addressbook#cindy')
        subject_manuel = sa.subjects.get('http://learningsparql.com/ns/addressbook#manuel')

        assert(subject_cindy is not None and type(subject_cindy) is Subject)
        assert(subject_manuel is not None and type(subject_manuel) is Subject)

        assert(subject_cindy.short_name == 'cindy')
        assert(subject_manuel.short_name == 'manuel')

        predicates = subject_manuel.predicates.get('http://learningsparql.com/ns/addressbook#isbossof')
        assert(predicates is not None and type(predicates) is Predicates)
        assert(predicates.isreference)
        assert(predicates.value == subject_cindy.short_name)


if __name__ == '__main__':
    unittest.main()
