#! /usr/bin/env python
# -*-- coding: utf-8 -*-

import copy
import logging as log
import pymysql

from ti_server.common.path_constant import PathConstant
from ConfigParser import ConfigParser
from ConfigParser import NoSectionError
from ConfigParser import NoOptionError


class TiDBService(object):
    TI_DB_SECTION = "TiDB"

    def __init__(self):
        self.ti_db_options = {
            "host": "",
            "port": "",
            "username": "",
            "password": "",
            "database": ""
        }
        self.get_db_config()
        self.ti_db = pymysql.connect(
            host=self.ti_db_options["host"],
            port=self.ti_db_options["port"],
            user=self.ti_db_options["username"],
            password=self.ti_db_options["password"],
            database=self.ti_db_options["database"]
        )

    def get_db_config(self):
        db_config = ConfigParser()
        db_config.read(PathConstant.TI_CONFIG)
        if not db_config.has_section(self.TI_DB_SECTION):
            log.error("There is not TiDB configuration in %s. section: %s" % (
                PathConstant.TI_CONFIG, self.TI_DB_SECTION
            ))
            raise NoSectionError(self.TI_DB_SECTION)
        for db_option in self.ti_db_options:
            if not db_config.has_option(self.TI_DB_SECTION, db_option):
                log.error("There is not option[%s] of TiDB configuration" % (
                    db_option
                ))
                raise NoOptionError(self.TI_DB_SECTION, db_option)
            self.ti_db_options[db_option] = \
                db_config.get(self.TI_DB_SECTION, db_option)
        return copy.deepcopy(self.ti_db_options)