import tests.utils.utils as t

def run():
	results = []
	tagPath = "[SiteSyncUDTs]TestDevice"

	# THL config
	r = utils.historyconfig.getHistoryConfig("THL", tagPath)
	results.append(t.assertEqual(len(r["pens"]), 2, "THL returns 2 pens"))
	results.append(t.assertEqual(r["chartTitle"], "Temperature & Humidity", "THL chart title"))
	results.append(t.assertContains(r["pens"][0]["path"], "/temperature", "THL pen 0 is temperature"))

	# VIBRATION config
	r = utils.historyconfig.getHistoryConfig("VIBRATION", tagPath)
	results.append(t.assertEqual(len(r["pens"]), 3, "VIBRATION returns 3 pens (x/y/z)"))
	results.append(t.assertEqual(r["chartTitle"], "RMS Acceleration (X/Y/Z)", "VIBRATION chart title"))

	# Case insensitivity
	r = utils.historyconfig.getHistoryConfig("thl", tagPath)
	results.append(t.assertEqual(r["chartTitle"], "Temperature & Humidity", "THL case insensitive"))

	# Fallback / unknown sensor type
	r = utils.historyconfig.getHistoryConfig("UNKNOWN_TYPE", tagPath)
	results.append(t.assertEqual(len(r["pens"]), 1, "Fallback returns 1 pen"))
	results.append(t.assertEqual(r["chartTitle"], "Value History", "Fallback chart title"))
	results.append(t.assertContains(r["pens"][0]["path"], "/metaData/valueToDisplay", "Fallback pen path"))

	# None sensor type
	r = utils.historyconfig.getHistoryConfig(None, tagPath)
	results.append(t.assertEqual(r["chartTitle"], "Value History", "None sensorType gets fallback"))

	return results