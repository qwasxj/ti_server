#! /usr/bin/env python
# -*-- coding: utf-8 -*-

import argparse
import os
import sys
import traceback
import utils

from configparser import ConfigParser
from configparser import NoOptionError
from configparser import NoSectionError

from log import logger as log


class Shell(object):

    TI_SERVER_SECTION = "TiServer"
    TI_CONFIG = os.path.join(os.path.dirname(os.path.dirname(
        os.path.dirname(__file__))), "config", "ti_server.ini"
    )

    def __init__(self):
        self.argv = None
        self.parser = None
        self.subcommands = dict()
        self.ti_server_info = {
            "host": "localhost",
            "port": "8020"
        }
        self.ti_server_url = ""

    def get_parser(self, prog, command):

        parser = argparse.ArgumentParser(
            prog=prog, add_help=False,
            epilog="See '%s help command' for help "
                   "on a specific command." % prog,
        )
        parser.add_argument("-h", "--help", action="help",
                            help=argparse.SUPPRESS)
        parser.add_argument("-d", "--debug", action="store_true",
                            default=False, help="Debug switch")

        __import__(command)
        subparsers = parser.add_subparsers(metavar='<subcommand>')
        self._find_actions(subparsers, sys.modules[command])
        self._find_actions(subparsers, self)
        return parser

    def _find_actions(self, subparsers, actions_mod):
        for attr in [act for act in dir(actions_mod) if act.startswith("do_")]:
            command = attr[3:].replace("_", "-")
            callback = getattr(actions_mod, attr)
            desc = callback.__doc__ or ""
            help = desc.strip().split("\n")[0]
            arguments = getattr(callback, "arguments", [])

            sub_parser = subparsers.add_parser(
                command, help=help, description=desc, add_help=False
            )
            sub_parser.add_argument(
                "-h", "--help", action="help", help=argparse.SUPPRESS
            )
            self.subcommands[command] = subparsers
            for arg in arguments:
                if callable(arg):
                    arg(sub_parser)
                else:
                    sub_parser.add_argument(*arg[0], **arg[1])
            sub_parser.set_defaults(func=callback)

    @utils.arg("command", metavar="<subcommand>", nargs="?",
               help="Display help for <subcommand>")
    def do_help(self, args):
        if getattr(args, "command", None):
            if args.command in self.subcommands:
                self.subcommands[args.command].print_help()
            else:
                raise Exception("command of args not supported. command: %s, "
                                "args: %s" % (args.command, args))
        else:
            self.parser.print_help()

    def main(self, arg, prog, class_name, command):

        # load ti-server info
        self.__load_config(self.TI_CONFIG)

        self.argv = arg
        self.parser = self.get_parser(prog, command)

        if not arg:
            self.do_help([])
            return 0

        args = self.parser.parse_args(arg)

        if args.func == self.do_help:
            self.do_help(args)
            return 0

        sys.path.append(os.path.split(os.path.split(
            os.path.realpath(__file__))[0])[0])
        module_name, class_name = class_name.rsplit('.', 1)
        __import__(module_name)
        module_meta = sys.modules[module_name]
        proxy = getattr(module_meta, class_name)(self.ti_server_url)
        try:
            args.func(proxy, args)
        except Exception as e:
            log.error("execute cmd: %s failed. error: %s, trace: %s" % (
                "%s %s" % (prog, args.func.__name__), e, traceback.format_exc()
            ))
            print("execute cmd: %s failed. error: %s, trace: %s" % (
                "%s %s" % (prog, args.func.__name__), e, traceback.format_exc()
            ))

    def __load_config(self, config):
        if not os.path.exists(config):
            log.error("ti server configuration file not exist. "
                      "path: %s" % config)
            raise Exception("ti server configuration file not exist. "
                            "path: %s" % config)
        log.info("ti-server config path: %s" % config)
        ti_config = ConfigParser()
        ti_config.read(config)
        if not ti_config.has_section(self.TI_SERVER_SECTION):
            log.error("there is not ti server configuration in config "
                      "file: %s" % config)
            raise NoSectionError(self.TI_SERVER_SECTION)
        for option in self.ti_server_info:
            if not ti_config.has_option(self.TI_SERVER_SECTION, option):
                log.error("there is not ti server %s in config "
                          "file: %s" % (option, config))
                raise NoOptionError(option, self.TI_SERVER_SECTION)
            self.ti_server_info[option] = \
                ti_config.get(self.TI_SERVER_SECTION, option)
        self.ti_server_url = "http://%s:%s" % (
            self.ti_server_info["host"], self.ti_server_info["port"]
        )


def main(prog, class_name, command):
    try:
        workspace_path = ""
        try:
            workspace_index = sys.argv.index("--workspace")
            workspace_path = sys.argv[workspace_index + 1]
        except ValueError as e:
            log.error("not an ti run command. workspace set as: %s, error: "
                      "%s" % (workspace_path, e))
        log_path = os.path.join("/root/", workspace_path, "test")
        log.init(log_path)
        sys.exit(Shell().main(sys.argv[1:], prog, class_name, command))
    except Exception as e:
        print("error occurred when execute cmd, error: %s, trace: %s" %
              (e, traceback.format_exc()))
        exit(1)
