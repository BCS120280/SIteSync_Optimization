import tests.utils.utils as t
import tests.fixtures.fixtures as fix

def run():
	results = []

	# linkToAsset -- invalid EUI
	try:
		r = device.assetAssociation.linkToAsset("short", 1)
		results.append(t.assertResultFailure(r, "linkToAsset invalid EUI"))
	except Exception as e:
		results.append(t.safeTry(lambda: (_ for _ in ()).throw(e), "linkToAsset invalid EUI"))

	# linkToAsset -- invalid assetID
	try:
		r = device.assetAssociation.linkToAsset(fix.TEST_DEVEUI_01, -1)
		results.append(t.assertResultFailure(r, "linkToAsset invalid assetID"))
	except Exception as e:
		results.append(t.safeTry(lambda: (_ for _ in ()).throw(e), "linkToAsset invalid assetID"))

	# unlinkFromAsset -- invalid EUI
	try:
		r = device.assetAssociation.unlinkFromAsset("short")
		results.append(t.assertResultFailure(r, "unlinkFromAsset invalid EUI"))
	except Exception as e:
		results.append(t.safeTry(lambda: (_ for _ in ()).throw(e), "unlinkFromAsset invalid EUI"))

	# getDeviceAsset -- nonexistent
	try:
		r = device.assetAssociation.getDeviceAsset("0000000000000000")
		# Returns None or dict depending on API behavior
		results.append(t.assertTrue(
			r is None or isinstance(r, dict),
			"getDeviceAsset returns None or dict"
		))
	except Exception as e:
		results.append(t.safeTry(lambda: (_ for _ in ()).throw(e), "getDeviceAsset nonexistent"))

	# getDeviceAsset -- empty EUI
	try:
		r = device.assetAssociation.getDeviceAsset("")
		results.append(t.assertIsNone(r, "getDeviceAsset empty returns None"))
	except Exception as e:
		results.append(t.safeTry(lambda: (_ for _ in ()).throw(e), "getDeviceAsset empty"))

	# listAssetDevices -- invalid ID
	try:
		r = device.assetAssociation.listAssetDevices(-1)
		results.append(t.assertEqual(r, [], "listAssetDevices invalid returns empty"))
	except Exception as e:
		results.append(t.safeTry(lambda: (_ for _ in ()).throw(e), "listAssetDevices invalid"))

	# listAssetDevices -- None
	try:
		r = device.assetAssociation.listAssetDevices(None)
		results.append(t.assertEqual(r, [], "listAssetDevices None returns empty"))
	except Exception as e:
		results.append(t.safeTry(lambda: (_ for _ in ()).throw(e), "listAssetDevices None"))

	return results