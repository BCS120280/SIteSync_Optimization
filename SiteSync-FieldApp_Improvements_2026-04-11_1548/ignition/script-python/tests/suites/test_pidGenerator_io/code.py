import tests.utils.utils as t
import tests.fixtures.fixtures as fix

def run():
	results = []

	# getDeviceTypeFromProfile -- requires live decoders.model.getModel
	try:
		dtype = device.pidGenerator.getDeviceTypeFromProfile(fix.TEST_MODEL_ID)
		if dtype is not None:
			results.append(t.assertIsInstance(dtype, str, "getDeviceTypeFromProfile returns string"))
		else:
			results.append(t.skip("getDeviceTypeFromProfile", "model has no device_type"))
	except Exception as e:
		results.append(t.safeTry(lambda: (_ for _ in ()).throw(e), "getDeviceTypeFromProfile"))

	# getDeviceTypeFromProfile -- None modelID
	try:
		dtype = device.pidGenerator.getDeviceTypeFromProfile(None)
		results.append(t.assertIsNone(dtype, "getDeviceTypeFromProfile(None) returns None"))
	except Exception as e:
		results.append(t.safeTry(lambda: (_ for _ in ()).throw(e), "getDeviceTypeFromProfile None"))

	# getDeviceTypeFromProfile -- -1
	try:
		dtype = device.pidGenerator.getDeviceTypeFromProfile(-1)
		results.append(t.assertIsNone(dtype, "getDeviceTypeFromProfile(-1) returns None"))
	except Exception as e:
		results.append(t.safeTry(lambda: (_ for _ in ()).throw(e), "getDeviceTypeFromProfile -1"))

	# getSiteNameFromTenant
	try:
		name = device.pidGenerator.getSiteNameFromTenant(fix.TEST_TENANT_ID)
		if name is not None:
			results.append(t.assertIsInstance(name, str, "getSiteNameFromTenant returns string"))
			results.append(t.assertNotIn(" ", name, "getSiteNameFromTenant replaces spaces"))
		else:
			results.append(t.skip("getSiteNameFromTenant", "tenant not found"))
	except Exception as e:
		results.append(t.safeTry(lambda: (_ for _ in ()).throw(e), "getSiteNameFromTenant"))

	# getSiteNameFromTenant -- None
	try:
		name = device.pidGenerator.getSiteNameFromTenant(None)
		results.append(t.assertIsNone(name, "getSiteNameFromTenant(None) returns None"))
	except Exception as e:
		results.append(t.safeTry(lambda: (_ for _ in ()).throw(e), "getSiteNameFromTenant None"))

	# getNextLoopNumber -- reads/writes [PID Loops] tag, may not exist
	# Skip if tag provider doesn't exist to avoid errors
	results.append(t.skip(
		"getNextLoopNumber",
		"Skipped: requires PID Loops tag provider to be configured"
	))

	# generatePidName -- requires getNextLoopNumber to work
	results.append(t.skip(
		"generatePidName",
		"Skipped: depends on getNextLoopNumber (PID Loops tags)"
	))

	return results