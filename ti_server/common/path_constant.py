#! /usr/bin/env python
# -*-- coding: utf-8 -*-

import os


class PathConstant(object):
    # current work dir of all subprocess
    SUBPROCESS_ROOT = "/"

    # path of ti server log
    TI_SERVER_LOG = "/var/log/ti_server"

    # ti server root path
    TI_ROOT = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    # root path of tiDB test framework
    TI_SERVER_ROOT = os.path.join(TI_ROOT, "ti_server")
    # path of url mapping file
    REST_URL_MAPPING = os.path.join(TI_SERVER_ROOT, "rest_provider.json")

