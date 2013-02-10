#!/usr/bin/python

import logging
from jump.network import refresh
from jump.entities import JumpServer
from jump import NewClients

logging.basicConfig(level=logging.DEBUG)
log=logging.getLogger(__name__)

s=JumpServer("0.0.0.0", 1234)

while True:
	refresh()