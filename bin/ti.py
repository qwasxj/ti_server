#! /usr/bin/env python
# -*-- coding: utf-8 -*-

import os
import sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)))

from bin.ti_command import shell  # noqa

shell.main("ti", "ti_command.proxy.Proxy", "ti_command.command")

