#! /usr/bin/env python
# -*-- coding: utf-8 -*-

import eventlet
import json
import socket as orig_socket
import sys
import time
import threading
import types
import traceback

from eventlet import wsgi
from eventlet.green import socket
from eventlet.wsgi import HttpProtocol
from SocketServer import BaseRequestHandler
from ti_server.common.log import logger as log
from ti_server.rest_parser import RestReqApp
from webob import Response


class TiRestServer(threading.Thread):

    def __init__(self, name, host, port):
        super(TiRestServer, self).__init__(name=name)
        self.host = host
        self.port = port
        self.app = RestReqApp()

    def run(self):
        log.info("ti-server running at http://%s:%s" % (self.host, self.port))
        while True:
            try:
                HTTPServer(
                    self.host, self.port, self.app, threaded=False
                ).start()
            except Exception as e:
                log.error("exception occurred when request to ti server http"
                          "://%s:%s, error: %s" % (self.host, self.port, e))
                time.sleep(3)


class ServerLog(object):

    def __init__(self, _log):
        self.log = _log

    def write(self, msg):
        self.log.debug(msg)

    def info(self, msg):
        self.log.info(msg)

    def warn(self, msg):
        self.log.warn(msg)

    def error(self, msg):
        self.log.error(msg)


class HTTPServer(object):

    def __init__(self, host, port, app, threaded=False, _log=None,
                 socket_timeout=None, need_parallel_func=None):
        self.host = host
        self.port = port
        self.app = app
        self.threaded = threaded
        self.log = ServerLog(_log) if _log is not None else None
        self.socket_timeout = socket_timeout
        self.need_parallel_func = need_parallel_func

    def start(self):

        if not self.threaded:
            socket_class = socket
            _socket = eventlet.listen((self.host, int(self.port)))
        else:
            socket_class = orig_socket
            _socket = orig_socket.socket(
                orig_socket.AF_INET, orig_socket.SOCK_STREAM
            )

            if sys.platform[:3] != "win":
                _socket.setsockopt(socket_class.SOL_SOCKET,
                                   socket_class.SO_REUSEADDR, 1)

            _socket.bind((self.host, int(self.port)))
            _socket.listen(50)

        try:
            _socket.setsockopt(socket_class.SOL_SOCKET,
                               socket_class.SO_KEEPALIVE, 1)

            if hasattr(socket_class, 'TCP_KEEPIDLE'):
                _socket.setsockopt(socket_class.IPPROTO_TCP,
                                   socket_class.TCP_KEEPIDLE, 120)
                _socket.setsockopt(socket_class.IPPROTO_TCP,
                                   socket_class.TCP_KEEPCNT, 4)
                _socket.setsockopt(socket_class.IPPROTO_TCP,
                                   socket_class.TCP_KEEPINTVL, 15)

            srv = wsgi.server if not self.threaded else thread_server
            if (isinstance(self.app, types.InstanceType) and not isinstance(
                    self.app, BaseRequestHandler)) \
                    or isinstance(self.app, types.FunctionType):
                srv(_socket, self.app, protocol=HttpProtocol, log=self.log,
                    socket_timeout=self.socket_timeout,
                    need_parallel_func=self.need_parallel_func)
            elif isinstance(self.app, types.ClassType):
                srv(_socket, _default_app, protocol=self.app, log=self.log,
                    socket_timeout=self.socket_timeout,
                    need_parallel_func=self.need_parallel_func)
            else:
                srv(_socket, self.app, protocol=HttpProtocol, log=self.log,
                    socket_timeout=self.socket_timeout)
                # raise Exception("rest server only support func call or "
                #                 "instance of BaseRequestHandler")
        except Exception as e:
            log.error("HTTPServer start error: %s, trace; %s" %
                      (e, traceback.format_exc()))
        finally:
            _socket.close()


# left to build
def thread_server():
    pass


def _default_app(environ, start_response):
    res = Response()
    res.content_type = "application/json"
    res.body = json.dumps({})
    res.status = "200 OK"
    response = res
    return response(environ, start_response)


# left to build
# class MyHttpProtocol(HttpProtocol):
#     pass
