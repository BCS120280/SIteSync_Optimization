import tests.utils.utils as t
import tests.fixtures.fixtures as fix

def _cleanup():
	for eui in [fix.TEST_DEVEUI_01, fix.TEST_DEVEUI_02]:
		try:
			system.sitesync.archiveDevice(eui)
		except:
			pass

def run():
	results = []
	_cleanup()

	# processFile -- I/O (calls system.perspective.print)
	try:
		profiles = fix.SAMPLE_PROFILE_LIST
		rows = [fix.SAMPLE_UPLOAD_ROW, fix.SAMPLE_UPLOAD_ROW_BAD_EUI]
		devices = device.bulkuploadV2.processFile(
			rows, profiles, "TestTenant", "TestApp", fix.TEST_TAG_PATH,
			fix.TEST_TENANT_ID, fix.TEST_MODEL_ID, fix.TEST_APP_ID, fix.TEST_TAG_PROVIDER
		)
		results.append(t.assertEqual(len(devices), 2, "processFile returns 2 devices"))

		# First device should be uploadable
		results.append(t.assertTrue(devices[0]["uploadStatus"], "processFile device 0 uploadable"))
		results.append(t.assertEqual(devices[0]["name"], "TestDevice0001", "processFile preserves name"))

		# Second device should NOT be uploadable (bad EUI)
		results.append(t.assertFalse(devices[1]["uploadStatus"], "processFile device 1 not uploadable"))
	except Exception as e:
		results.append(t.safeTry(lambda: (_ for _ in ()).throw(e), "processFile"))

	# doUpload -- I/O
	try:
		d = {
			"dev_eui": fix.TEST_DEVEUI_01,
			"join_eui": fix.VALID_JOIN_EUI,
			"app_key": fix.VALID_APP_KEY,
			"name": "BulkV2Test",
			"serial_number": None,
			"deviceTypeID": fix.TEST_MODEL_ID,
			"description": "v2 test",
			"tagProvider": fix.TEST_TAG_PROVIDER,
			"tagPath": fix.TEST_TAG_PATH,
			"appID": fix.TEST_APP_ID,
			"tenantID": fix.TEST_TENANT_ID,
		}
		r = device.bulkuploadV2.doUpload(d)
		results.append(t.assertIsInstance(r, dict, "doUpload returns dict"))
		results.append(t.assertIn("messageType", r, "doUpload has messageType"))
	except Exception as e:
		results.append(t.safeTry(lambda: (_ for _ in ()).throw(e), "doUpload"))

	# createFileForDownload -- I/O (uses system.dataset)
	try:
		csv = device.bulkuploadV2.createFileForDownload()
		results.append(t.assertIsNotNone(csv, "createFileForDownload returns data"))
		results.append(t.assertContains(csv, "dev_eui", "CSV contains dev_eui header"))
		results.append(t.assertContains(csv, "app_key", "CSV contains app_key header"))
	except Exception as e:
		results.append(t.safeTry(lambda: (_ for _ in ()).throw(e), "createFileForDownload"))

	_cleanup()
	return results