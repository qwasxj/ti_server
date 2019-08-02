#! /usr/bin/env python
# -*-- coding: utf-8 -*-

import os
import sys
import time
import traceback

# add ti_server_path to sys path of subprocess
ti_server_path = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
if ti_server_path not in sys.path:
    sys.path.append(ti_server_path)

from ti_server.common.log import logger as log  # noqa
from ti_server.common.ti_base_func import BaseFun  # noqa
from ti_server.service_api.ti_db_api import TiDBService  # noqa
from ti_server.ti_db_tests.test_bank_transfer import TestBankTransfer  # noqa


class AutoTest(object):

    def __init__(self):
        pass

    @staticmethod
    def ti_test_run(workspace, match_string):
        log.info("begin to run ti test.. workspace: %s, match_string: %s" %
                 (workspace, match_string))
        self_call_cmd = "python3 %s %s %s" % (__file__, workspace, match_string)
        log.info("cmd: %s" % self_call_cmd)
        BaseFun.exe_cmd_demon(self_call_cmd)

    @staticmethod
    def start_cluster():
        """启动 tiDB 集群之前确保已经完成了前面的安装

        :return: None
        """

        start_cmd = "docker-compose up -d"

        code, output = BaseFun.exe_cmd(start_cmd)
        if code:
            log.info("execute cmd: %s to start tiDB cluster failed. code: "
                     "%s, error: %s" % (start_cmd, code, output[-1]))
            raise Exception(
                "execute cmd: %s to start tiDB cluster failed. code: %s, "
                "error: %s" % (start_cmd, code, output[-1])
            )

    @staticmethod
    def is_cluster_started(watch_time=60):
        watch_cmd = "netstat -apn | grep 4000"
        while watch_time:
            code, output = BaseFun.exe_cmd(watch_cmd)
            log.info("execute cmd: %s. code: %s, output: %s" %
                     (watch_cmd, code, output))
            if code:
                log.error(
                    "error occurred when detect whether cluster can connect "
                    "or not, code: %s, error: %s" % (code, output[-1])
                )
                raise Exception("error occurred when detect whether cluster "
                                "can connect or not")
            if "docker-proxy" in str(output[0]):
                log.info("tiDB cluster has been started...")
                return True
            watch_time -= 1
            time.sleep(1)
        log.info("tiDB cluster has not been started")
        return False

    @staticmethod
    def env_set(workspace, match_string):

        # set TiDB request object to global variable
        log.init("test", workspace)
        log.info("set env, workspace: %s, match_string: %s" % (
            workspace, match_string
        ))
        # start tiDB cluster when TiDB cluster is not started
        if not AutoTest.is_cluster_started(1):
            AutoTest.start_cluster()
        watch_time = 60
        if not AutoTest.is_cluster_started(watch_time):
            raise Exception("tiDB cluster has not started successfully after "
                            "%s s" % watch_time)

    @staticmethod
    def run_test(match_string):
        ti_db = TiDBService().ti_db
        log.info("get tiDB instance %s" % ti_db)
        log.info("start to run tiDB test instance %s" % match_string)
        try:
            test = TestBankTransfer(ti_db, log)
            test.setUp()
            test.test_bank_transfer()
            test.tearDown()
        except Exception as test_e:
            log.info("execute test %s failed. error: %s, trace: %s" % (
                match_string, test_e, traceback.format_exc()
            ))
        finally:
            ti_db.cursor().close()
            ti_db.close()
        

if __name__ == "__main__":
    log.init("ti-server")
    try:
        AutoTest.env_set(sys.argv[1], sys.argv[2])
        AutoTest.run_test(sys.argv[2])
    except Exception as e:
        log.error("execute tiDB test %s failed. error: %s trace: %s" % (
            sys.argv[2], e, traceback.format_exc()
        ))
