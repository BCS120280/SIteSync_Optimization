import tests.utils.utils as t

def run():
	results = []

	# getRegions
	try:
		regions = decoders.LoRaSpecs.getRegions()
		results.append(t.assertIsInstance(regions, list, "getRegions returns list"))
		if len(regions) > 0:
			results.append(t.assertIn("label", regions[0], "region has label"))
			results.append(t.assertIn("value", regions[0], "region has value"))
		else:
			results.append(t.skip("getRegions structure", "no regions returned"))
	except Exception as e:
		results.append(t.safeTry(lambda: (_ for _ in ()).throw(e), "getRegions"))

	# getLoRaVersions
	try:
		versions = decoders.LoRaSpecs.getLoRaVersions()
		results.append(t.assertIsInstance(versions, list, "getLoRaVersions returns list"))
		if len(versions) > 0:
			results.append(t.assertIn("label", versions[0], "version has label"))
		else:
			results.append(t.skip("getLoRaVersions structure", "no versions returned"))
	except Exception as e:
		results.append(t.safeTry(lambda: (_ for _ in ()).throw(e), "getLoRaVersions"))

	# getLoRaRevisions -- requires valid region and version
	try:
		regions = decoders.LoRaSpecs.getRegions()
		versions = decoders.LoRaSpecs.getLoRaVersions()
		if len(regions) > 0 and len(versions) > 0:
			revisions = decoders.LoRaSpecs.getLoRaRevisions(
				regions[0]["value"], versions[0]["value"]
			)
			results.append(t.assertIsInstance(revisions, list, "getLoRaRevisions returns list"))
		else:
			results.append(t.skip("getLoRaRevisions", "no regions or versions to test with"))
	except Exception as e:
		results.append(t.safeTry(lambda: (_ for _ in ()).throw(e), "getLoRaRevisions"))

	# getLoRaClass
	try:
		classes = decoders.LoRaSpecs.getLoRaClass()
		results.append(t.assertIsInstance(classes, list, "getLoRaClass returns list"))
		if len(classes) > 0:
			results.append(t.assertIn("label", classes[0], "class has label"))
		else:
			results.append(t.skip("getLoRaClass structure", "no classes returned"))
	except Exception as e:
		results.append(t.safeTry(lambda: (_ for _ in ()).throw(e), "getLoRaClass"))

	return results