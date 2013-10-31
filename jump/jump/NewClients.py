import logging
from jsonrpc import RpcMethod
import dns

log=logging.getLogger(__name__)

@RpcMethod("identify")
def doIdentify(cl, message, username, password):
	log.debug("Client %s identifying with u=%s, p=%s", cl, username, password)
	dns.gethostbyaddr(cl.remoteHost, finishIdentify, cl=cl, message=message)

def finishIdentify(result, cl, message):
	cl.hostname=result[0]
	cl.reply(message, result={"hostname": cl.hostname})