import logging
from storm.locals import *
from jsonrpc import RpcMethod
from database import store, User
import dns

log=logging.getLogger(__name__)

@RpcMethod("register")
def doRegister(cl, message, username, password):
	dns.gethostbyaddr(cl.remoteHost, finishRegister, cl=cl, message=message)

def finishRegister(result, cl, message):
	cl.hostname=result[0]
	if not User.validateUsername(message["params"]["username"]):
		cl.reply(message, error={"code": 11, "message": "The username you have chosen is invalid", "data": message["params"]["username"]})
		return
	if store.find(User, Like(User.username, message["params"]["username"])).one():
		cl.reply(message, error={"code": 11, "message": "The username you have chosen is already in use", "data": message["params"]["username"]})
		return
	u=User()
	u.username=message["params"]["username"]
	u.password=message["params"]["password"]
	store.add(u)
	store.commit()
	cl.reply(message, result="OK")