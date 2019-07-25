#! /usr/bin/env python
# -*-- coding: utf-8 -*-


class FiAutoTest(object):

    def __init__(self):
        pass

    def fi_auto_test_request(self, environ):
        return "200", {"code": 200, "data": [1, 2, 3, 4]}

