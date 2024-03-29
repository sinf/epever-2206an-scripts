import json
import time
from threading import Thread
import socket
import http.server
import socketserver
from typing import Tuple
from http import HTTPStatus
from urllib.parse import parse_qsl

from .util import *
from .register import *
from .device import *

class RequestHandler(http.server.SimpleHTTPRequestHandler):

    def __init__(self, request: bytes, client_address: Tuple[str, int], s: socketserver.BaseServer):
        super().__init__(request, client_address, s)

    def oldest_good_time(self):
        return time.time() - 30

    def bad_request(self,
            code=HTTPStatus.NOT_IMPLEMENTED,
            msg="Request DENIED! This incident will be logged and reported\n"):
        # not actually logging anything lol
        self.send_response(code)
        self.end_headers()
        self.wfile.write(msg.encode())

    def do_HEAD(self):
        self.bad_request()

    def sane_update_interval(self, dbtable):
        if dbtable == 'stats':
            return 10
        else:
            return 24*60*60

    def do_GET(self):
        path=self.path
        path_parts = path.lstrip('/').split('/')
        p0 = path_parts[0].strip().lower() if len(path_parts)>0 else None
        if (dbtable := p0) in the_device.dbtable_regs:
            min_t = time.time() - self.sane_update_interval(dbtable)
            keys = the_device.names(dbtable)
            the_device.read_regs(keys, update_older_than=min_t)
            resp = the_device.to_json(keys, indent=1)
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(resp.encode())
        elif (name := p0) in the_device.regs: # /<id>
            reg = the_device.regs[name]
            min_t = time.time() - self.sane_update_interval(reg.dbtable)
            the_device.read_regs([name], update_older_than=min_t)
            resp = the_device.to_json([name], indent=1)
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(resp.encode())
        else:
            self.bad_request()

    def do_POST(self):
        if config('http_api.can_write') != True:
            return self.bad_request()

        bodylen = int(self.headers.get('Content-Length'))
        body = self.rfile.read(bodylen)

        if self.path == '/write':
            t=self.headers.get('Content-Type')
            if t == 'application/json':
                key_values = json.loads(body)
            elif t == 'application/x-www-form-urlencoded':
                f = lambda x: x.decode('utf-8', errors='ignore')
                key_values = dict((f(k),f(v)) for k,v in parse_qsl(body))
            else:
                return self.bad_request(HTTPStatus.BAD_REQUEST)
        else: # /<id>
            if (name := self.path[1:]) not in the_device.regs:
                return self.bad_request(HTTPStatus.NOT_FOUND)
            key_values = {name: body.strip()}
        resp = {}
        ok=True
        print(key_values)
        for name, value in key_values.items():
            is_error, msg = the_device.write(name, value)
            resp[name] = msg if is_error else 'ok'
            ok = ok and not is_error
        resp_j = json.dumps(resp, indent=4).encode()
        self.send_response(HTTPStatus.OK if ok else HTTPStatus.INTERNAL_SERVER_ERROR)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(resp_j)


class ImprovedServer(socketserver.ThreadingTCPServer):
    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        super().server_bind()

def start_http_server(device):
    global the_device
    the_device = device
    ip = config('http_api.bind_ip', '127.0.0.1')
    port = int(config('http_api.port', 8000))
    def server_main():
        print(f"Starting server at {ip} {port}")
        sv = ImprovedServer((ip, port), RequestHandler)
        sv.serve_forever()
    t = Thread(target=server_main, daemon=True, name='http-server')
    t.start()
    return t

