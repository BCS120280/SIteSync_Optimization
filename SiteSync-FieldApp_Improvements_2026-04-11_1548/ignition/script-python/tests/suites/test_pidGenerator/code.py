import tests.utils.utils as t

def run():
	results = []
	fn = device.pidGenerator.getTypeAbbreviation

	# All mapped types
	expectations = {
		"LEVEL": "LI",
		"POSITION": "ZI",
		"VALVEPOSITION": "ZI",
		"TEMPERATURE": "TI",
		"PRESSURE": "PI",
		"VIBRATION": "VI",
		"STEAMTRAP": "X",
		"VOLTAGE": "EI",
		"CURRENT": "II",
		"HOTDROP": "II",
		"FLOW": "FI",
		"FLOWMETER": "FI",
	}
	for deviceType, expected in expectations.items():
		results.append(t.assertEqual(
			fn(deviceType), expected,
			"getTypeAbbreviation({0})".format(deviceType)
		))

	# Unknown type
	results.append(t.assertEqual(fn("UNKNOWN"), "X", "getTypeAbbreviation unknown -> X"))

	# None
	results.append(t.assertEqual(fn(None), "X", "getTypeAbbreviation(None) -> X"))

	# Case insensitivity (function uppercases)
	results.append(t.assertEqual(fn("temperature"), "TI", "getTypeAbbreviation lowercase"))
	results.append(t.assertEqual(fn("  Pressure  "), "PI", "getTypeAbbreviation with whitespace"))

	return results