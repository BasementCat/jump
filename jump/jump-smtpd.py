#!/usr/bin/python

import logging
import asyncore
from smtpd import SMTPServer

class JumpSMTPd (SMTPServer):
    #Constructor signature takes a localaddr and remoteaddr

    def process_message(self, peer, mailfrom, rcpttos, data):
        print data

server = JumpSMTPd(('127.0.0.1', 2525), None)

if __name__ == '__main__':
    asyncore.loop()