import tests.utils.utils as t
import tests.fixtures.fixtures as fix

def run():
	results = []
	createdID = None

	# downlinkModel (pure)
	dm = decoders.downlinks.downlinkModel()
	results.append(t.assertIsInstance(dm, dict, "downlinkModel returns dict"))
	results.append(t.assertEqual(dm["id"], 0, "downlinkModel id is 0"))
	results.append(t.assertEqual(dm["name"], "", "downlinkModel name is empty"))
	results.append(t.assertEqual(dm["hexCommand"], "", "downlinkModel hexCommand is empty"))

	# processAnyInputs (pure)
	results.append(t.assertEqual(
		decoders.downlinks.processAnyInputs("AABB{0}CCDD", "FF"),
		"AABBFFCCDD",
		"processAnyInputs substitutes placeholder"
	))
	results.append(t.assertEqual(
		decoders.downlinks.processAnyInputs("AABBCCDD", "FF"),
		"AABBCCDD",
		"processAnyInputs no placeholder"
	))

	# getDownlinkFromList (pure)
	testList = [{"id": 1, "name": "DL1"}, {"id": 2, "name": "DL2"}]
	results.append(t.assertEqual(
		decoders.downlinks.getDownlinkFromList(2, testList)["name"],
		"DL2",
		"getDownlinkFromList finds by ID"
	))
	notFound = decoders.downlinks.getDownlinkFromList(99, testList)
	results.append(t.assertEqual(notFound["id"], 0, "getDownlinkFromList not found returns model"))

	# saveDownlink + listDownlinks + deleteDownlink (I/O cycle)
	try:
		r = decoders.downlinks.saveDownlink(
			0, fix.TEST_MODEL_ID, "AA01", 10, "_TEST_SUITE_downlink", "_TEST_DL"
		)
		results.append(t.assertResultSuccess(r, "saveDownlink success"))
		# Try to extract ID
		if "id" in r:
			createdID = r["id"]
		elif "message" in r:
			try:
				createdID = int(r["message"])
			except:
				pass
	except Exception as e:
		results.append(t.safeTry(lambda: (_ for _ in ()).throw(e), "saveDownlink"))

	# listDownlinks
	try:
		dl = decoders.downlinks.listDownlinks(fix.TEST_MODEL_ID)
		if dl is not None:
			results.append(t.assertIsInstance(dl, list, "listDownlinks returns list"))
		else:
			results.append(t.assertIsNone(dl, "listDownlinks returns None"))
	except Exception as e:
		results.append(t.safeTry(lambda: (_ for _ in ()).throw(e), "listDownlinks"))

	# getDonwlinkByID (note: typo in function name is intentional)
	if createdID:
		try:
			dl = decoders.downlinks.getDonwlinkByID(createdID)
			results.append(t.assertIsInstance(dl, dict, "getDonwlinkByID returns dict"))
		except Exception as e:
			results.append(t.safeTry(lambda: (_ for _ in ()).throw(e), "getDonwlinkByID"))

	# deleteDownlink
	if createdID:
		try:
			r = decoders.downlinks.deleteDownlink(createdID)
			results.append(t.assertIsInstance(r, dict, "deleteDownlink returns dict"))
			createdID = None
		except Exception as e:
			results.append(t.safeTry(lambda: (_ for _ in ()).throw(e), "deleteDownlink"))

	# sendDownlink -- skip to avoid sending real downlinks
	results.append(t.skip("sendDownlink", "Skipped: would send real downlink to device"))

	# Teardown
	if createdID:
		try:
			decoders.downlinks.deleteDownlink(createdID)
		except:
			pass

	return results