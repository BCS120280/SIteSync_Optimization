#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Smoke test for utils.debug under Jython 2.7. Run: ./jython.sh test_debug_helper.py"""

import os
import sys


def main():
	repo_root = os.path.dirname(os.path.abspath(__file__))
	sys.path.insert(0, os.path.join(repo_root, "ignition", "script-python", "utils", "debug"))

	import code as dbg

	print("=== utils.debug smoke test ===")
	print("Python version:", sys.version)
	print("stdin tty?:", sys.stdin.isatty() if hasattr(sys.stdin, "isatty") else "unknown")
	print("Calling dbg.brk() - expect (Pdb) prompt if tty, warning otherwise.")
	x = 42
	y = "hello from jython"
	dbg.brk()
	print("Resumed. x =", x, "y =", y)
	return 0


if __name__ == "__main__":
	sys.exit(main())
