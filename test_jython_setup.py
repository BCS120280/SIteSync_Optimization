#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Jython 2.7 Test Script for Ignition Development
Tests basic Jython functionality and Java integration
"""

import sys
import os

# Initialize mock system if not available (for testing outside Ignition).
# Ignition injects `system` into the global namespace; outside Ignition we
# detect its absence and install a mock.
if 'system' not in globals():
	class MockPerspective:
		@staticmethod
		def print(*args):
			sys.stdout.write(" ".join(str(arg) for arg in args) + "\n")

	class MockSystem:
		perspective = MockPerspective()

		class tag:
			@staticmethod
			def readBlocking(paths):
				return [{"value": "mock_value", "quality": type('MockQuality', (), {'good': True})()}]

		class util:
			@staticmethod
			def getLogger(name):
				def log_info(msg):
					system.perspective.print("[INFO] {}".format(msg))
				return type('MockLogger', (), {'info': log_info})()

	system = MockSystem()

def test_basic_jython():
	"""Test basic Jython functionality"""
	system.perspective.print("=== Jython 2.7 Environment Test ===")
	system.perspective.print("Python version:", sys.version)
	system.perspective.print("Platform:", sys.platform)
	system.perspective.print("Jython check:", sys.platform.startswith('java'))

def test_java_integration():
	"""Test Java class imports and basic functionality"""
	try:
		system.perspective.print("\n=== Java Integration Test ===")

		# Test basic Java imports
		from java.lang import String
		from java.lang import Exception as JavaException
		from java.util import ArrayList

		system.perspective.print("OK Successfully imported Java classes")

		# Test Java object creation
		java_string = String("Hello from Jython!")
		system.perspective.print("OK Created Java String:", java_string)

		array_list = ArrayList()
		array_list.add("Item 1")
		array_list.add("Item 2")
		system.perspective.print("OK Created ArrayList with", array_list.size(), "items")

		# Test exception handling
		try:
			raise JavaException("Test exception")
		except JavaException as e:
			system.perspective.print("OK Exception handling works:", str(e))

	except ImportError as e:
		system.perspective.print("FAIL Java import failed:", str(e))
		return False
	except Exception as e:
		system.perspective.print("FAIL Java integration test failed:", str(e))
		return False

	return True

def test_ignition_simulation():
	"""Simulate basic Ignition-like functionality"""
	try:
		system.perspective.print("\n=== Ignition Simulation Test ===")

		# Mock system functions (since we don't have real Ignition)
		class MockPerspective:
			@staticmethod
			def print(*args):
				sys.stdout.write(" ".join(str(arg) for arg in args) + "\n")

		class MockSystem:
			perspective = MockPerspective()
			
			class tag:
				@staticmethod
				def readBlocking(paths):
					# Mock response
					return [{"value": "mock_value", "quality": type('MockQuality', (), {'good': True})()}]

			class util:
				@staticmethod
				def getLogger(name):
					def log_info(msg):
						system.perspective.print("[INFO] {}".format(msg))
					return type('MockLogger', (), {'info': log_info})()

		# Temporarily replace system if it doesn't exist
		if 'system' not in globals():
			global system
			system = MockSystem()

		system.perspective.print("OK Mock Ignition system functions available")

		# Test basic tag reading simulation
		result = system.tag.readBlocking(["test/path"])
		system.perspective.print("OK Tag reading simulation works")

		return True

	except Exception as e:
		system.perspective.print("FAIL Ignition simulation failed:", str(e))
		return False

def main():
	"""Main test function"""
	system.perspective.print("Starting Jython 2.7 environment verification...\n")

	test_basic_jython()

	java_ok = test_java_integration()
	ignition_ok = test_ignition_simulation()

	system.perspective.print("\n=== Test Results ===")
	system.perspective.print("Java Integration:", "PASS" if java_ok else "FAIL")
	system.perspective.print("Ignition Simulation:", "PASS" if ignition_ok else "FAIL")

	if java_ok and ignition_ok:
		system.perspective.print("\n[PASS] Jython 2.7 environment is ready for Ignition development!")
		return 0
	else:
		system.perspective.print("\n[FAIL] Some tests failed. Check the output above for details.")
		return 1

if __name__ == "__main__":
	sys.exit(main())