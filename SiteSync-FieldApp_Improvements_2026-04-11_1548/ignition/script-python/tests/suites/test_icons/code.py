import tests.utils.utils as t

def run():
	results = []
	fn = dashboard.icons.getIcon

	# All mapped types
	expectations = {
		"TEMPERATURE": "material/free_breakfast",
		"PRESSURE": "material/speed",
		"VIBRATION": "material/vibration",
		"LOCKOUT": "material/lock",
		"VALVEPOSITION": "material/toggle_on",
		"LEVEL": "material/filter_list",
		"THL": "material/sensors",
		"VOLTAGE": "material/power_input",
		"ANALOG": "material/straighten",
		"TANKBOX": "material/water_damage",
		"PULSE": "material/monitor_heart",
		"420MA": "material/straighten",
		"OTHER": "material/devices_other",
	}

	for sensorType, expectedIcon in expectations.items():
		results.append(t.assertEqual(
			fn(sensorType), expectedIcon,
			"getIcon({0})".format(sensorType)
		))

	# Fallback for unknown type
	results.append(t.assertEqual(
		fn("NONEXISTENT"),
		"material/devices_other",
		"getIcon unknown type falls back to devices_other"
	))

	# None key
	results.append(t.assertEqual(
		fn(None),
		"material/devices_other",
		"getIcon(None) falls back"
	))

	return results