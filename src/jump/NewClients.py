import logging
from jsonrpc import RpcMethod

log=logging.getLogger(__name__)

@RpcMethod("identify")
def doIdentify(cl, message, username, password):
	log.debug("Client %s identifying with u=%s, p=%s", cl, username, password)
	cl.reply(message, result="OK")