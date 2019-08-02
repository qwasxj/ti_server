#! /usr/bin/env python
# -*-- coding: utf-8 -*-

import copy
import logging as log
import pymysql

from ti_server.common.path_constant import PathConstant
from configparser import ConfigParser
from configparser import NoSectionError
from configparser import NoOptionError


class TiDBService(object):
    TI_DB_SECTION = "TiDB"

    def __init__(self):
        self.ti_db_options = {
            "host": "127.0.0.1",
            "port": 4000,
            "user": "root",
            "password": "xj",
            "database": "test"
        }
        self.get_db_config()
        self.ti_db = pymysql.connect(
            host=self.ti_db_options["host"],
            port=int(self.ti_db_options["port"]),
            user=self.ti_db_options["user"],
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
