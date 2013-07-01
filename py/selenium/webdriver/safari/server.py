import socket
#from selenium.webdriver.common import utils

CLIENTJS = r"C:\Users\jayakum\selenium\javascript\safari-driver\client.js"


class Server(object):

    HEADER = """HTTP/1.1 %d %s
Content-Type: text/html; charset=utf-8
Server: safaridriver-python
""".replace("\n", "\r\n")

    HTML = "<!DOCTYPE html><script>" + open(CLIENTJS).read() + "</script>"

    def __init__(self, port=None, timeout=60):
        self.port = 9000
        self.timeout = timeout

    def start(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #self.server.setblocking(0)
        self.server.bind(("127.0.0.1", self.port))
        self.server.listen(2)
        self.process_initial_http_request()
        self.process_handshake()

    def stop(self):
        if self.server:
            self.server.close()

    def process_initial_http_request(self):
        conn, addr = self.server.accept()
        print "accepted.."
        self.data = conn.recv(1024)

        head_end = self.data.find("\r\n\r\n")
        if head_end == -1:
            raise "No initial http request from safari driver"

        head = self.data[:head_end]
        f = conn.makefile("r+b", bufsize=0)
        if head.find("?url=") == -1:
            f.write(Server.HEADER % (302, 'Moved Temporarily'))
            import urllib2
            f.write("Location: http://127.0.0.1:9000?url=" + urllib2.quote("ws://127.0.0.1:9000/wd") + "\r\n")
            f.write("\r\n\r\n")
            f.flush()
            f.close()
            conn.close()
            self.process_initial_http_request()
        else:
            f.write(self.HEADER % (200, 'OK'))
            print repr(self.HEADER)
            f.write("\r\n\r\n")
            print repr(self.HTML)
            f.write(self.HTML)
            f.flush()
            f.close()
            conn.close()
            print "sent HTML"


    def process_handshake(self):
        conn, addr = self.server.accept()
        self.data = conn.recv(1024)
        print "Handshake started"
        print self.data

        if self.data.find("favicon.ico") != -1:
            conn.close()
            self.process_handshake()
