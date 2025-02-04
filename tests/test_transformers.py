import json
import unittest
from config_translator import ConfigTranslator
from conversor.subject_analysis import SubjectAnalysis
from helpers import get_graph, eprint

class TestTransformer(unittest.TestCase):
    def setUp(self) -> None:
        self.o = get_graph("examples/simple-sample-test-expansions.ttl")

    def get_data_from_analysis(self, sa: SubjectAnalysis):
        j_data = []
        for a in sa:
            j_data.append(a)
        print(json.dumps(j_data) if len(j_data) > 1 else json.dumps(j_data[0]))
        return j_data


    def testAllLongNames(self):
        ConfigTranslator.instance = None
        ConfigTranslator("configs/test_config_no_transform.cfg")
        sa = SubjectAnalysis(self.o)

        j_data = self.get_data_from_analysis(sa)

        assert(j_data[0]['id'] == "https://example.org/DP101")
        assert(j_data[0]['type'] == "https://w3id.org/aerOS/data-catalog#DataProduct")
        assert('http://www.w3.org/ns/dcat#distribution' in j_data[0])
        assert('http://purl.org/dc/terms/identifier' in j_data[0])
        assert('https://w3id.org/aerOS/data-catalog#mapping' in j_data[0])
        assert('http://purl.org/dc/terms/description' in j_data[0])
        assert('http://www.w3.org/ns/dcat#keyword' in j_data[0])
        assert('http://www.w3.org/ns/dcat#theme' in j_data[0])

    def testPrefixedNames(self):
        ConfigTranslator.instance = None
        ConfigTranslator("configs/test_config_transform_only_predictes_prefix.cfg")

        j_data = self.get_data_from_analysis(SubjectAnalysis(self.o))

        assert(j_data[0]['id'] == "https://example.org/DP101")
        assert(j_data[0]['type'] == "https://w3id.org/aerOS/data-catalog#DataProduct")
        assert('dcterms:publisher' in j_data[0])
        assert('dcterms:description' in j_data[0])
        assert('dcat:keyword' in j_data[0])
        assert('dcat:theme' in j_data[0])
        assert('dcterms:identifier' in j_data[0])
        # assert('aerdcat:mapping' in j_data[0]) -- ns2???