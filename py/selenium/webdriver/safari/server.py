import socket
#from selenium.webdriver.common import utils

CLIENTJS = r"C:\Users\jayakum\selenium\javascript\safari-driver\client.js"


class Server(object):

    HEADER = r"""HTTP/1.1 %d %s\r\n
Content-Type: text/html; charset=utf-8\r\n
Server: safaridriver-python\r\n
"""
    HTML = r"<!DOCTYPE html><script>%s</script>" % open(CLIENTJS).read()

    def __init__(self, port=None, timeout=60):
        self.port = 9000
        self.timeout = timeout

    def start(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(("127.0.0.1", self.port))
        self.server.listen(1)
        self.process_initial_http_request()
        self.process_handshake()

    def stop(self):
        if self.server:
            self.server.close()

    def process_initial_http_request(self):
        conn, addr = self.server.accept()
        print "accepted"
        print addr
        self.data = conn.recv(1024)
        print self.data

        head_end = self.data.find("\r\n\r\n")
        if head_end == -1:
            raise "No initial http request from safari driver"

        head = self.data[:head_end]
        print "head:"
        print head
        f = conn.makefile("r+b", bufsize=0)
        if head.find("?url=") != -1:
            f.write(self.HEADER % (200, 'OK'))
            f.write(self.HTML)
            f.flush()
            f.close()
            conn.close()
            print "connected..."
        else:
            f.write(Server.HEADER % (302, 'Moved Temporarily'))
            f.write(r"Location: http%3A%2F%2F127.0.0.1%3A9000?url=ws%3A%2F%2F127.0.0.1%3A9000%2Fwd\r\n")
            f.write(r"\r\n\r\n")
            f.flush()
            f.close()
            conn.close()
            print "No initial conn"
            self.process_initial_http_request()

    def process_handshake(self):
        conn, addr = self.server.accept()
        self.data = conn.recv(1024)
        print "Handshake started"
        print self.data

        if self.data.find("favicon.ico") != -1:
            conn.close()
            self.process_handshake()
