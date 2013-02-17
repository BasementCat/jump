#!/usr/bin/python

import logging
from jump.network import refresh
from jump.entities import JumpServer
from jump import dns, database
from jump import NewClients, Registration

logging.basicConfig(level=logging.DEBUG)
log=logging.getLogger(__name__)

s=JumpServer("0.0.0.0", 1234)

try:
	while True:
		dns.run()
		refresh()
except KeyboardInterrupt:
	pass

dns.stop()