import logging
from jsonrpc import RpcMethod

log=logging.getLogger(__name__)

@RpcMethod("_connect")
def ChallengeAuth(cl):
	def AuthResponse(cl, result=None, error=None):
		if result:
			log.debug("Client %s:%d authed with u=%s p=%s", cl.remoteHost, cl.remotePort, result["username"], result["password"])
	cl.call("challenge_auth", callback=AuthResponse)

@RpcMethod("_disconnect")
def doDisconnect(cl):
	log.debug("Client disconnected suddenly: %s:%d", cl.remoteHost, cl.remotePort)