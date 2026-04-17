def getHistoryConfig(sensorType, fullTagPath):
	configs = {
		"THL": {
			"pens": [
				{"name": "Temperature", "path": fullTagPath + "/temperature", "color": "#ED6A5A"},
				{"name": "Humidity", "path": fullTagPath + "/humidity", "color": "#18C7B8"}
			],
			"chartTitle": "Temperature & Humidity",
			"exportPrefix": "thl"
		},
		"VIBRATION": {
			"pens": [
				{"name": "X", "path": fullTagPath + "/measurement/x/rms_acceleration", "color": "#ED6A5A"},
				{"name": "Y", "path": fullTagPath + "/measurement/y/rms_acceleration", "color": "#18C7B8"},
				{"name": "Z", "path": fullTagPath + "/measurement/z/rms_acceleration", "color": "#FFE733"}
			],
			"chartTitle": "RMS Acceleration (X/Y/Z)",
			"exportPrefix": "vibration"
		}
	}

	if sensorType and sensorType.upper() in configs:
		return configs[sensorType.upper()]

	return {
		"pens": [
			{"name": "Value", "path": fullTagPath + "/metaData/valueToDisplay", "color": "#18C7B8"}
		],
		"chartTitle": "Value History",
		"exportPrefix": "history"
	}