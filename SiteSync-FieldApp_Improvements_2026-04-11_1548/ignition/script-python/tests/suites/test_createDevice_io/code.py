import json
import tests.utils.utils as t
import tests.fixtures.fixtures as fix

def _cleanup():
	"""Remove test devices from previous failed runs."""
	for eui in [fix.TEST_DEVEUI_01]:
		try:
			system.sitesync.archiveDevice(eui)
		except:
			pass

def run():
	results = []
	_cleanup()
	deviceCreated = False

	# createDevice (low-level)
	try:
		req = device.createDevice.formatAddDeviceRequest(
			fix.TEST_DEVEUI_01, fix.VALID_JOIN_EUI, fix.VALID_APP_KEY,
			"TestCreateIO", "SN-TEST-001", fix.TEST_TENANT_ID,
			fix.TEST_MODEL_ID, "test create", fix.TEST_APP_ID
		)
		r = device.createDevice.createDevice(req)
		results.append(t.assertResultSuccess(r, "createDevice success"))
		if utils.resultParser.isResultSuccess(r):
			deviceCreated = True
	except Exception as e:
		results.append(t.safeTry(lambda: (_ for _ in ()).throw(e), "createDevice"))

	# saveTagPathForDevice
	if deviceCreated:
		try:
			r = device.createDevice.saveTagPathForDevice(
				fix.TEST_DEVEUI_01, fix.TEST_TAG_PROVIDER,
				fix.TEST_TAG_PATH, "TestCreateIO", fix.TEST_TENANT_ID
			)
			results.append(t.assertResultSuccess(r, "saveTagPathForDevice success"))
		except Exception as e:
			results.append(t.safeTry(lambda: (_ for _ in ()).throw(e), "saveTagPathForDevice"))

	# Verify device exists
	if deviceCreated:
		try:
			d = device.get.getDevice(fix.TEST_DEVEUI_01)
			results.append(t.assertEqual(
				d.get("devEUI", "").lower(), fix.TEST_DEVEUI_01,
				"created device retrievable"
			))
		except Exception as e:
			results.append(t.safeTry(lambda: (_ for _ in ()).throw(e), "verify created device"))

	# Teardown
	if deviceCreated:
		try:
			system.sitesync.archiveDevice(fix.TEST_DEVEUI_01)
		except:
			pass
	_cleanup()

	return results