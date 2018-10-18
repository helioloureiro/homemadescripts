#! /usr/bin/python3

"""
Unit Tests for gpg-signing-tool
"""
import unittest
from mock import MagicMock, Mock
import mockfs


class SigningToolTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_ids(self):
        print("test_get_ids()")
        from gpg_signing_tool import *
        s = SigningTool()
        s.get_ids(key=["abcde", "01234"])


if __name__ == '__main__':
    s = SigningTool()
    s.run()
    unittest.main()
