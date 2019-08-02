#! /usr/bin/env python
# -*-- coding: utf-8 -*-

import os
import json
import ssl
import time
import traceback
import urllib.request as urllib2

from log import logger as log

RIGHT_RESPONSE_CODE = [200 + code for code in range(100)]


class RestSender(object):

    # can add method when request method not exists but need urllib2 to accept
    METHOD = ["GET", "POST", "PUT", "DELETE", "HEAD"]

    def __init__(self, str_url):
        self.str_url = str_url
        self.is_https = self.str_url.startswith("https")

    def _set_method(self, req, method):
        """Deal with request method, change request method to uppercase and
        judge method supported or not
        :param req: urllib2 request object, request
        :param method: str, request method before change
        :return: str, request method
        """
        req_method = method.upper()
        for method in self.METHOD:
            if method in req_method:
                req.get_method = lambda: method
                return
        raise HTTPException("Method not supported. method: %s" % req_method)

    def json_request(self, method, path, **kwargs):
        """Encapsulate urllib2 request to json request

        :param method: str, request method
        :param path: str, request path
        :param kwargs: tuple list, other specified arguments
        :return: tuple, (response, response body)
        """
        input_arg = dict()
        # set request headers
        headers = input_arg.setdefault("headers", dict())
        headers["Content-Type"] = "application/json"
        if "headers" in kwargs:
            headers.update(kwargs["headers"])

        # set request body
        if "body" in kwargs:
            input_arg["body"] = kwargs["body"]
        # set request transfer time
        if "timeout" in kwargs and kwargs["timeout"]:
            input_arg["timeout"] = kwargs["timeout"]
        else:
            input_arg["timeout"] = 180
        # set ssl validate path
        if self.is_https:
            if "verify" in kwargs:
                input_arg["verify"] = kwargs["verify"]
            else:
                input_arg["verify"] = False
        # set request url
        url = "".join([self.str_url, path])

        content = kwargs.get("body", {})
        if type(content) != dict:
            content = dict()

        log.info("Request... method: %s, url: %s, body: %s"
                 % (method, url, content))
        # request to upgrade service
        timeout_retry = 3
        res_code, res_data = None, None
        for i in range(timeout_retry):
            time.sleep(0.5)
            try:
                log.debug("rest call try cnt %d" % i)
                if self.is_https:
                    res_code, res_data = self.https_request(
                        method, url, **input_arg)
                else:
                    res_code, res_data = self.http_request(
                        method, url, **input_arg)
                if res_code in RIGHT_RESPONSE_CODE:
                    break
            except Exception as te:
                if i == timeout_retry - 1:
                    raise te
                else:
                    continue

        try:
            body = json.loads(res_data)
        except ValueError as e:
            log.warn("response body is json object. res body: %s" % res_data)
            raise e

        log.warn("code: %s, data: %s" % (res_code, body))
        return res_code, body

    def https_request(self, method, url, **kwargs):
        """Deal with http request use urllib2

        :param method: str, request method
        :param url: str, server url
        :param kwargs: tuple list, other specified arguments
        :return: urllib2 Response object, response
        """
        if (not method) or (not url):
            raise HTTPException("The input params is null.")
        # replace http protocol to https
        _url = url.strip()
        _url = _url.replace("http://", "https://", 1)
        # judge protocol is https or not
        if not _url.startswith("https://"):
            raise HTTPException("The url is illegal,url=%s." % url)
        req_param = dict()
        url_open_param = dict()
        req_param["url"] = url
        # set request headers
        req_param["headers"] = {"Content-Type": "application/json"}
        if "headers" in kwargs:
            req_param["headers"] = kwargs["headers"]
        # set request body
        if "body" in kwargs:
            if req_param["headers"]["Content-Type"] == "application/gzip":
                req_param["data"] = kwargs["body"]
            else:
                req_param["data"] = json.dumps(kwargs["body"])
        # build urllib2 Request object
        req = urllib2.Request(**req_param)
        self._set_method(req, method)
        # set max transfer time
        if "timeout" in kwargs:
            url_open_param["timeout"] = kwargs["timeout"]
        # judge verify exists or not
        if "verify" not in kwargs:
            raise HTTPException("The verify is null")
        # judge ssl verify file exists or not
        ca_path = kwargs["verify"]
        if not ca_path:
            url_open_param["context"] = ssl._create_unverified_context()
        elif self.is_file_exist(ca_path):
            url_open_param["context"] = ca_path
        else:
            raise HTTPException(
                "The verify is illegal . verify=%s " % ca_path
            )
        # request to server
        try:
            response = urllib2.urlopen(req, **url_open_param)
            res_code = response.code
            res_data = response.read()
        except urllib2.HTTPError as e:
            log.error("http error: %s" % traceback.format_exc())
            res_code = e.getcode()
            res_data = e.read()
        return res_code, res_data

    @staticmethod
    def is_file_exist(path):
        """Judge file exists or not

        :param path: str, file path
        :return: bool, True when file exists or False when not
        """
        # parameter validate
        if not isinstance(path, str) or not path:
            raise HTTPException(
                "fileIsExist failed .the input param is None.")
        # file exists
        if os.path.exists(path) and os.path.isfile(path):
            return True
        # file not exists
        return False

    def http_request(self, method, url, **kwargs):
        """Deal with http request use urllib2

        :param method: str, request method
        :param url: str, server url
        :param kwargs: tuple list, other specified arguments
        :return: urllib2 Response object, response
        """
        # judge method or url exists or not
        if (not method) or (not url):
            raise HTTPException("The input params is null.")
        # change https protocol to http protocol
        _url = url.strip()
        _url = _url.replace("https://", "http://", 1)
        if not _url.startswith("http://"):
            raise HTTPException("The url is illegal,url=%s." % url)
        req_param = dict()
        url_open_param = dict()
        req_param["url"] = url
        # set request headers
        req_param["headers"] = {"Content-Type": "application/json"}
        if "headers" in kwargs:
            req_param["headers"] = kwargs["headers"]
        # set request body
        if "body" in kwargs:
            if req_param["headers"]["Content-Type"] == "application/gzip":
                req_param["data"] = kwargs["body"]
            else:
                req_param["data"] = json.dumps(kwargs["body"])
        # build urllib2 Request object
        req = urllib2.Request(**req_param)
        self._set_method(req, method)
        # set max transfer time
        if "timeout" in kwargs:
            url_open_param["timeout"] = kwargs["timeout"]
        # request to server
        try:
            response = urllib2.urlopen(req, **url_open_param)
            res_code = response.code
            res_data = response.read()
        except urllib2.HTTPError as e:
            log.error("http error: %s" % traceback.format_exc())
            res_code = e.getcode()
            res_data = e.read()
        return res_code, res_data


class HTTPException(Exception):
    """Base HTTP exception.

    To correctly use this class, inherit from it and define
    a "message" property. That message with the keyword
    arguments provided to the constructor.
    """
    s_message = "An unknown exception occurred with http api"

    def __init__(self, message=None, **kwargs):
        if not message:
            message = self.s_message
        try:
            message = message % kwargs
        except (Exception,):
            # at least get the core message out if something happened
            pass

        super(HTTPException, self).__init__(message)
