#! /usr/bin/env python
# -*-- coding: utf-8 -*-

import json
import re
import sys
import traceback

from common.log import logger as log
from common.path_constant import PathConstant
from common.ti_base_func import BaseFun
from webob import Request
from webob import Response


class RestReqApp(object):

    CONTENT_TYPE = "application/json"

    def __init__(self):
        self.url_mapping = BaseFun.com_read_file_with_json(
            PathConstant.REST_URL_MAPPING
        )

    def __call__(self, environ, start_response):
        req = Request(environ)
        action = req.method
        url = req.path
        params = req.params

        if url == "/":
            res = Response()
            res.status = "200"
            res.content_type = self.CONTENT_TYPE
            return res(environ, start_response)

        log.info("Rest request! -> action: %s url: %s, params: %s" % (
            str(action), str(url), str(params)
        ))

        provider, method = self.get_provider_method(url)
        log.debug("provider: %s, method: %s" % (str(provider), str(method)))

        if provider is not None:
            response = self.__build_success_response(provider, method, environ)
        else:
            response = self.__build_failed_response(req)

        return response(environ, start_response)

    def get_provider_method(self, url):
        log.info("get request url mapping method, url: %s" % url)
        for item in self.url_mapping:
            provider = item["provider"]
            uri_list = item["uris"]
            for uri in uri_list:
                path = uri["uri"]
                p = re.compile(path)
                if p.match(url):
                    return provider, uri["method"]
        log.error("get provider of url: %s failed." % url)
        return None, None

    @staticmethod
    def import_object(class_path):
        module_str, sep, class_name = class_path.rpartition(".")
        log.info("xxjj: %s %s %s" % (module_str, sep, class_name))
        try:
            __import__(module_str)
            return getattr(sys.modules[module_str], class_name)()
        except (ValueError, AttributeError) as e:
            log.error("failed to import class: %s in file: %s, "
                      "error: %s, trace: %s" % (class_name, module_str, e,
                                                traceback.format_exc()))
            raise ImportError("Class: %s cannot be found in: %s" %
                              (class_name, module_str))

    @staticmethod
    def ex_func(obj, method, *args):
        return getattr(obj, method)(*args)

    def __build_success_response(self, class_path, method, environ):
        res = Response()
        res.content_type = self.CONTENT_TYPE
        try:
            obj = self.import_object(class_path)
            status, body = self.ex_func(obj, method, environ)
            log.info("the http status: %s" % status)

            res.body = json.dumps(body)
            res.status = status
        except Exception as e:
            res.status = "500"
            log.error("internal error, class: %s, method: %s, "
                      "error: %s, trace: %s" %
                      (class_path, method, e, traceback.format_exc()))
        return res

    def __build_failed_response(self, request):
        res = Response()
        log.error("unsupported request! request body: %s" % str(request.body))
        res.status = "400"
        res.content_type = self.CONTENT_TYPE
        return res
