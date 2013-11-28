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

from chat import Chat

class TestSMTPd(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestSMTPd, self).__init__(*args, **kwargs)
        self.beanstalkd = {
            'host': '127.0.0.1',
            'port': 11372,
        }
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
        self.smtpd_args['beanstalk'] = "%s:%d"%(self.beanstalkd['host'], self.beanstalkd['port'])
        self.proc_delay = 0.3

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
        for p in self.procs:
            p['_proc'] = subprocess.Popen(p['run'], **p['args'])
            p['_pid'] = p['_proc'].pid
            time.sleep(self.proc_delay)

        self._stop_procs.wait()

        for p in self.procs:
            p['_proc'].terminate()
            try:
                os.kill(int(p['_pid']), signal.SIGTERM)
                os.kill(int(p['_pid']), signal.SIGKILL)
            except OSError:
                pass

    def setUp(self):
        #Make a tempdir for our queue
        self.smtpd_args['queue'] = tempfile.mkdtemp()

        #build proc list
        self.procs = [
            {'run': ['beanstalkd', '-l', self.beanstalkd['host'], '-p', str(self.beanstalkd['port'])], 'args': dict(stdout=sys.stderr, stderr=sys.stderr)},
            {'run': ["python", self.smtpd] + self._make_args(self.smtpd_args), 'args': dict(stdout=sys.stderr, stderr=sys.stderr)},
        ]

        #start up the background processes
        self._stop_procs=threading.Event()
        self._procs_thread=threading.Thread(target=self._run_procs)
        self._procs_thread.start()
        time.sleep(self.proc_delay * len(self.procs))
        
        #now make sure the smtpd is accepting connections or we can't keep testing
        self.sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        res=self.sock.connect_ex(("127.0.0.1", 2525))
        self.assertEqual(res, 0, "The test SMTPD is not accepting connections")

        #test beanstalkd too
        bs_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        res = bs_sock.connect_ex((self.beanstalkd['host'], self.beanstalkd['port']))
        self.assertEqual(res, 0, "The test beanstalkd is not accepting connections")
        bs_sock.close()

        self.beanstalk = beanstalkc.Connection(**self.beanstalkd)
        self.beanstalk.watch('new_smtp')

    def tearDown(self):
        try:
            self.sock.close()
        except:
            pass
        self._stop_procs.set()
        self._procs_thread.join()
        shutil.rmtree(self.smtpd_args['queue'])
        self.smtpd_args['queue'] = None

    def test_send(self):
        sock = Chat(self.sock, line_term = "\r\n")
        sock.rexpect(ur"^220")
        sock.send("HELO unittesting")
        sock.rexpect(ur"^250")
        sock.send("MAIL FROM: <support@port25.com>")
        sock.rexpect(ur"^250")
        sock.send("RCPT TO: <support@port25.com>")
        sock.rexpect(ur"^250")
        sock.send("DATA")
        sock.rexpect(ur"^354")
        sock.send('From: "John Smith" <jsmith@port25.com>')
        sock.send('To: "Jane Doe" <jdoe@port25.com>')
        sock.send('Subject: test message sent from manual telnet session')
        sock.send('Date: Wed, 11 May 2011 16:19:57 -0400\r\n')
        sock.send('Hello World,')
        sock.send('This is a test message sent from a manual telnet session.\r\n')
        sock.send('Yours truly,')
        sock.send('SMTP administrator')
        sock.send('.')
        sock.rexpect(ur"^250")
        sock.send("QUIT")
        sock.rexpect(ur"^221")
        self.assertIsNotNone(self.beanstalk.reserve(timeout = 30))

if __name__ == '__main__':
    unittest.main()