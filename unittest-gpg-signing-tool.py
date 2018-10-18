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
        from gpg_signing_tool import SigningTool
        import sys
        s = SigningTool()
        print(" * get_id single key via stdin")
        sys.argv = [ "gpg-signing-tool", "EDB0208D" ]
        s.get_ids()
        self.assertTrue(s.keys == ["EDB0208D" ], "Wrong parsed arguments.")

        print(" * get_id duo keys via stdin")
        sys.argv = [ "gpg-signing-tool", "EDB0208D", "FB5972D1" ]
        s.get_ids()
        self.assertTrue(s.keys == ["EDB0208D", "FB5972D1" ], "Wrong parsed arguments.")

        print(" * get_id missing arguments")
        sys.argv = []
        with self.assertRaises(RuntimeError) as error:
            s.get_ids()





if __name__ == '__main__':
    unittest.main()
