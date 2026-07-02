import unittest


class MyFailTestCase(unittest.TestCase):
    def test_fail(self):
        assert False
