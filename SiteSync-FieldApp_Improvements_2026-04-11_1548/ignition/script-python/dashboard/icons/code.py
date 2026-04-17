def getIcon(sensorType):
	iconMap = {
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
		"OTHER": "material/devices_other"
	}
	return iconMap.get(sensorType, "material/devices_other")