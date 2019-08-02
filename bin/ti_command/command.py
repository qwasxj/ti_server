#! /usr/bin/env python
# -*-- coding: utf-8 -*-


from . import utils
from .log import logger as log

RIGHT_RESPONSE_CODE = [200 + code for code in range(100)]


@utils.arg("--workspace", metavar="<workspace>", required=True,
           help="specify user workspace to store log or config")
@utils.arg("--regex", metavar="<match string>", required=True,
           help="match sting to specify test instance position")
def do_run(proxy, args):
    log.info("start request to ti-server to execute test instance. workspace"
             ": %s, test match string: %s" % (args.workspace, args.regex))
    _code, body = proxy.ti_server_rest.auto_test(args.workspace, args.regex)
    if _code in RIGHT_RESPONSE_CODE:
        print("request to execute TiDB auto test successfully. you can view "
              "log in your workspace: %s" % args.workspace)
    else:
        print("request to ti-server failed. please view log in you workspace:"
              " %s for detail info" % args.workspace)
