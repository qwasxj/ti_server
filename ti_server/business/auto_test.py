#! /usr/bin/env python
# -*-- coding: utf-8 -*-

import __builtin__
import binascii
import json
import os
import sys

from ti_server.common.log import logger as log
from ti_server.common.ti_base_func import BaseFun
from ti_server.service_api.ti_db_api import TiDBService


class AutoTest(object):

    def __init__(self):
        pass

    @staticmethod
    def ti_test_run(workspace, match_string):
        args = {
            "workspace": workspace,
            "match_string": match_string
        }
        log.info("begin to run ti test.. argument: %s" % args)
        args = binascii.hexlify(json.dumps(args))
        self_call_cmd = "python %s %s" % (__file__, args)
        BaseFun.exe_cmd_demon(self_call_cmd)

    @staticmethod
    def env_set(workspace, match_string):

        # set TiDB request object to global variable
        __builtin__.__dict__["global_resource"] = dict()
        global_resource = __builtin__.__dict__["global_resource"]
        global_resource["TiDB"] = TiDBService().ti_db
        # set user workspace env
        log.init(os.path.join("root", workspace, "test"))
        # load tiDB test instance to sys environ
        paths = match_string.split(".")
        find_test_dir = "find / -empty -name %s"
        code, output = BaseFun.exe_cmd(find_test_dir)
        if code:
            log.error("find tiDB test dir specified failed. code: %s, error: "
                      "%s" % (code, output[-1]))
            raise Exception("find tiDB test dir failed.")
        dirs = output[0].split("\n")
        match_dirs = [t_dir for t_dir in dirs if paths[0] in t_dir]
        if not match_string:
            raise Exception("you just specified an error match string.")
        match_t = os.path.dirname(match_dirs[0])
        while paths:
            temp_t = os.path.join(match_t, paths[0])
            if os.path.isdir(temp_t) or os.path.isfile(temp_t):
                match_t = temp_t
                sys.path.append(match_t)
                paths = paths[1:]
            else:
                break
        # # a dir or an file the match string specified
        # if not paths and os.path.isdir(match_t):
        #     tests = AutoTest.load_all_files_tests(match_t)
        # elif not paths and os.path.isdir(match_t):
        #     tests = AutoTest.load_some_file_test(match_t)
        # # an class the match string specified
        # elif len(paths) == 1:
        #     tests = AutoTest.load_some_class_tests(match_t, paths)
        # elif len(paths) == 2:
        #     tests = AutoTest.load_some_class_test(match_t, paths)
        pass
        
        
    # @staticmethod
    # def load_all_files_tests(path):
    #     t_files = os.listdir(path)
    #     tests = list()
    #     for t_file in t_files:
    #         tests.extend(AutoTest.load_some_files_test(t_file))
    #     return tests
    #
    # @staticmethod
    # def load_some_files_test(path):
    #     return

    @staticmethod
    def run_test(match_string):
        # log.info("start to run tiDB test instance %s" % match_string)
        pass


if __name__ == "__main__":
    arg = json.loads(binascii.unhexlify((sys.argv[1])))
    log.info("xxxxxxxxxxxxxxxxxxxxxxx: %s" % arg)
    AutoTest.env_set(arg.get("workspace"), arg.get("match_string"))
    AutoTest.run_test(arg.get("match_string"))

