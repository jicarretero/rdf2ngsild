import json
import unittest
from config_translator import ConfigTranslator
from conversor.subject_analysis import SubjectAnalysis
from helpers import get_graph, eprint

class TestGeoproperty(unittest.TestCase):
    def setUp(self) -> None:
        self.o = get_graph("examples/car_annotation_output.ttl")

    def testGeoproperty(self):
        ConfigTranslator.instance = None
        ConfigTranslator("configs/test_config_nameonly.cfg")

        sa = SubjectAnalysis(self.o)
        i = 0
        for a in sa:
            assert("location" in a)
            data = a["location"]

            assert data["type"] == "GeoProperty"
            assert data["value"]["type"] == "Point"
            assert "coordinates" in data["value"]

        print(a)

