#! /usr/bin/env python
# -*-- coding: utf-8 -*-

import logging
import os
import traceback

from logging.handlers import RotatingFileHandler
from ti_server.common.path_constant import PathConstant


class Logger(object):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Logger, cls).__new__(cls)
            cls.instance.__init__()
        return cls.instance

    def __init__(self):
        self.logger = None
        self.file_handler = None

    def close_log(self):
        self.logger.removeHandler(self.file_handler)

    @classmethod
    def get_log_info(cls):
        stack = traceback.extract_stack()
        file_path = stack[-2][0]
        line = stack[-2][1]
        method = stack[-2][2]

        return file_path, line, method

    def info(self, msg=""):
        file_path, line, method = self.get_log_info()
        self.logger.info("[file:%s][line:%s][method:%s] :%s"
                         % (file_path, line, method, msg))

    def debug(self, msg=""):
        file_path, line, method = self.get_log_info()
        self.logger.debug("[file:%s][line:%s][method:%s] :%s"
                          % (file_path, line, method, msg))

    def warn(self, msg=""):
        file_path, line, method = self.get_log_info()
        self.logger.warning("[file:%s][line:%s][method:%s] :%s"
                            % (file_path, line, method, msg))

    def warning(self, msg=""):
        file_path, line, method = self.get_log_info()
        self.logger.warning("[file:%s][line:%s][method:%s] :%s"
                            % (file_path, line, method, msg))

    def error(self, msg=""):
        file_path, line, method = self.get_log_info()
        self.logger.error("[file:%s][line:%s][method:%s] :%s"
                          % (file_path, line, method, msg))

    def init(self, service):
        log_task = service
        log_path = PathConstant.TI_SERVER_LOG

        if not os.path.exists(log_path):
            os.makedirs(log_path)

        log_file = os.path.join(log_path, '%s.log' % log_task)
        formats = "%s %s" % ("%(asctime)s %(levelname)s",
                             "%(message)s")
        formatter = logging.Formatter(formats)
        _file_handler = RotatingFileHandler(
            log_file, maxBytes=1024*1024*20, backupCount=5)

        _file_handler.setFormatter(formatter)
        _logger = logging.getLogger(log_task)
        _logger.addHandler(_file_handler)
        _logger.setLevel(logging.INFO)

        self.logger = _logger
        self.file_handler = _file_handler


logger = Logger()
