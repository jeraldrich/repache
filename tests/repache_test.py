import unittest
import urllib
import argparse

from ..repache import Repache
from .. import mimetype_matches


class TestRepache(unittest.TestCase):

    def setUp(self):
        """
        Initialize repache instance
        """
        parser = argparse.ArgumentParser()
        parser.add_argument('-f', '--filename', dest='filename_opt',
                            default='access.log',
                            help="path to apache access log file")
        parser.add_argument('-u', '--uri', dest='uri_opt',
                            default='http://127.0.0.1/',
                            help="base uri to send requests to EXAMPLE: \
                            http://localhost/")
        parser.add_argument('-m', '--mimetype', dest='mimetype_opt',
                            default='', help="filter access log for mimetype")
        args = parser.parse_args()
        self.repache_instance = Repache(args)

    def test_parse_apache_access_log(self):
        """
        parse log file and populate self.log_data
        """
        self.repache_instance.parse_log()
        self.assertTrue(self.repache_instance.log_data)
        self.assertTrue('uri' in self.repache_instance.log_data[0])

    def test_parse_mimetypes(self):
        """
        Check that all mimetypes in mimetype_matches are matched in log file
        """
        mimetypes_matched = {}
        for mimetype in mimetype_matches.matches.keys():
            mimetypes_matched[mimetype] = False
        for line_data in self.repache_instance.log_data:
            if line_data['mimetype'] in mimetypes_matched:
                mimetypes_matched[mimetype] = True
        all_mimetypes_matched = True
        for mimetype, matched in mimetypes_matched.items():
            if not matched:
                all_mimetypes_matched = False
        self.assertTrue(all_mimetypes_matched, mimetypes_matched)


if __name__ == '__main__':
    unittest.main()
