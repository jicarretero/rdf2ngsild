import unittest
from config_translator import ConfigTranslator
from transformer import transformer
import os

class TestConfigTranslator(unittest.TestCase):

    def test_is_singleton(self):
        ConfigTranslator.instance = None
        o1 = ConfigTranslator("./configs/test_config.cfg")
        o2 = ConfigTranslator("./configs/test_config.cfg")
        print(o1)
        print(o2)
        self.assertIs(o1, o2)

    def test_get_str(self):
        ConfigTranslator.instance = None
        o1 = ConfigTranslator("./configs/test_config.cfg")
        assert(o1.get_string("urn-transform", "urn") == "std_urn_name")

    def test_get_a_short_name(self):
        ConfigTranslator.instance = None
        o1 = ConfigTranslator("./configs/test_config.cfg")
        t = transformer("http://example.com/this-space#this-name")
        print(t)
        assert(t == "urn:ngsi-ld:this-space:this-name")

    def tests_get_a_name_only(self):
        ConfigTranslator.instance = None
        o1 = ConfigTranslator("./configs/test_config_nameonly.cfg")
        t = transformer("http://example.com/this-space#this-name")
        assert(t == "this-name")
    def tests_get_not_transformed(self):
        ConfigTranslator.instance = None
        o1 = ConfigTranslator("./configs/test_config_no_transform.cfg")
        t = transformer("http://example.com/this-space#this-name")
        assert(t == "http://example.com/this-space#this-name")

if __name__ == '__main__':
    unittest.main()

