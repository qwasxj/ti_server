#! /usr/bin/env python
# -*-- coding: utf-8 -*-

import __builtin__
import binascii
import json
import os
import sys

from ti_server.common.log import logger as log
from ti_server.common.ti_base_func import BaseFun
from ti_server.service_api.ti_db_api import TiDBService


class AutoTest(object):

    def __init__(self):
        pass

    @staticmethod
    def ti_test_run(workspace, match_string):
        args = {
            "workspace": workspace,
            "match_string": match_string
        }
        log.info("begin to run ti test.. argument: %s" % args)
        args = binascii.hexlify(json.dumps(args))
        self_call_cmd = "python %s %s" % (__file__, args)
        BaseFun.exe_cmd_demon(self_call_cmd)

    @staticmethod
    def env_set(workspace):

        # set TiDB request object to global variable
        __builtin__.__dict__["global_resource"] = dict()
        global_resource = __builtin__.__dict__["global_resource"]
        global_resource["TiDB"] = TiDBService().ti_db
        # set user workspace env
        log.init(os.path.join(workspace, "test.log"))

    @staticmethod
    def run_test(match_string):
        # log.info("start to run tiDB test instance %s" % match_string)
        pass


if __name__ == "__main__":
    arg = json.loads(binascii.unhexlify((sys.argv[1])))
    log.info("xxxxxxxxxxxxxxxxxxxxxxx: %s" % arg)
    AutoTest.env_set(arg.get("workspace"))
    AutoTest.run_test(arg.get("match_string"))

