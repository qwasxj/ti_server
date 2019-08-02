#! /usr/bin/env python
# -*-- coding: utf-8 -*-

from bin.ti_command.ti_server_rest import TiServerRest


class Proxy(object):

    def __init__(self, ti_server_url):
        """There can store different server rest objects

        :param ti_server_url:
        """
        self.ti_server_rest = TiServerRest(ti_server_url)
