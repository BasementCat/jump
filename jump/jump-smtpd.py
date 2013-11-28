#!/usr/bin/python

import logging
import asyncore
import argparse
import os
import cPickle as pickle
import hashlib

from secure_smtpd import SMTPServer
import beanstalkc

from jump.network import parse_service

class JumpSMTPd (SMTPServer):
    #def __init__(self, localaddr, remoteaddr, ssl=False, certfile=None, keyfile=None, ssl_version=ssl.PROTOCOL_SSLv23, require_authentication=False, credential_validator=None, maximum_execution_time=30, process_count=5):
    def __init__(self, cmd_args, *args, **kwargs):
        SMTPServer.__init__(self, *args, **kwargs)
        self.cmd_args = cmd_args
        bs_host, bs_port = cmd_args.beanstalk
        self.beanstalk = beanstalkc.Connection(host = bs_host, port = bs_port)

    def process_message(self, peer, mailfrom, rcpttos, data):
        mail = dict(
            peer = peer,
            mailfrom = mailfrom,
            rcpttos = rcpttos,
            data = data
        )
        mail_pickled = pickle.dumps(mail, 0 if self.cmd_args.debug else pickle.HIGHEST_PROTOCOL)
        fname = hashlib.sha512(mail_pickled).hexdigest()
        with open(self.cmd_args.queue + '/' + fname + '.pickle', 'wb') as fp:
            fp.write(mail_pickled)

        self.beanstalk.use('new_smtp')
        self.beanstalk.put(fname)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'Accept SMTP traffic for JUMP to process')
    parser.add_argument('--host', default = '0.0.0.0', help = "Bind to this host")
    parser.add_argument('--port', default = 25, type = int, help = "Unencrypted SMTP port  (0 to disable)")
    parser.add_argument('--ssl', action = 'store_true', help = "Enable SSL - a certfile and keyfile must be specified")
    parser.add_argument('--ssl-port', default = 465, type = int, help = "SMTP+SSL port")
    parser.add_argument('--certfile', help = "SSL certfile")
    parser.add_argument('--keyfile', help = "SSL keyfile")
    parser.add_argument('--queue', default = '/var/jump/smtpd-queue', help = "Messages will be dumped to this queue directory for processing")
    parser.add_argument('--debug', action = 'store_true', help = "Enable debugging - extra output may be produced")
    parser.add_argument('--beanstalk', default = '127.0.0.1:11300', help = "Beanstalkd hostname and port number to connect to")
    args = parser.parse_args()

    #let's sanity check!
    if not (args.port or args.ssl):
        raise Exception("You must supply a non-zero --port (or use the default), or enable --ssl")

    if args.ssl:
        if not (args.certfile and args.keyfile):
            raise Exception("To enable SSL, a certfile and keyfile must be provided")
        elif not (os.path.exists(args.certfile) and os.path.isfile(args.certfile)):
            raise Exception("Certfile '%s' does not exist or is not a file"%(args.certfile,))
        elif not (os.path.exists(args.keyfile) and os.path.isfile(args.keyfile)):
            raise Exception("Keyfile '%s' does not exist or is not a file"%(args.keyfile,))

    if not (os.path.exists(args.queue) and os.path.isdir(args.queue)):
        raise Exception("The queue '%s' does not exist or is not a directory"%(args.queue,))

    _bs = parse_service(args.beanstalk)
    if _bs is None:
        raise Exception("'%s' is not a valid service address for beanstalkd"%(args.beanstalk,))
    else:
        args.beanstalk = _bs

    server = None
    SSLserver = None

    if args.port:
        server = JumpSMTPd(
            args,
            (args.host, args.port),
            None,
            ssl = False,
            certfile = None,
            keyfile = None,
            require_authentication = False
        )

    if args.ssl:
        SSLserver = JumpSMTPd(
            args,
            (args.host, args.ssl_port),
            None,
            ssl = True,
            certfile = args.certfile,
            keyfile = args.keyfile,
            require_authentication = False
        )

    try:
        asyncore.loop()
    except KeyboardInterrupt:
        if server:
            server.close()

        if SSLserver:
            SSLserver.close()