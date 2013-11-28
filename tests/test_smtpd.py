import sys
import os
import time
import unittest
import subprocess
import threading
import signal
import socket
import tempfile
import shutil
import random

import beanstalkc

class TestSMTPd(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestSMTPd, self).__init__(*args, **kwargs)
        self.smtpd = os.path.join(os.path.dirname(os.path.dirname(__file__)), "jump", "jump-smtpd.py")
        self.smtpd_args = {
            'host':     '0.0.0.0',
            'port':     2525,
            'ssl':      False,
            'ssl-port': None, #465
            'certfile': None,
            'keyfile':  None,
            'queue':    None,
        }
        self.beanstalkd = {
            'host': '127.0.0.1',
            'port': 11372,
        }

    def _make_args(self, argdict):
        out = []
        for k,v in argdict.items():
            if not v:
                continue
            out.append('--' + k)
            if v is not True:
                out.append(str(v))
        return out

    def _run_procs(self):
        procs = [
            {'run': ["python", self.smtpd] + self._make_args(self.smtpd_args), 'args': dict(stdout=sys.stderr, stderr=sys.stderr)},
            {'run': ['beanstalkd', '-l', self.beanstalkd['host'], '-p', str(self.beanstalkd['port'])], 'args': dict(stdout=sys.stderr, stderr=sys.stderr)},
        ]

        for p in procs:
            p['_proc'] = subprocess.Popen(p['run'], **p['args'])
            p['_pid'] = p['_proc'].pid

        self._stop_procs.wait()

        for p in procs:
            p['_proc'].terminate()
            try:
                os.kill(int(p['_pid']), signal.SIGTERM)
                os.kill(int(p['_pid']), signal.SIGKILL)
            except OSError:
                pass

    def setUp(self):
        #Make a tempdir for our queue
        self.smtpd_args['queue'] = tempfile.mkdtemp()
        #start up the smtpd
        self._stop_procs=threading.Event()
        self._procs_thread=threading.Thread(target=self._run_procs)
        self._procs_thread.start()
        #let the smtpd start up
        time.sleep(1)
        
        #now make sure the smtpd is accepting connections or we can't keep testing
        self.sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        res=self.sock.connect_ex(("127.0.0.1", 2525))
        self.assertEqual(res, 0, "The test SMTPD is not accepting connections")

        #test beanstalkd too
        bs_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        res = bs_sock.connect_ex((self.beanstalkd['host'], self.beanstalkd['port']))
        self.assertEqual(res, 0, "The test beanstalkd is not accepting connections")
        bs_sock.close()

    def tearDown(self):
        self.sock.close()
        self._stop_procs.set()
        self._procs_thread.join()
        shutil.rmtree(self.smtpd_args['queue'])
        self.smtpd_args['queue'] = None

    def test_asdf(self):
        self.sock.send("asdflkjaslkdf\r\n")

if __name__ == '__main__':
    unittest.main()