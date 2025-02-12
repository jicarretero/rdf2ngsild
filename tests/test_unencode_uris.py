import unittest

from config_translator import ConfigTranslator
from conversor.subject_analysis import SubjectAnalysis
from helpers import get_graph


class MyTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.o = get_graph("examples/uncode_uris.ttl")

    def test_with_encodetransform_unquote_true(self):
        ConfigTranslator.instance = None
        ConfigTranslator("configs/test_config_no_transform_with_unquote.cfg")

        sa = SubjectAnalysis(self.o)

        for f in sa:
            assert(f['id'] == 'urn:Pilot5:Device:10502070602:EnergyObservation:2024-10-31T11:19:58')
            assert(f['https://saref.etsi.org/core/hasResult']['object'] == 'urn:Pilot5:Device:10502070602:EnergyObservation:2024-10-31T11:19:58:PropertyValue')
            print(f)

    def test_with_encodetransform_unquote_true(self):
        ConfigTranslator.instance = None
        ConfigTranslator("configs/test_config_no_transform.cfg")

        sa = SubjectAnalysis(self.o)

        for f in sa:
            assert(f['id'] == 'urn:Pilot5:Device:10502070602:EnergyObservation:2024-10-31T11%3a19%3a58')
            assert(f['https://saref.etsi.org/core/hasResult']['object'] == 'urn:Pilot5:Device:10502070602:EnergyObservation:2024-10-31T11%3a19%3a58:PropertyValue')
            print(f)
