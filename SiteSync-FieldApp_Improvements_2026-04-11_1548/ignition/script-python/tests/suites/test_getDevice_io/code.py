import tests.utils.utils as t
import tests.fixtures.fixtures as fix

def run():
	results = []

	# listDevices
	try:
		devices = device.get.listDevices(fix.TEST_TENANT_ID)
		results.append(t.assertIsInstance(devices, list, "listDevices returns list"))
	except Exception as e:
		results.append(t.safeTry(lambda: (_ for _ in ()).throw(e), "listDevices"))

	# getDevice -- nonexistent EUI returns error dict
	try:
		r = device.get.getDevice("0000000000000000")
		results.append(t.assertIn("status", r, "getDevice nonexistent has status key"))
		results.append(t.assertEqual(r["status"], "ERROR", "getDevice nonexistent status ERROR"))
	except Exception as e:
		results.append(t.safeTry(lambda: (_ for _ in ()).throw(e), "getDevice nonexistent"))

	# deviceLookup -- nonexistent EUI returns error dict
	try:
		r = device.get.deviceLookup("0000000000000000")
		results.append(t.assertIn("status", r, "deviceLookup nonexistent has status key"))
		results.append(t.assertEqual(r["status"], "ERROR", "deviceLookup nonexistent status ERROR"))
	except Exception as e:
		results.append(t.safeTry(lambda: (_ for _ in ()).throw(e), "deviceLookup nonexistent"))

	# getMetaData -- nonexistent returns empty dict (device not found -> no metaData key)
	try:
		r = device.get.getMetaData("0000000000000000")
		results.append(t.assertIsInstance(r, dict, "getMetaData nonexistent returns dict"))
	except Exception as e:
		results.append(t.safeTry(lambda: (_ for _ in ()).throw(e), "getMetaData nonexistent"))

	return results