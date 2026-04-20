#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Smoke test for utils.debug under Jython 2.7. Run: ./jython.sh test_debug_helper.py"""

import os
import sys


def log(msg):
	system.perspective.print(msg)


def main():
	repo_root = os.path.dirname(os.path.abspath(__file__))
	sys.path.insert(0, os.path.join(repo_root, "ignition", "script-python", "utils", "debug"))

	import code as dbg

	log("=== utils.debug smoke test ===")
	log("Python version: {}".format(sys.version))
	log("stdin tty?: {}".format(sys.stdin.isatty() if hasattr(sys.stdin, "isatty") else "unknown"))
	log("Calling dbg.brk() - expect (Pdb) prompt if tty, warning otherwise.")
	x = 42
	y = "hello from jython"
	dbg.brk()
	log("Resumed. x = {} y = {}".format(x, y))
	return 0


if __name__ == "__main__":
	sys.exit(main())
