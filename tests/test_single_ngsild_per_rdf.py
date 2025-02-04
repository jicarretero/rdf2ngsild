from unittest import TestCase

from config_translator import ConfigTranslator
from conversor.subject_analysis import SubjectAnalysis
from northbound.build_single_ngsild import BuildSingleNGSILD
from helpers import get_graph, eprint
from northbound.northbound import Northbound


class TestSingleNgsildPerRDF(TestCase):
    def setUp(self):
        self.g = get_graph("examples/simple-sample-relationship.ttl")
        ConfigTranslator("configs/test_config.cfg")

    def test_output_single_ngsild(self):
        ngisld_builder = BuildSingleNGSILD(None)
        sa = SubjectAnalysis(self.g)

        for d in sa:
            ngisld_builder.send(d)

        data = ngisld_builder.data()
        assert(len(data) == 2)
        for d in data:
            assert d['id'] in ('urn:ngsi-ld:addressbook:manuel','urn:ngsi-ld:addressbook:cindy')
        print(ngisld_builder.json_data())
        