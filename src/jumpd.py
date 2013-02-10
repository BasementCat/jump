#!/usr/bin/python

import logging
from jump.network import Server, Client, refresh
from jump.jsonrpc import JsonRpcServer
from jump import NewClients

logging.basicConfig(level=logging.DEBUG)
log=logging.getLogger(__name__)

s=JsonRpcServer("0.0.0.0", 1234)

while True:
	refresh()