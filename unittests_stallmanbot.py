#! /usr/bin/python3

import unittest
from mock import MagicMock
import mockfs


class StallmanBot(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_error(self):
        print("Testing error()")
        from stallmanbot import error
        import syslog

        debug = MagicMock()
        syslog.openlog = MagicMock()
        syslog.syslog = MagicMock()

        print(" * ASCII")
        message = "testing"
        error(message)
        syslog.openlog.assert_called_with("StallNoMan")
        syslog.syslog.assert_called_with(syslog.LOG_ERR,
                                         "ERROR: %s" % message)

        print(" * UTF-8")
        message = "tésting ç å üt°f-8"
        error(message)
        syslog.openlog.assert_called_with("StallNoMan")
        syslog.syslog.assert_called_with(syslog.LOG_ERR,
                                         "ERROR: %s" % message)



    def test_log(self):
        print("Testing log()")
        from stallmanbot import log
        import syslog

        debug = MagicMock()
        syslog.openlog = MagicMock()
        syslog.syslog = MagicMock()

        message = "testing"
        log(message)
        syslog.openlog.assert_called_with("StallNoMan")
        syslog.syslog.assert_called_with(syslog.LOG_INFO,
                                         message)

    def test_read_file(self):
        print("Testing read_file()")
        from stallmanbot import read_file, error

        fs = mockfs.replace_builtins()
        fs.add_entries({ "/etc/python" : "zen of python",
                        "/étç/två" : "ett två três"})

        print(" * file exists and it is ASCII")
        result = read_file("/etc/python")
        self.assertEqual(result, "zen of python", "Failed to read content")

        print(" * file exists and it is UTF-8")
        result = read_file("/étç/två")
        self.assertEqual(result, "ett två três", "Failed to read content")

        print(" * file doesn't exist")
        result = read_file("/etc/helio_loureiro")
        self.assertEqual(result, None, "None return failed from non-existent file")

        mockfs.restore_builtins()

    def test_check_if_run(self):
        print("Testing check_if_run()")
        from stallmanbot import check_if_run, PIDFILE
        import sys
        import time
        import os

        fs = mockfs.replace_builtins()
        fs.add_entries({"%s/.stallmanbot.pid" % os.environ["HOME"] : "12345",
                       "/proc/12345/running" : "yes"})
        sys.exit = MagicMock(return_value="exiting")
        os.getpid = MagicMock(return_value=12345)
        log = MagicMock()

        print(" * process exists and is running")
        print("mypid=%d" % os.getpid())
        check_if_run()

        mockfs.restore_builtins()



if __name__ == '__main__':
    unittest.main()
