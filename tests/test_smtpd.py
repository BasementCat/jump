import sys
import os
import time
import unittest
import subprocess
import threading
import signal
import socket

class TestSMTPd(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestSMTPd, self).__init__(*args, **kwargs)
        self.smtpd = os.path.join(os.path.dirname(os.path.dirname(__file__)), "jump", "jump-smtpd.py")

    def _run_smtpd(self):
        smtpd_proc=subprocess.Popen(["python", self.smtpd], stdout=sys.stderr, stderr=sys.stderr)
        pid=smtpd_proc.pid
        self._stop_smtpd.wait()
        smtpd_proc.terminate()
        try:
            os.kill(int(pid), signal.SIGTERM)
            os.kill(int(pid), signal.SIGKILL)
        except OSError:
            pass

    def setUp(self):
        #start up the smtpd
        self._stop_smtpd=threading.Event()
        self._smtpd_thread=threading.Thread(target=self._run_smtpd)
        self._smtpd_thread.start()
        #let the smtpd start up
        time.sleep(1)
        
        #now make sure the smtpd is accepting connections or we can't keep testing
        self.sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        res=self.sock.connect_ex(("127.0.0.1", 2525))
        self.assertEqual(res, 0, "The test SMTPD is not accepting connections")

    def tearDown(self):
        self.sock.close()
        self._stop_smtpd.set()
        self._smtpd_thread.join()

    def test_test(self):
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()