import tests.utils.utils as t
import tests.fixtures.fixtures as fix

def run():
	results = []
	bv2 = device.bulkuploadV2

	# --- pathValidator ---
	results.append(t.assertTrue(bv2.pathValidator("Devices/Site1"), "pathValidator valid"))
	results.append(t.assertTrue(bv2.pathValidator("A_folder/B"), "pathValidator underscores"))
	results.append(t.assertFalse(bv2.pathValidator("$bad"), "pathValidator rejects $"))
	results.append(t.assertTrue(bv2.pathValidator(None), "pathValidator None -> True"))
	results.append(t.assertTrue(bv2.pathValidator(""), "pathValidator empty -> True"))

	# --- validator ---
	results.append(t.assertTrue(bv2.validator("FFFF000000000001", 16), "validator 16 chars"))
	results.append(t.assertTrue(bv2.validator("FFFF-0000-0000-0001", 16), "validator strips dashes"))
	results.append(t.assertTrue(bv2.validator("FFFF 0000 0000 0001", 16), "validator strips spaces"))
	results.append(t.assertFalse(bv2.validator("short", 16), "validator too short"))
	results.append(t.assertFalse(bv2.validator("", 16), "validator empty"))

	# --- validatorReturnValue ---
	results.append(t.assertEqual(
		bv2.validatorReturnValue("FFFF000000000001", 16, "dev_eui"),
		"ffff000000000001",
		"validatorReturnValue valid returns lowercased"
	))
	r = bv2.validatorReturnValue("short", 16, "dev_eui")
	results.append(t.assertContains(r, "dev_eui", "validatorReturnValue invalid mentions field name"))
	results.append(t.assertContains(r, "16", "validatorReturnValue invalid mentions expected length"))

	# --- canUpload ---
	results.append(t.assertTrue(bv2.canUpload("Device can be uploaded"), "canUpload success message"))
	results.append(t.assertFalse(bv2.canUpload("some error"), "canUpload error message"))
	results.append(t.assertFalse(bv2.canUpload(""), "canUpload empty"))

	# --- deviceChecker ---
	results.append(t.assertEqual(
		bv2.deviceChecker({"deviceType": "TEPressure"}, "Fallback"),
		"TEPressure",
		"deviceChecker uses row deviceType"
	))
	results.append(t.assertEqual(
		bv2.deviceChecker({"deviceType": ""}, "Fallback"),
		"Fallback",
		"deviceChecker empty falls back"
	))
	results.append(t.assertEqual(
		bv2.deviceChecker({}, "Fallback"),
		"Fallback",
		"deviceChecker missing key falls back"
	))

	# --- deviceIDChecker -- KNOWN_DEFECT ---
	results.append(t.knownDefect(
		"deviceIDChecker references undefined variables",
		"deviceIDChecker references 'modelName' and 'deviceName' which are undefined"
	))

	# --- getSpecialColumns ---
	cols = bv2.getSpecialColumns()
	results.append(t.assertIn("dev_eui", cols, "getSpecialColumns has dev_eui"))
	results.append(t.assertIn("app_key", cols, "getSpecialColumns has app_key"))
	results.append(t.assertIn("join_eui", cols, "getSpecialColumns has join_eui"))
	results.append(t.assertIn("name", cols, "getSpecialColumns has name"))
	results.append(t.assertNotIn("custom_col", cols, "getSpecialColumns excludes custom_col"))

	# --- formatMetaData ---
	row = {
		"dev_eui": "FFFF000000000001",
		"name": "Test",
		"custom_field": "val1",
		"install_notes": "val2",
		"description": "",
	}
	meta = bv2.formatMetaData(row)
	results.append(t.assertIn("custom_field", meta, "formatMetaData includes custom_field"))
	results.append(t.assertIn("install_notes", meta, "formatMetaData includes install_notes"))
	results.append(t.assertNotIn("dev_eui", meta, "formatMetaData excludes dev_eui"))
	results.append(t.assertNotIn("name", meta, "formatMetaData excludes name"))
	# Empty values excluded
	results.append(t.assertNotIn("description", meta, "formatMetaData excludes empty values"))

	# --- formatName ---
	# Name provided
	results.append(t.assertEqual(
		bv2.formatName({"name": "MyDevice", "dev_eui": "1234567890123456"}),
		"MyDevice",
		"formatName uses provided name"
	))
	# Name with whitespace
	results.append(t.assertEqual(
		bv2.formatName({"name": "  MyDevice  ", "dev_eui": "1234"}),
		"MyDevice",
		"formatName strips whitespace"
	))
	# Name empty -- auto-generate
	results.append(t.assertEqual(
		bv2.formatName({"name": "", "deviceType": "Pressure", "dev_eui": "FFFF000000000001"}),
		"Pressure0001",
		"formatName auto-generates from type + last4"
	))
	# Name missing -- auto-generate
	results.append(t.assertEqual(
		bv2.formatName({"deviceType": "Temp", "dev_eui": "FFFF000000000001"}),
		"Temp0001",
		"formatName auto-generates when name key missing"
	))
	# Short devEUI
	results.append(t.assertEqual(
		bv2.formatName({"name": "", "deviceType": "X", "dev_eui": "AB"}),
		"XAB",
		"formatName short devEUI concatenated"
	))

	# --- getDeviceModelID ---
	profiles = fix.SAMPLE_PROFILE_LIST
	# Row has deviceType matching profile
	results.append(t.assertEqual(
		bv2.getDeviceModelID(99, {"deviceType": "TEPressure"}, profiles),
		1,
		"getDeviceModelID finds profile by name"
	))
	# Row deviceType empty -- uses form selection
	results.append(t.assertEqual(
		bv2.getDeviceModelID(99, {"deviceType": ""}, profiles),
		99,
		"getDeviceModelID falls back to selectedDeviceProfileID"
	))
	# Row deviceType not in profiles
	results.append(t.assertEqual(
		bv2.getDeviceModelID(99, {"deviceType": "Unknown"}, profiles),
		-1,
		"getDeviceModelID not found returns -1"
	))

	# --- getDeviceModel ---
	# Row has deviceType
	results.append(t.assertEqual(
		bv2.getDeviceModel(1, {"deviceType": "CustomType"}, profiles),
		"CustomType",
		"getDeviceModel uses row deviceType"
	))
	# Row deviceType empty -- look up by ID
	results.append(t.assertEqual(
		bv2.getDeviceModel(1, {"deviceType": ""}, profiles),
		"TEPressure",
		"getDeviceModel looks up by ID"
	))
	# Row deviceType empty -- ID not found
	r = bv2.getDeviceModel(999, {"deviceType": ""}, profiles)
	results.append(t.assertContains(r, "not found", "getDeviceModel ID not found"))

	# --- deviceParserStatus ---
	good_device = {
		"dev_eui_valid": True, "dev_eui": "ffff000000000001",
		"app_key_valid": True, "app_key": "00112233445566778899aabbccddeeff",
		"join_eui_valid": True, "join_eui": "0000000000000000",
		"tagPath": "ValidPath", "name": "ValidName",
	}
	results.append(t.assertEqual(
		bv2.deviceParserStatus(good_device),
		"Device can be uploaded",
		"deviceParserStatus all valid"
	))

	bad_device = {
		"dev_eui_valid": False, "dev_eui": "bad eui error",
		"app_key_valid": False, "app_key": "bad key error",
		"join_eui_valid": True, "join_eui": "0000000000000000",
		"tagPath": "ValidPath", "name": "ValidName",
	}
	status = bv2.deviceParserStatus(bad_device)
	results.append(t.assertContains(status, "bad eui error", "deviceParserStatus includes eui error"))
	results.append(t.assertContains(status, "bad key error", "deviceParserStatus includes key error"))

	return results