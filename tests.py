import unittest
import urllib

from repache import Repache

class TestRepache(unittest.TestCase):

    def setUp(self):
        self.repache_instance = Repache('')

    def test_parse_apache_log(self):
        self.repache_instance.parse_log()
        self.assertTrue(self.repache_instance.log_data[0].has_key('uri'))

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()

