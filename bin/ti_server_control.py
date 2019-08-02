#! /usr/bin/env python
# -*-- coding: utf-8 -*-

import argparse
import fcntl
import os
import sys
import subprocess
import traceback

from configparser import ConfigParser
from configparser import NoOptionError
from configparser import NoSectionError

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from bin.ti_command.log import logger as log  # noqa


class TiServerControl(object):
    """
    Used to start or stop TiDB auto test Framework
    """

    SUBPROCESS_ROOT = "/"
    ACTION_LIST = ["start", "stop", "restart"]
    TI_SERVER_SECTION = "TiServer"
    # ti server root path
    TI_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # path of tiDB framework control script
    TI_CTL_LOCK = os.path.join(TI_ROOT, "ti_server_ctl_lock")
    # path of ti server pid file
    TI_SERVER_PID = os.path.join(TI_ROOT, "ti_server_pid")
    # root path of tiDB test framework
    TI_SERVER_ROOT = os.path.join(TI_ROOT, "ti_server")

    def __init__(self, server_path, server):
        self.ti_server_path = os.path.join(server_path, server)
        self.ti_server_info = {
            "host": "localhost",
            "port": "8020"
        }

    @staticmethod
    def __pre_func():
        os.umask(0)

    @staticmethod
    def __exe_cmd(cmd, pid=False):
        pro = subprocess.Popen(
            args=cmd, shell=True, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, cwd=TiServerControl.SUBPROCESS_ROOT,
            preexec_fn=TiServerControl.__pre_func, close_fds=True
        )
        output = pro.communicate()
        code = pro.returncode
        if not pid:
            return code, output
        return pro.pid, code, output

    def __start_ti_server(self):
        log.info("begin to start ti-server..")
        with open(TiServerControl.TI_CTL_LOCK, "r+") as fd:
            fcntl.flock(fd.fileno(), fcntl.LOCK_EX)
            is_run = self.is_ti_server_run()
            if is_run:
                log.info("ti server is run, exist ti_server_control")
            else:
                start_cmd = "python3 %s" % self.ti_server_path
                for arg, value in self.ti_server_info.items():
                    start_cmd = "%s -%s %s" % (start_cmd, arg, value)
                log.info("run ti-server start cmd: %s" % start_cmd)
                pro = subprocess.Popen(start_cmd, close_fds=True, shell=True)
                self.set_ti_server_pid(pro.pid)
                log.info("start ti server successfully for: %s" %
                         self.ti_server_path)

    def __stop_ti_server(self):
        log.info("begin to stop ti-server..")
        with open(TiServerControl.TI_CTL_LOCK, "r+") as fd:
            fcntl.flock(fd.fileno(), fcntl.LOCK_EX)
            is_run = self.is_ti_server_run()
            if not is_run:
                log.info("ti server is not run, exist ti_server_control")
            else:
                ti_server_pid = self.get_ti_server_pid()
                kill_cmd = "kill -9 %s" % ti_server_pid
                code, output = self.__exe_cmd(kill_cmd)
                if code:
                    log.error("ti server stop failed, code: %s, output: "
                              "%s" % (code, output))
                    raise Exception(output[-1])
                if os.path.exists(self.TI_SERVER_PID):
                    os.remove(self.TI_SERVER_PID)
                log.info("ti server stop successfully.")

    @staticmethod
    def is_ti_server_run():
        if not os.path.exists(TiServerControl.TI_SERVER_PID):
            return False
        with open(TiServerControl.TI_SERVER_PID, "r+") as ti_pid:
            pid = ti_pid.read()
        cmdline_path = "/proc/%s/cmdline" % pid
        if not os.path.exists(cmdline_path):
            return False
        with open(cmdline_path, "r+") as fs_cmdline:
            cmdline_info = fs_cmdline.read()
        if not cmdline_info:
            return False
        return True

    def get_ti_server_pid(self):
        if not self.is_ti_server_run():
            return ""
        with open(TiServerControl.TI_SERVER_PID, "r+") as ti_pid:
            pid = ti_pid.read()
        return pid

    def set_ti_server_pid(self, pid):
        with open(self.TI_SERVER_PID, "w+") as fd_pid:
            fd_pid.write(str(pid))
            log.info("write ti-server pid to pid file: %s. pid: %s"
                     % (self.TI_SERVER_PID, pid))

    def operate_ti_server(self, action):
        if action == "start":
            self.__start_ti_server()

        elif action == "stop":
            self.__stop_ti_server()

        else:
            self.__stop_ti_server()
            self.__start_ti_server()

    def __load_config(self, config):
        if not os.path.exists(config):
            raise Exception("ti server configuration file not exist. "
                            "path: %s" % config)
        log.info("ti-server config path: %s" % config)
        ti_config = ConfigParser()
        ti_config.read(config)
        if not ti_config.has_section(self.TI_SERVER_SECTION):
            log.info("there is not ti server configuration in config "
                     "file: %s" % config)
            raise NoSectionError(self.TI_SERVER_SECTION)
        for option in self.ti_server_info:
            if not ti_config.has_option(self.TI_SERVER_SECTION, option):
                log.info("there is not ti server %s in config "
                         "file: %s" % (option, config))
                raise NoOptionError(option, self.TI_SERVER_SECTION)
            self.ti_server_info[option] = \
                ti_config.get(self.TI_SERVER_SECTION, option)

    def run(self):
        args = init_options()
        log.info("input argument: %s" % args)
        if args.config:
            self.__load_config(args.config)
        if args.action:
            action = args.action.lower()
            if action not in self.ACTION_LIST:
                log.error("action to control ti-server invalid.")
                raise Exception("Action to control ti-server invalid.")
            self.operate_ti_server(action)

    @staticmethod
    def change_group_own(_path):
        code, output = TiServerControl.__exe_cmd(
            "sudo -n chgrp ${USER} -R %s" % _path
        )
        if code:
            log.error("Change group of %s failed." % _path)
        log.info("Change group of %s successfully.")
        return code


def init_options():
    parser = argparse.ArgumentParser()
    subparsers = \
        parser.add_subparsers(metavar="<subcommand>", dest="command_name")
    command, help_info = "control", "control ti-server",
    parser_sub = subparsers.add_parser(command, help=help_info)
    parser_sub.add_argument("-a", "--action", metavar="", required=True,
                            help="Action to control ti-server")
    parser_sub.add_argument("-c", "--config", metavar="", required=True,
                            help="configuration file of ti-server")
    parsed_args = parser.parse_args()
    return parsed_args


if __name__ == "__main__":
    log.init("ti_server_control")

    ti_server = "ti_server_process.py"
    ti_server_root = TiServerControl.TI_SERVER_ROOT
    log.info("ti_server_root: %s, ti_server: %s" % (ti_server_root, ti_server))

    if not os.path.exists(TiServerControl.TI_CTL_LOCK):
        with open(TiServerControl.TI_CTL_LOCK, "w"):
            TiServerControl.change_group_own(TiServerControl.TI_CTL_LOCK)

    try:
        ti_server_ctl = TiServerControl(ti_server_root, ti_server)
        ti_server_ctl.run()
    except Exception as e:
        log.error("operate ti-server failed. error: %s, trace: %s" %
                  (e, traceback.format_exc()))
