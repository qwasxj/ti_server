#! /usr/bin/env python
# -*-- coding: utf-8 -*-

from rest_util import RestSender


class TiServerRest(object):

    # ti-server request method
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DEL = "DELETE"

    # ti-server path supplied of TiServerRest, Can extend the request
    TI_AUTO_TEST = "/ti/v1/auto_test"

    def __init__(self, ti_server_url):
        self.rest = RestSender(ti_server_url)

    def auto_test(self, workspace, match_string):

        request_body = {
            "workspace": workspace,
            "match_string": match_string
        }
        code, body = self.rest.json_request(
            self.POST, self.TI_AUTO_TEST, body=request_body
        )
        return code, body
