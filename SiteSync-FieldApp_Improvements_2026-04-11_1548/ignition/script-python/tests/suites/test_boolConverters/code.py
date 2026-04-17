import tests.utils.utils as t

def run():
	results = []

	# getInt
	results.append(t.assertEqual(utils.boolConverters.getInt(False), 0, "getInt(False) == 0"))
	results.append(t.assertEqual(utils.boolConverters.getInt(True), 1, "getInt(True) == 1"))
	results.append(t.assertEqual(utils.boolConverters.getInt(None), 1, "getInt(None) == 1 (truthy path)"))
	results.append(t.assertEqual(utils.boolConverters.getInt(0), 0, "getInt(0) == 0 (falsy int)"))

	# getBool
	results.append(t.assertEqual(utils.boolConverters.getBool(0), False, "getBool(0) == False"))
	results.append(t.assertEqual(utils.boolConverters.getBool(1), True, "getBool(1) == True"))
	results.append(t.assertEqual(utils.boolConverters.getBool(42), True, "getBool(42) == True (nonzero)"))
	results.append(t.assertEqual(utils.boolConverters.getBool(-1), True, "getBool(-1) == True (nonzero)"))

	return results