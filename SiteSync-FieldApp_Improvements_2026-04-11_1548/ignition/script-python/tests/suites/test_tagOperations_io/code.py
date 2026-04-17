import json
import tests.utils.utils as t
import tests.fixtures.fixtures as fix

def _setup():
	"""Create a test device + tag for tag operation tests."""
	try:
		system.sitesync.archiveDevice(fix.TEST_DEVEUI_03)
	except:
		pass
	req = device.createDevice.formatAddDeviceRequest(
		fix.TEST_DEVEUI_03, fix.VALID_JOIN_EUI, fix.VALID_APP_KEY,
		"TestTagOpsIO", "SN-TEST-003", fix.TEST_TENANT_ID,
		fix.TEST_MODEL_ID, "tag ops test", fix.TEST_APP_ID
	)
	device.createDevice.createDevice(req)
	device.tagOperations.saveTagPathForDevice(
		fix.TEST_DEVEUI_03, fix.TEST_TAG_PROVIDER,
		fix.TEST_TAG_PATH, "TestTagOpsIO", fix.TEST_TENANT_ID
	)

def _teardown():
	try:
		system.sitesync.archiveDevice(fix.TEST_DEVEUI_03)
	except:
		pass

def run():
	results = []
	_setup()

	fullPath = device.tagOperations.assembleFullPath(
		fix.TEST_TAG_PROVIDER, fix.TEST_TAG_PATH, "TestTagOpsIO"
	)

	# saveTagPathForDevice (already done in setup, verify via lookup)
	try:
		d = device.get.deviceLookup(fix.TEST_DEVEUI_03)
		results.append(t.assertIsNotNone(d.get("fullTagPath"), "device has fullTagPath after tag creation"))
	except Exception as e:
		results.append(t.safeTry(lambda: (_ for _ in ()).throw(e), "verify tag path"))

	# updateDescriptionTag
	try:
		r = device.tagOperations.updateDescriptionTag(fullPath, "Test description")
		results.append(t.assertIsNotNone(r, "updateDescriptionTag returns result"))
	except Exception as e:
		results.append(t.safeTry(lambda: (_ for _ in ()).throw(e), "updateDescriptionTag"))

	# installedBy
	try:
		r = device.tagOperations.installedBy(fullPath, "test_user")
		results.append(t.assertIsNotNone(r, "installedBy returns result"))
	except Exception as e:
		results.append(t.safeTry(lambda: (_ for _ in ()).throw(e), "installedBy"))

	# updateInstallLocationTag
	try:
		r = device.tagOperations.updateInstallLocationTag(fullPath, 29.76, -95.37)
		results.append(t.assertIsNotNone(r, "updateInstallLocationTag returns result"))
	except Exception as e:
		results.append(t.safeTry(lambda: (_ for _ in ()).throw(e), "updateInstallLocationTag"))

	# updateMetaData
	try:
		r = device.tagOperations.updateMetaData(fullPath, json.dumps(fix.SAMPLE_META))
		results.append(t.assertIsNotNone(r, "updateMetaData returns result"))
	except Exception as e:
		results.append(t.safeTry(lambda: (_ for _ in ()).throw(e), "updateMetaData"))

	# updateImageTag
	try:
		r = device.tagOperations.updateImageTag(fullPath, fix.SAMPLE_IMAGE_B64)
		results.append(t.assertIsNotNone(r, "updateImageTag returns result"))
	except Exception as e:
		results.append(t.safeTry(lambda: (_ for _ in ()).throw(e), "updateImageTag"))

	# updateTagValues
	try:
		r = device.tagOperations.updateTagValues(
			[fullPath + "/metaData/locationDescription"],
			["updated via test"]
		)
		results.append(t.assertIsNotNone(r, "updateTagValues returns result"))
	except Exception as e:
		results.append(t.safeTry(lambda: (_ for _ in ()).throw(e), "updateTagValues"))

	# editExistingTag
	try:
		r = device.tagOperations.editExistingTag(
			fix.TEST_DEVEUI_03, fix.TEST_TAG_PROVIDER,
			fix.TEST_TAG_PATH, "TestTagOpsIO"
		)
		results.append(t.assertIsInstance(r, dict, "editExistingTag returns dict"))
	except Exception as e:
		results.append(t.safeTry(lambda: (_ for _ in ()).throw(e), "editExistingTag"))

	# renameTag -- skip to avoid destroying test state
	results.append(t.skip("renameTag", "skipped to preserve test device state"))

	# moveTag -- skip to avoid destroying test state
	results.append(t.skip("moveTag", "skipped to preserve test device state"))

	# regenerateTag -- stub
	results.append(t.assertFalse(
		device.tagOperations.regenerateTag(fullPath, fix.TEST_DEVEUI_03),
		"regenerateTag stub returns False"
	))

	_teardown()
	return results