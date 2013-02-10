import logging, json, uuid
from datetime import datetime, timedelta
from network import Client, Server

JSON_RPC_VERSION="2.0"
RESPONSE_TIMEOUT=60

RPCMethods={}

log=logging.getLogger(__name__)

class JsonRpcClient(Client):
	def __init__(self, *args, **kwargs):
		super(JsonRpcClient, self).__init__(*args, **kwargs)
		self.responseCallbacks={}

	def onNewData(self):
		d=self.sock.recv(1024)
		if d=="":
			log.debug("Client sent no data: %s", self)
			if "_disconnect" in RPCMethods:
				RPCMethods["_disconnect"](self)
			self.close()
			return
		self.dataQueue+=d
		parts=self.dataQueue.split("\r\n\r\n")
		if self.dataQueue.endswith("\r\n\r\n"):
			self.dataQueue=""
		else:
			self.dataQueue=parts.pop()
		for part in parts:
			if not part:
				continue
			try:
				obj=json.loads(part)
				if "result" in obj or "error" in obj:
					#this is a response
					if not "id" in obj:
						#TODO: if ID is not present, this is an error
						log.error("Client sent a response with no id: %s, %s", self, json.dumps(obj))
					elif not obj["id"]:
						#TODO: if ID is null/false/etc we need to report/log this but we can't do anything further
						log.error("Client sent a response with a null id: %s, %s", self, json.dumps(obj))
					else:
						if obj["id"] in self.responseCallbacks:
							self.responseCallbacks[obj["id"]][1](self, error=obj["error"] if "error" in obj else None, result=obj["result"] if "result" in obj else None)
							del(self.responseCallbacks[obj["id"]])
						else:
							#TODO: no response callback, send an error to the client (invalid id)
							log.error("Client responded with an invalid id: %s, %s", self, json.dumps(obj))
				elif "method" in obj:
					#this is a request
					#TODO: if this is an invalid method, tell the client
					log.debug("Client %s called: %s", self, json.dumps(obj))
					RPCMethods[obj["method"]](self, **(obj["params"] if "params" in obj else {}))
			except ValueError:
				log.error("Client sent invalid JSON: %s, %s", self, part)
				pass #TODO: send err to client

	def call(self, method, callback=None, **kwargs):
		out={
			"jsonrpc": JSON_RPC_VERSION,
			"method": method,
			"params": kwargs
		}
		if callback:
			out.update({"id": str(uuid.uuid4())})
			self.responseCallbacks[out["id"]]=(datetime.utcnow()+timedelta(seconds=RESPONSE_TIMEOUT), callback)
		return self.sock.sendall(json.dumps(out)+"\r\n\r\n")

	def reply(self, orig, result=None, error=None):
		if not "id" in orig:
			#TODO: orig must be a request and have an id
			return
		out={
			"jsonrpc": JSON_RPC_VERSION,
			"id": orig["id"]
		}
		if result:
			out["result"]=result
		else:
			out["error"]=error
		return self.sock.sendall(json.dumps(out)+"\r\n\r\n")

class JsonRpcServer(Server):
	def onNewSock(self, newSock):
		log.debug("Creating new jsonrpc client (server)")
		cl=JsonRpcClient(newSock)
		if "_connect" in RPCMethods:
			RPCMethods["_connect"](cl)
		return cl

def RpcMethod(methodName):
	def _RpcWrapExternal(callback):
		global RPCMethods
		if methodName not in RPCMethods:
			RPCMethods[methodName]=[]
		RPCMethods[methodName].append(callback)
		return callback
	return _RpcWrapExternal