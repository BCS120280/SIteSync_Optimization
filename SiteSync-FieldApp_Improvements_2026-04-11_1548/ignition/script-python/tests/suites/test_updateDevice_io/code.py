import json
import tests.utils.utils as t
import tests.fixtures.fixtures as fix

def _setup():
	"""Create a test device for update tests."""
	try:
		system.sitesync.archiveDevice(fix.TEST_DEVEUI_02)
	except:
		pass
	req = device.createDevice.formatAddDeviceRequest(
		fix.TEST_DEVEUI_02, fix.VALID_JOIN_EUI, fix.VALID_APP_KEY,
		"TestUpdateIO", "SN-TEST-002", fix.TEST_TENANT_ID,
		fix.TEST_MODEL_ID, "update test", fix.TEST_APP_ID
	)
	device.createDevice.createDevice(req)

def _teardown():
	try:
		system.sitesync.archiveDevice(fix.TEST_DEVEUI_02)
	except:
		pass

def run():
	results = []
	_setup()

	# updateDevice
	try:
		updateReq = json.loads(device.updateDevice.formatUpdateDeviceRequest(
			fix.TEST_DEVEUI_02, "UpdatedName", "Updated description"
		))
		r = device.updateDevice.updateDevice(updateReq)
		if isinstance(r, dict):
			results.append(t.assertResultSuccess(r, "updateDevice success"))
		else:
			results.append(t.assertTrue(False, "updateDevice returned non-dict: {0}".format(r)))
	except Exception as e:
		results.append(t.safeTry(lambda: (_ for _ in ()).throw(e), "updateDevice"))

	# updateLocation
	try:
		r = device.updateDevice.updateLocation(fix.TEST_DEVEUI_02, 29.76, -95.37)
		results.append(t.assertResultSuccess(r, "updateLocation success"))
	except Exception as e:
		results.append(t.safeTry(lambda: (_ for _ in ()).throw(e), "updateLocation"))

	# updateDeviceMetaData
	try:
		r = device.updateDevice.updateDeviceMetaData(fix.SAMPLE_META, fix.TEST_DEVEUI_02)
		if isinstance(r, dict):
			mt = r.get("messageType", r.get("status", "")).upper()
			results.append(t.assertNotEqual(mt, "ERROR", "updateDeviceMetaData not error"))
		else:
			results.append(t.skip("updateDeviceMetaData", "unexpected return type"))
	except Exception as e:
		results.append(t.safeTry(lambda: (_ for _ in ()).throw(e), "updateDeviceMetaData"))

	_teardown()
	return results