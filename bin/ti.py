#! /usr/bin/env python
# -*-- coding: utf-8 -*-

import os
import sys

from .ti_command import shell

sys.path.append(os.path.dirname(os.path.realpath(__file__)))
shell.main("ti", "ti_command.proxy.Proxy", "ti_command.command")

