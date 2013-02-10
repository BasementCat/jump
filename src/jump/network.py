import socket, select, logging

servers={}
clients={}
allSocks=[]

log=logging.getLogger(__name__)

class Server(object):
	def __init__(self, host, port, v6=False):
		global servers, allSocks

		self.host=host if host else ("::" if v6 else "0.0.0.0")
		self.port=port
		self.v6=v6

		self.sock=socket.socket(socket.AF_INET6 if self.v6 else socket.AF_INET, socket.SOCK_STREAM)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sock.bind((self.host, self.port))
		self.sock.listen(16)

		log.info("Listening on %s", self)

		servers[self.sock]=self
		allSocks.append(self.sock)

	def stop(self):
		global servers, allSocks

		del(servers[self.sock])
		allSocks.remove(self.sock)
		self.sock.close()
		log.info("Stopped listening on %s", self)

	def _onNewSock(self):
		global clients, allSocks
		newSock=self.sock.accept()[0]
		out=self.onNewSock(newSock, self)
		clients[newSock]=out
		allSocks.append(newSock)

	def onNewSock(self, newSock, listener):
		return Client(newSock, listener)

	def __str__(self):
		if self.v6:
			return "[%s]:%d"%(self.host, self.port)
		else:
			return "%s:%d"%(self.host, self.port)

class Client(object):
	def __init__(self, newSock, listener):
		self.sock=newSock
		self.localHost, self.localPort=self.sock.getsockname()
		self.remoteHost, self.remotePort=self.sock.getpeername()
		self.dataQueue=""
		self.server=listener
		log.info("New client: %s->%s", self, self.server)

	def onNewData(self):
		d=self.sock.recv(1024)
		self.dataQueue+=d
		log.debug("Got %d bytes from %s:%d", len(d), self.remoteHost, self.remotePort)

	def close(self):
		global clients, allSocks
		del(clients[self.sock])
		allSocks.remove(self.sock)
		self.sock.close()

	def __str__(self):
		return "%s:%d"%(self.remoteHost, self.remotePort)

def refresh(selectTimeout=0.1):
	global allSocks, servers, clients
	readSocks=allSocks
	read, write, exc=select.select(readSocks, [], [], selectTimeout)
	for sock in read:
		if sock in servers:
			servers[sock]._onNewSock()
		else:
			clients[sock].onNewData()

def shutdown():
	global allSocks
	for sock in allSocks:
		sock.close()