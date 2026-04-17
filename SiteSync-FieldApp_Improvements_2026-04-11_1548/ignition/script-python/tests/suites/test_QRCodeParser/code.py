import tests.utils.utils as t
import tests.fixtures.fixtures as fix

def run():
	results = []

	# getQRType
	results.append(t.assertEqual(
		utils.QRCodeParser.getQRType(fix.QR_LORA),
		"LORAALIANCE",
		"getQRType LoRa Alliance format"
	))
	results.append(t.assertEqual(
		utils.QRCodeParser.getQRType(fix.QR_SITESYNC),
		"SITESYNC",
		"getQRType SiteSync format"
	))
	results.append(t.assertEqual(
		utils.QRCodeParser.getQRType(fix.QR_VEGA),
		"VEGA",
		"getQRType Vega format (>4 colons with L0:D0)"
	))
	results.append(t.assertEqual(
		utils.QRCodeParser.getQRType(fix.QR_EUI_ONLY),
		"DEVEUI",
		"getQRType bare EUI"
	))
	results.append(t.assertEqual(
		utils.QRCodeParser.getQRType("nocolons"),
		"DEVEUI",
		"getQRType no colons"
	))

	# determineQRContentType (slightly different logic)
	results.append(t.assertEqual(
		utils.QRCodeParser.determineQRContentType(fix.QR_LORA),
		"LORAALIANCE",
		"determineQRContentType LoRa"
	))
	results.append(t.assertEqual(
		utils.QRCodeParser.determineQRContentType("AB:CD"),
		"SITESYNC",
		"determineQRContentType with colon but no L0:D0"
	))

	# validateDevEUI
	results.append(t.assertTrue(
		utils.QRCodeParser.validateDevEUI("FFFF000000000001"),
		"validateDevEUI valid 16 chars"
	))
	results.append(t.assertFalse(
		utils.QRCodeParser.validateDevEUI("short"),
		"validateDevEUI too short"
	))
	results.append(t.assertFalse(
		utils.QRCodeParser.validateDevEUI("12345678901234567"),
		"validateDevEUI too long (17 chars)"
	))

	# setName
	results.append(t.assertEqual(
		utils.QRCodeParser.setName("FFFF000000000001", "Pressure"),
		"Pressure-0001",
		"setName with valid 16-char EUI"
	))
	results.append(t.assertEqual(
		utils.QRCodeParser.setName("short", "Pressure"),
		"short",
		"setName with short EUI returns raw"
	))

	# parseSiteSync
	r = utils.QRCodeParser.parseSiteSync(fix.QR_SITESYNC)
	results.append(t.assertEqual(r["devEUI"], "ffff000000000001", "parseSiteSync devEUI lowercased"))
	results.append(t.assertEqual(r["appKey"], fix.VALID_APP_KEY, "parseSiteSync appKey"))
	results.append(t.assertEqual(r["deviceType"], "SushiPressure", "parseSiteSync deviceType A107"))
	results.append(t.assertEqual(r["joinEUI"], "0000000000000000", "parseSiteSync default joinEUI"))
	results.append(t.assertEqual(r["scanType"], "SiteSync", "parseSiteSync scanType"))

	# parseSiteSync with explicit appEUI
	r2 = utils.QRCodeParser.parseSiteSync(fix.QR_SITESYNC_WITH_APPEUI)
	results.append(t.assertEqual(r2["joinEUI"], "1234567890abcdef", "parseSiteSync explicit joinEUI"))

	# parseLoRa
	r = utils.QRCodeParser.parseLoRa(fix.QR_LORA)
	results.append(t.assertEqual(r["devEUI"], "ffff000000000001", "parseLoRa devEUI"))
	results.append(t.assertEqual(r["joinEUI"], "1234567890abcdef", "parseLoRa joinEUI"))
	results.append(t.assertEqual(r["scanType"], "LoRa Alliance Standard", "parseLoRa scanType"))

	# parseVega -- KNOWN_DEFECT: indented inside getQRType, unreachable
	results.append(t.knownDefect(
		"parseVega unreachable",
		"parseVega is indented inside getQRType function body -- NameError at module level"
	))

	# getDeviceType map lookups
	results.append(t.assertEqual(utils.QRCodeParser.getDeviceType("A107"), "SushiPressure", "getDeviceType A107"))
	results.append(t.assertEqual(utils.QRCodeParser.getDeviceType("A100"), "Abeeway", "getDeviceType A100"))
	results.append(t.assertEqual(utils.QRCodeParser.getDeviceType("A109"), "SushiVibration", "getDeviceType A109"))
	results.append(t.assertEqual(
		utils.QRCodeParser.getDeviceType("UNKNOWN_CODE"),
		"UNKNOWN_CODE",
		"getDeviceType unknown returns input"
	))

	# parse -- integration: SiteSync format
	r = utils.QRCodeParser.parse(fix.QR_SITESYNC)
	results.append(t.assertEqual(r["scanType"], "SiteSync", "parse dispatches SiteSync"))

	# parse -- integration: LoRa format
	r = utils.QRCodeParser.parse(fix.QR_LORA)
	results.append(t.assertEqual(r["scanType"], "LoRa Alliance Standard", "parse dispatches LoRa"))

	# parse -- bare EUI (valid)
	r = utils.QRCodeParser.parse(fix.QR_EUI_ONLY)
	results.append(t.assertEqual(r["devEUI"], "ffff000000000001", "parse bare EUI returns lowercased devEUI"))
	results.append(t.assertEqual(r["scanType"], "EUI Only", "parse bare EUI scanType"))

	# parse -- unrecognized short data
	r = utils.QRCodeParser.parse(fix.QR_SHORT)
	results.append(t.assertEqual(r["scanType"], "Unknown format", "parse short unknown format"))
	results.append(t.assertEqual(r["devEUI"], "", "parse unknown has empty devEUI"))

	return results