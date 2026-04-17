import tests.utils.utils as t
import tests.fixtures.fixtures as fix

def run():
	results = []

	# getEncoder -- None
	try:
		r = decoders.encoder.getEncoder(None)
		results.append(t.assertIsNone(r, "getEncoder(None) returns None"))
	except Exception as e:
		results.append(t.safeTry(lambda: (_ for _ in ()).throw(e), "getEncoder None"))

	# getEncoder -- 0
	try:
		r = decoders.encoder.getEncoder(0)
		results.append(t.assertIsNone(r, "getEncoder(0) returns None"))
	except Exception as e:
		results.append(t.safeTry(lambda: (_ for _ in ()).throw(e), "getEncoder 0"))

	# getEncoder -- nonexistent ID
	try:
		r = decoders.encoder.getEncoder(99999)
		# May return None or a dict depending on API
		results.append(t.assertTrue(
			r is None or isinstance(r, dict),
			"getEncoder nonexistent returns None or dict"
		))
	except Exception as e:
		results.append(t.safeTry(lambda: (_ for _ in ()).throw(e), "getEncoder nonexistent"))

	# getEncoderQuestions -- with None encoder
	try:
		r = decoders.encoder.getEncoderQuestions(None)
		results.append(t.assertEqual(r, [], "getEncoderQuestions(None) returns []"))
	except Exception as e:
		results.append(t.safeTry(lambda: (_ for _ in ()).throw(e), "getEncoderQuestions None"))

	# getEncoderQuestions -- with 0
	try:
		r = decoders.encoder.getEncoderQuestions(0)
		results.append(t.assertEqual(r, [], "getEncoderQuestions(0) returns []"))
	except Exception as e:
		results.append(t.safeTry(lambda: (_ for _ in ()).throw(e), "getEncoderQuestions 0"))

	# encodeAndSave -- skip as it requires a real encoder to be configured
	results.append(t.skip(
		"encodeAndSave",
		"Requires configured encoder with valid questions"
	))

	return results