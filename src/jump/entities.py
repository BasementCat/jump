import logging, json, uuid
from datetime import datetime, timedelta
from network import Client, Server
from jsonrpc import JsonRpcClient, JsonRpcServer
import dns

log=logging.getLogger(__name__)

class JumpClient(JsonRpcClient):
	def __init__(self, *args, **kwargs):
		super(JumpClient, self).__init__(*args, **kwargs)
		self.hostname=None
		dns.gethostbyaddr(self.remoteHost, self._setHostname)

	def _setHostname(self, lookup):
		self.hostname=lookup[0]

class JumpServer(JsonRpcServer):
	def onNewSock(self, newSock, listener):
		cl=JumpClient(newSock, listener)
		return super(JumpServer, self).onNewSock(cl, listener)