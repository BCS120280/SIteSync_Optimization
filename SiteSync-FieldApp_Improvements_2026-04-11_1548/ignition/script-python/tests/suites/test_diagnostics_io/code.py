import tests.utils.utils as t
import tests.fixtures.fixtures as fix

def run():
	results = []

	# getTagPaths -- pure logic, but test with real-ish data
	dataset = [
		{"fullTagPath": "[SiteSyncUDTs]Site1/Device1"},
		{"fullTagPath": "[SiteSyncUDTs]Site1/Device2"},
	]
	paths = device.diagnostics.getTagPaths(dataset)
	results.append(t.assertEqual(len(paths), 2, "getTagPaths returns 2 paths"))
	results.append(t.assertEqual(paths[0], "[SiteSyncUDTs]Site1/Device1", "getTagPaths first path"))

	# getValues -- reads tag values, may fail if tags don't exist
	try:
		values = device.diagnostics.getValues(paths)
		results.append(t.assertEqual(len(values), 2, "getValues returns same count as input"))
	except Exception as e:
		results.append(t.safeTry(lambda: (_ for _ in ()).throw(e), "getValues"))

	# getStatusCalculations -- with mock QualifiedValue-like objects
	# We test the logic with real tag reads from getValues
	try:
		if values:
			calcs = device.diagnostics.getStatusCalculations(values)
			results.append(t.assertIn("NotActivated", calcs, "getStatusCalculations has NotActivated"))
			results.append(t.assertIn("Operational", calcs, "getStatusCalculations has Operational"))
			results.append(t.assertIn("TimedOut", calcs, "getStatusCalculations has TimedOut"))
			results.append(t.assertIn("DecodeError", calcs, "getStatusCalculations has DecodeError"))
	except Exception as e:
		results.append(t.safeTry(lambda: (_ for _ in ()).throw(e), "getStatusCalculations"))

	# getStatusPaths
	try:
		if values:
			diagPaths = [p + "/metaData/diagnostics/code" for p in paths]
			statusPaths = device.diagnostics.getStatusPaths(diagPaths, values)
			results.append(t.assertIn(-1, statusPaths, "getStatusPaths has -1 key"))
			results.append(t.assertIn(0, statusPaths, "getStatusPaths has 0 key"))
	except Exception as e:
		results.append(t.safeTry(lambda: (_ for _ in ()).throw(e), "getStatusPaths"))

	return results