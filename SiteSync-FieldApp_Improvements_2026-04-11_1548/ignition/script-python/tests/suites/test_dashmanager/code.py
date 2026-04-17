import tests.utils.utils as t

def run():
	results = []

	results.append(t.assertEqual(
		utils.dashmanager.getPath("SiteSync/dragino-lht65"),
		"Devices/Details/values/dashes/tempandhumidity",
		"getPath dragino-lht65 returns specific path"
	))

	results.append(t.assertEqual(
		utils.dashmanager.getPath("SiteSync/other-device"),
		"Devices/Details/values/dashes/generic",
		"getPath other device returns generic"
	))

	results.append(t.assertEqual(
		utils.dashmanager.getPath(""),
		"Devices/Details/values/dashes/generic",
		"getPath empty string returns generic"
	))

	return results