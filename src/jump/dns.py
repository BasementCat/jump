import socket, logging, threading, Queue

log=logging.getLogger(__name__)

toResolve=Queue.Queue(maxsize=64)
resolved=Queue.Queue(maxsize=64)
threads=[]
cache={}
cacheLock=threading.RLock()

def gethostbyname(name, callback):
	log.info("Looking up hostname %s", name)
	toResolve.put(("gethostbyname", name, callback), block=True)

def gethostbyaddr(addr, callback):
	log.info("Looking up address %s", addr)
	toResolve.put(("gethostbyaddr", addr, callback), block=True)

def resolver():
	try:
		method, arg, callback=toResolve.get(block=True, timeout=1)
		
		cacheLock.acquire(blocking=1)
		if arg in cache:
			result=cache[arg]
			cacheLock.release()
		else:
			cacheLock.release()
			result=getattr(socket, method)(arg)
			cacheLock.acquire(blocking=1)
			cache[arg]=result
			cacheLock.release()
		resolved.put((callback, result, threading.current_thread()), block=True)
	except Queue.Empty:
		pass

def run():
	for i in range(min(toResolve.qsize(), 5)):
		t=threading.Thread(target=resolver)
		threads.append(t)
		t.start()
	try:
		while not resolved.empty():
			callback, result, thread=resolved.get(block=False)
			thread.join()
			threads.remove(thread)
			callback(result)
	except Queue.Empty:
		pass

def stop():
	global threads
	log.info("Waiting for %d DNS resolver threads to stop...", len(threads))
	for t in threads:
		t.join()
	threads=[]
	log.info("All DNS resolver threads have been stopped.")

def clearCache():
	global cache
	cacheLock.acquire(blocking=1)
	cache={}
	cacheLock.release()