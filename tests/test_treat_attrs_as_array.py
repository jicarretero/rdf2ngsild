import unittest

from config_translator import ConfigTranslator
from conversor.subject_analysis import SubjectAnalysis
from helpers import get_graph


class TestAttributesAsArrays(unittest.TestCase):
    def setUp(self):
        self.o = get_graph("examples/simple-sample-relationship.ttl")

    def test_configuration(self):
        ConfigTranslator.instance = None
        cfg = ConfigTranslator("configs/test_attrs_as_array.cfg")

        l = cfg.get_list("treat-as-array", "attributes")

        expected = {"http://learningsparql.com/ns/addressbook#email",
                    "http://learningsparql.com/ns/addressbook#homeTel"}
        assert l == expected

    def test_interpreted_as_array(self):
        ConfigTranslator.instance = None
        cfg = ConfigTranslator("configs/test_attrs_as_array.cfg")

        sa = SubjectAnalysis(self.o)

        for f in sa:
            print(f)
            assert type(f['http://learningsparql.com/ns/addressbook#email']['value']) is list
            assert type(f['http://learningsparql.com/ns/addressbook#homeTel']['value']) is list
            assert type(f['http://learningsparql.com/ns/addressbook#jobName']['value']) is not list


if __name__ == '__main__':
    unittest.main()
