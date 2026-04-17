import tests.utils.utils as t
import tests.fixtures.fixtures as fix

def _setup():
	try:
		system.sitesync.archiveDevice(fix.TEST_DEVEUI_04)
	except:
		pass
	req = device.createDevice.formatAddDeviceRequest(
		fix.TEST_DEVEUI_04, fix.VALID_JOIN_EUI, fix.VALID_APP_KEY,
		"TestImagesIO", "SN-TEST-004", fix.TEST_TENANT_ID,
		fix.TEST_MODEL_ID, "image test", fix.TEST_APP_ID
	)
	device.createDevice.createDevice(req)

def _teardown():
	try:
		system.sitesync.archiveDevice(fix.TEST_DEVEUI_04)
	except:
		pass

def run():
	results = []
	_setup()

	# saveImage
	try:
		r = device.images.saveImage(fix.SAMPLE_IMAGE_B64, fix.TEST_DEVEUI_04)
		results.append(t.assertResultSuccess(r, "saveImage success"))
	except Exception as e:
		results.append(t.safeTry(lambda: (_ for _ in ()).throw(e), "saveImage"))

	# getImageByDevEUI
	try:
		img = device.images.getImageByDevEUI(fix.TEST_DEVEUI_04)
		results.append(t.assertIsNotNone(img, "getImageByDevEUI returns data"))
	except Exception as e:
		results.append(t.safeTry(lambda: (_ for _ in ()).throw(e), "getImageByDevEUI"))

	# getImageByDevEUI -- nonexistent
	try:
		img = device.images.getImageByDevEUI("0000000000000000")
		results.append(t.assertIsNone(img, "getImageByDevEUI nonexistent returns None"))
	except Exception as e:
		results.append(t.safeTry(lambda: (_ for _ in ()).throw(e), "getImageByDevEUI nonexistent"))

	_teardown()
	return results