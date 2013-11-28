import select
import re

class Chat (object):
    def __init__(self, sock, timeout = 10, line_term = ""):
        self.sock = sock
        self.timeout = timeout
        self.line_term = line_term

    def rexpect(self, what):
        r, w, e = select.select([self.sock], [], [], self.timeout)
        if len(r) < 1:
            raise Exception("Did not receive data after %d seconds"%(self.timeout,))
        for sock in r:
            data = sock.recv(1048576)
            if not re.match(what, data):
                raise Exception("Expected to match '%s', got: %s"%(what, data))

    def send(self, what):
        for line in (what if isinstance(what, list) else [what]):
            self.sock.sendall(line + self.line_term)