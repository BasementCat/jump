import unittest
import os
import sys

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../jump/')

from jump.network import parse_service

class TestNetworkFuncs(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestNetworkFuncs, self).__init__(*args, **kwargs)

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_parse_service(self):
        self.assertEqual(parse_service('0.0.0.0:0'), ('0.0.0.0', 0))
        self.assertEqual(parse_service('127.0.0.1:12'), ('127.0.0.1', 12))
        self.assertEqual(parse_service('8.8.8.8:345'), ('8.8.8.8', 345))
        self.assertEqual(parse_service('10.10.0.1:6789'), ('10.10.0.1', 6789))
        self.assertEqual(parse_service('172.16.0.1:12345'), ('172.16.0.1', 12345))

        self.assertEqual(parse_service('[::]:0'), ('::', 0))
        self.assertEqual(parse_service('[::1]:12'), ('::1', 12))
        self.assertEqual(parse_service('[a::5]:345'), ('a::5', 345))
        self.assertEqual(parse_service('[7:f::8]:6789'), ('7:f::8', 6789))
        self.assertEqual(parse_service('[5:c:d:3::f]:12345'), ('5:c:d:3::f', 12345))
        self.assertEqual(parse_service('[0123:4567:89ab:cdef:0123:4567:89ab:cdef]:80'), ('0123:4567:89ab:cdef:0123:4567:89ab:cdef', 80))

        self.assertIsNone(parse_service('laskdjflkasjd'))
        self.assertIsNone(parse_service('1234.1.2.3:75'))
        self.assertIsNone(parse_service('1.2.3.4'))
        self.assertIsNone(parse_service('3.6.7.3:'))
        self.assertIsNone(parse_service('8.7.6.56:123456'))
        self.assertIsNone(parse_service('1.2.3:4'))

        self.assertIsNone(parse_service('[d::z]:4'))
        self.assertIsNone(parse_service('[a::f]:123456'))
        self.assertIsNone(parse_service('[::]'))
        self.assertIsNone(parse_service('[::]:'))

if __name__ == '__main__':
    unittest.main()