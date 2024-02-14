import unittest
from config_translator import ConfigTranslator
from transformer import transformer

class TestConfigTranslator(unittest.TestCase):
    def test_is_singleton(self):
        o1 = ConfigTranslator("./configs/test_config.cfg")
        o2 = ConfigTranslator("./configs/test_config.cfg")
        print(o1)
        print(o2)
        self.assertIs(o1, o2)

    def test_get_str(self):
        o1 = ConfigTranslator("./configs/test_config.cfg")
        assert(o1.get_string("urn-transform", "urn") ==  "std_urn_name")

    def test_get_a_short_name(self):
        o1 = ConfigTranslator("./configs/test_config.cfg")
        print(transformer("http://example.com/this-space#this-name"))
        assert(transformer("http://example.com/this-space#this-name") ==
               "urn:ngsild:this-space:this-name")


if __name__ == '__main__':
    unittest.main()

