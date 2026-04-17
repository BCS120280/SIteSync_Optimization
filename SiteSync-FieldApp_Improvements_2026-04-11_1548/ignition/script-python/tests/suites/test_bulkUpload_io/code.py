import json
import tests.utils.utils as t
import tests.fixtures.fixtures as fix

def _cleanup():
	for eui in [fix.TEST_DEVEUI_01]:
		try:
			system.sitesync.archiveDevice(eui)
		except:
			pass

def run():
	results = []
	_cleanup()

	# formatMetaData (pure)
	row = {"dev_eui": "AAA", "name": "X", "custom1": "val1", "custom2": "", "deviceType": "T"}
	meta = device.bulkUpload.formatMetaData(row)
	results.append(t.assertIn("custom1", meta, "V1 formatMetaData includes custom1"))
	results.append(t.assertNotIn("dev_eui", meta, "V1 formatMetaData excludes dev_eui"))
	results.append(t.assertNotIn("custom2", meta, "V1 formatMetaData excludes empty"))

	# formatName (pure)
	results.append(t.assertEqual(
		device.bulkUpload.formatName({"name": "MyDev"}),
		"MyDev",
		"V1 formatName uses provided name"
	))
	results.append(t.assertEqual(
		device.bulkUpload.formatName({"deviceType": "Pressure", "dev_eui": "1234567890123456"}),
		"Pressure3456",
		"V1 formatName auto-generates"
	))

	# charCheck (pure)
	results.append(t.assertTrue(device.bulkUpload.charCheck("1234567890123456", 16), "V1 charCheck pass"))
	results.append(t.assertFalse(device.bulkUpload.charCheck("short", 16), "V1 charCheck fail"))

	# generateTagPath (stub)
	results.append(t.assertEqual(
		device.bulkUpload.generateTagPath("model", "tenant", []),
		"model",
		"V1 generateTagPath returns model (stub)"
	))

	# uploadLine -- I/O test with valid row
	try:
		profiles = decoders.model.listDeviceProfiles(fix.TEST_TENANT_ID)
		if len(profiles) > 0:
			row = {
				"dev_eui": fix.TEST_DEVEUI_01,
				"join_eui": fix.VALID_JOIN_EUI,
				"app_key": fix.VALID_APP_KEY,
				"name": "BulkV1Test",
				"deviceType": profiles[0].get("model_name", ""),
				"tagPath": fix.TEST_TAG_PATH,
				"description": "bulk v1 test",
			}
			status = device.bulkUpload.uploadLine(row, profiles, fix.TEST_TENANT_ID, fix.TEST_TAG_PROVIDER)
			results.append(t.assertIsInstance(status, dict, "uploadLine returns dict"))
			results.append(t.assertIn("message", status, "uploadLine has message"))
		else:
			results.append(t.skip("uploadLine", "no device profiles available"))
	except Exception as e:
		results.append(t.safeTry(lambda: (_ for _ in ()).throw(e), "uploadLine"))

	_cleanup()
	return results