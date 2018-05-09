#! /usr/bin/python3

import unittest
from mock import MagicMock, Mock
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
        #sys.exit.assert_called_with(os.EX_OK)

        #print(" * process doesn't exist and isn't running")
        #fs.remove("%s/.stallmanbot.pid" % os.environ["HOME"])
        #check_if_run()

        mockfs.restore_builtins()

    def test_save_file(self):
        print("Testing check_if_run()")
        from stallmanbot import save_file

        fs = mockfs.replace_builtins()
        fs.add_entries({"/tmp/testing" : ""})
        save_file("12345", "/tmp/testing")

        self.assertEqual("12345", fs.read("/tmp/testing"), "Saving data failed")

        mockfs.restore_builtins()

    def test_read_configuration(self):
        print("Testing read_configuration()")
        from stallmanbot import read_configuration
        import sys
        import time
        import os
        import configparser

        fs = mockfs.replace_builtins()
        SESSION = "TELEGRAM"
        fs.add_entries({"configuration.conf" : "[TELEGRAM]\n" + \
            "STALLBOT = abc:123456\n" + \
            "STALLBOTADM = HelioLoureiro\n"})
        sys.exit = MagicMock()
        error = MagicMock()

        print(" * correct configuration")
        cfg = read_configuration("configuration.conf")
        self.assertEqual(cfg.get(SESSION, "STALLBOT"), "abc:123456", "Parameter didn't match.")
        self.assertEqual(cfg.get(SESSION, "STALLBOTADM"), "HelioLoureiro", "Parameter didn't match.")

        print(" * missing session")
        SESSION = "FAKE"
        self.assertRaises(configparser.NoSectionError,
                          cfg.get,
                          SESSION,
                          "STALLBOT")
        print(" * missing session using utf-8")
        SESSION = "FåKEçÉ"
        self.assertRaises(configparser.NoSectionError,
                          cfg.get,
                          SESSION,
                          "STÁLLBÖT")

        print(" * missing parameter")
        SESSION = "TELEGRAM"
        self.assertRaises(configparser.NoOptionError,
                          cfg.get,
                          SESSION,
                          "WHATEVER")
        mockfs.restore_builtins()

    def test_get_telegram_key(self):
        print("Testing get_telegram_key()")

        from stallmanbot import read_configuration, get_telegram_key
        import os
        import configparser

        fs = mockfs.replace_builtins()
        SESSION = "TELEGRAM"
        fs.add_entries({"configuration.conf" : "[TELEGRAM]\n" + \
            "STALLBOT = abc:123456\n" + \
            "STALLBOTADM = HelioLoureiro\n"})
        sys = Mock()
        error = Mock()
        debug = Mock()

        cfg = read_configuration("configuration.conf")
        print(" * testing existent values")
        result = get_telegram_key(cfg, "STALLBOT")
        self.assertEqual(result, "abc:123456", "Resulting is mismatching expected value.")

        print(" * testing non-existent values")
        result = get_telegram_key(cfg, "ROCKNROLL")
        self.assertIsNone(result, "Command returned value (expected empty).")

        mockfs.restore_builtins()

    def test_get_foodporn_json(self):
        print("Testing get_foodporn_json()")

if __name__ == '__main__':
    unittest.main()
