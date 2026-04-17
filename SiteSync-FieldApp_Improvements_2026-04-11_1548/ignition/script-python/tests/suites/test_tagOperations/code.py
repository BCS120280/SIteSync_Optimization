import tests.utils.utils as t

def run():
	results = []

	# assembleFullPath -- with basePath
	results.append(t.assertEqual(
		device.tagOperations.assembleFullPath("SiteSyncUDTs", "Sites/Building1", "Sensor01"),
		"[SiteSyncUDTs]Sites/Building1/Sensor01",
		"assembleFullPath with basePath"
	))

	# assembleFullPath -- empty basePath
	results.append(t.assertEqual(
		device.tagOperations.assembleFullPath("SiteSyncUDTs", "", "Sensor01"),
		"[SiteSyncUDTs]Sensor01",
		"assembleFullPath empty basePath"
	))

	# assembleFullPath -- None basePath
	results.append(t.assertEqual(
		device.tagOperations.assembleFullPath("SiteSyncUDTs", None, "Sensor01"),
		"[SiteSyncUDTs]Sensor01",
		"assembleFullPath None basePath"
	))

	# assembleBasePath -- with basePath
	results.append(t.assertEqual(
		device.tagOperations.assembleBasePath("Sites/Building1", "Sensor01"),
		"Sites/Building1/Sensor01",
		"assembleBasePath with basePath"
	))

	# assembleBasePath -- empty basePath
	results.append(t.assertEqual(
		device.tagOperations.assembleBasePath("", "Sensor01"),
		"Sensor01",
		"assembleBasePath empty"
	))

	# assembleBasePath -- None basePath
	results.append(t.assertEqual(
		device.tagOperations.assembleBasePath(None, "Sensor01"),
		"Sensor01",
		"assembleBasePath None"
	))

	# preventNullBasePath
	results.append(t.assertEqual(
		device.tagOperations.preventNullBasePath(None), "",
		"preventNullBasePath None -> empty"
	))
	results.append(t.assertEqual(
		device.tagOperations.preventNullBasePath("path"), "path",
		"preventNullBasePath preserves value"
	))

	# regenerateTag always returns False
	results.append(t.assertFalse(
		device.tagOperations.regenerateTag("any", "any"),
		"regenerateTag always returns False (stub)"
	))

	return results