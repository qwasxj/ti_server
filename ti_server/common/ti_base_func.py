#! /usr/bin/env python
# -*-- coding: utf-8 -*-

import copy
import json
import os
import subprocess

from log import logger as log
from path_constant import PathConstant


class BaseFun(object):

    @staticmethod
    def __pre_func():
        os.umask(0)

    @staticmethod
    def exe_cmd(cmd, pid=False):
        pro = subprocess.Popen(
            args=cmd, shell=True, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, cwd=PathConstant.SUBPROCESS_ROOT,
            preexec_fn=BaseFun.__pre_func, close_fds=True
        )
        output = pro.communicate()
        code = pro.returncode
        if not pid:
            return code, output
        return pro.pid, code, output

    @staticmethod
    def com_read_file_with_json(file_name, mode="r", **kwargs):
        if not os.path.exists(file_name):
            log.warning('File <%s> not exist.' % file_name)
            if "default" in kwargs:
                return kwargs["default"]
            raise IOError("No such file or directory: %s" % file_name)

        with open(file_name, mode) as fp:
            json_body = json.load(fp)
        return json_body

    @staticmethod
    def com_write_file_with_json(file_name, json_body, mode="w+"):
        body = copy.deepcopy(json_body)
        with open(file_name, mode) as fp:
            fp.write(json.dumps(body))
        log.info('Save file <%s> success.' % file_name)
