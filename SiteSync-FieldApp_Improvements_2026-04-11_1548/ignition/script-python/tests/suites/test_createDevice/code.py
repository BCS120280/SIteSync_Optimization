import tests.utils.utils as t

def run():
	results = []

	# pathValidator -- valid paths
	results.append(t.assertTrue(
		device.createDevice.pathValidator("Devices/MyDevice"),
		"pathValidator valid path"
	))
	results.append(t.assertTrue(
		device.createDevice.pathValidator("A_folder/Sub_folder"),
		"pathValidator underscores"
	))
	results.append(t.assertTrue(
		device.createDevice.pathValidator("Site 1/Building A"),
		"pathValidator with spaces"
	))
	results.append(t.assertTrue(
		device.createDevice.pathValidator("path-with(parens)"),
		"pathValidator with parens and hyphen"
	))

	# pathValidator -- invalid paths
	results.append(t.assertFalse(
		device.createDevice.pathValidator("$invalid"),
		"pathValidator rejects $ at start"
	))
	results.append(t.assertFalse(
		device.createDevice.pathValidator(".hidden"),
		"pathValidator rejects leading dot"
	))

	# pathValidator -- None and empty (both return True)
	results.append(t.assertTrue(
		device.createDevice.pathValidator(None),
		"pathValidator None returns True"
	))
	results.append(t.assertTrue(
		device.createDevice.pathValidator(""),
		"pathValidator empty returns True"
	))

	# charCheck
	results.append(t.assertTrue(
		device.createDevice.charCheck("1234567890abcdef", 16),
		"charCheck 16 chars passes"
	))
	results.append(t.assertFalse(
		device.createDevice.charCheck("short", 16),
		"charCheck too short fails"
	))
	results.append(t.assertFalse(
		device.createDevice.charCheck("12345678901234567", 16),
		"charCheck too long fails"
	))

	# formatAddDeviceRequest
	r = device.createDevice.formatAddDeviceRequest(
		"FFFF-0000-0000-0001", "0000-0000-0000-0000",
		"0011-2233-4455-6677-8899-AABB-CCDD-EEFF",
		"TestDev", "SN001", 1, 5, "test desc", 2
	)
	results.append(t.assertEqual(r["devEUI"], "ffff000000000001", "formatAdd strips dashes, lowercases devEUI"))
	results.append(t.assertEqual(r["applicationKey"], "00112233445566778899aabbccddeeff", "formatAdd strips dashes, lowercases appKey"))
	results.append(t.assertEqual(r["joinEUI"], "0000000000000000", "formatAdd strips dashes, lowercases joinEUI"))
	results.append(t.assertEqual(r["name"], "TestDev", "formatAdd preserves name"))
	results.append(t.assertEqual(r["tenantID"], 1, "formatAdd tenantID"))
	results.append(t.assertEqual(r["deviceModelID"], 5, "formatAdd modelID"))
	results.append(t.assertEqual(r["appID"], 2, "formatAdd appID"))

	# preventNullBasePath
	results.append(t.assertEqual(
		device.createDevice.preventNullBasePath(None), "",
		"preventNullBasePath None -> empty"
	))
	results.append(t.assertEqual(
		device.createDevice.preventNullBasePath("some/path"), "some/path",
		"preventNullBasePath preserves value"
	))

	return results