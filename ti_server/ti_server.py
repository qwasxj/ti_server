#! /usr/bin/env python
# -*-- coding: utf-8 -*-

import argparse
import sys
import time
import traceback

from common.log import logger as log
from common.path_constant import PathConstant
from ti_rest_server import TiRestServer


class TiServer(object):

    NAME = "ti_server"

    def __init__(self):
        self.info = {
            "host": "127.0.0.1",
            "port": "8020"
        }

    def start_rest_server(self):
        log.info("start ti-server rest api to listen request.")
        ti_reset_server = \
            TiRestServer(self.NAME, self.info["host"], self.info["port"])
        ti_reset_server.start()

    def run(self):
        arg = init_options()
        log.info("ti-server enter argument: %s" % arg)
        if arg.host:
            self.info["host"] = arg.host
        if arg.port:
            self.info["port"] = arg.port
        self.start_rest_server()
        while True:
            time.sleep(10)


def init_options():
    parser = argparse.ArgumentParser()
    parser.add_argument("-host", "--host", metavar="", required=True,
                        help="ip of ti-server")
    parser.add_argument("-port", "--port", metavar="", required=True,
                        help="port of ti-server")
    parsed_args = parser.parse_args()
    return parsed_args


if __name__ == "__main__":
    log.init("ti-server")
    sys.path.append(PathConstant.TI_SERVER_ROOT)
    try:
        TiServer().run()
    except Exception as e:
        log.error("ti-server exit abnormal. error: %s, trace: %s"
                  % (e, traceback.format_exc()))
