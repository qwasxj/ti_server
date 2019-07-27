#! /usr/bin/env python
# -*-- coding: utf-8 -*-

import json
import traceback

from ti_server.business.auto_test import AutoTest
from ti_server.common.log import logger as log
from ti_server.common.http_constant import HttpConstant
from webob import Request


class FiAutoTest(object):

    FAIL = "Request to run tempest failed with"

    def __init__(self):
        pass

    def ti_auto_test_request(self, environ):
        req = Request(environ)
        action = req.method
        if action == "POST":
            # request body invalid
            try:
                request_body = json.loads(req.body)
                workspace = request_body["workspace"]
                match_string = request_body["match_string"]
                if not match_string:
                    raise Exception("has not specified tiDB test match string.")
                if not workspace:
                    raise Exception("has not specified tiDB workspace.")
            except Exception as e:
                message = "%s request body invalid. body: %s" % \
                          (self.FAIL, req.body)
                log.error("%s, error: %s, trace: %s" %
                          (message, e, traceback.format_exc()))
                return HttpConstant.CODE500, {"code": 500, "message": message}
            try:
                AutoTest.ti_test_run(workspace, match_string)
            except Exception as e:
                message = "%s ti-server internal error." % self.FAIL
                log.error("%s, error: %s, trace: %s" %
                          (message, e, traceback.format_exc()))
                return HttpConstant.CODE500, {"code": 500, "message": message}
            message = "start to run tiDB auto test instance: %s, log " \
                      "dir path: %s" % (match_string, workspace)
            log.info(message)
            return HttpConstant.CODE200, {"code": 200, "message": message}
        else:
            message = "Request to run tempest failed with api not supported"
            log.error(message)
            return HttpConstant.CODE500, {"code": 500, "message": message}

