import tests.utils.utils as t
import tests.fixtures.fixtures as fix

def run():
	results = []
	models = fix.SAMPLE_MODEL_LIST

	# findModelIDByName -- found
	results.append(t.assertEqual(
		decoders.model.findModelIDByName(models, "TEPressure"),
		1,
		"findModelIDByName finds TEPressure -> 1"
	))
	results.append(t.assertEqual(
		decoders.model.findModelIDByName(models, "SushiVibration"),
		2,
		"findModelIDByName finds SushiVibration -> 2"
	))

	# findModelIDByName -- not found
	results.append(t.assertEqual(
		decoders.model.findModelIDByName(models, "DoesNotExist"),
		-1,
		"findModelIDByName returns -1 for missing"
	))

	# findModelIDByName -- empty list
	results.append(t.assertEqual(
		decoders.model.findModelIDByName([], "TEPressure"),
		-1,
		"findModelIDByName returns -1 for empty list"
	))

	# findModelNameByID -- found
	results.append(t.assertEqual(
		decoders.model.findModelNameByID(models, 1),
		"TEPressure",
		"findModelNameByID finds id 1 -> TEPressure"
	))
	results.append(t.assertEqual(
		decoders.model.findModelNameByID(models, 3),
		"RadioBridge4-20ma",
		"findModelNameByID finds id 3"
	))

	# findModelNameByID -- not found
	results.append(t.assertEqual(
		decoders.model.findModelNameByID(models, 999),
		-1,
		"findModelNameByID returns -1 for missing"
	))

	# findModelNameByID -- empty list
	results.append(t.assertEqual(
		decoders.model.findModelNameByID([], 1),
		-1,
		"findModelNameByID returns -1 for empty list"
	))

	return results