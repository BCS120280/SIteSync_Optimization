import tests.utils.utils as t
import tests.fixtures.fixtures as fix

def run():
	results = []

	# listDecoders
	try:
		decoderList = decoders.decoder.listDecoders(fix.TEST_TENANT_ID)
		if decoderList is not None:
			results.append(t.assertIsInstance(decoderList, list, "listDecoders returns list"))
		else:
			results.append(t.assertIsNone(decoderList, "listDecoders returns None (no decoders)"))
	except Exception as e:
		results.append(t.safeTry(lambda: (_ for _ in ()).throw(e), "listDecoders"))

	# getDecoder -- with valid model ID
	try:
		dec = decoders.decoder.getDecoder(fix.TEST_MODEL_ID)
		results.append(t.assertIsInstance(dec, dict, "getDecoder returns dict"))
	except Exception as e:
		results.append(t.safeTry(lambda: (_ for _ in ()).throw(e), "getDecoder"))

	# validateDecoder -- valid JS
	try:
		r = decoders.decoder.validateDecoder("function decode(payload) { return {}; }")
		results.append(t.assertIsInstance(r, dict, "validateDecoder returns dict"))
	except Exception as e:
		results.append(t.safeTry(lambda: (_ for _ in ()).throw(e), "validateDecoder"))

	# testDecoder -- simple hex
	try:
		r = decoders.decoder.testDecoder(
			"function decode(payload, port) { return {test: true}; }",
			"0102", 1
		)
		results.append(t.assertIsInstance(r, dict, "testDecoder returns dict"))
	except Exception as e:
		results.append(t.safeTry(lambda: (_ for _ in ()).throw(e), "testDecoder"))

	# loadAPI -- returns dict with defaults or saved
	try:
		api = decoders.decoder.loadAPI(fix.TEST_MODEL_ID)
		results.append(t.assertIsInstance(api, dict, "loadAPI returns dict"))
		results.append(t.assertIn("decoder", api, "loadAPI has decoder key"))
	except Exception as e:
		results.append(t.safeTry(lambda: (_ for _ in ()).throw(e), "loadAPI"))

	# addDecoder + updateDecoder + delete cycle
	createdID = None
	try:
		r = decoders.decoder.addDecoder(fix.TEST_TENANT_ID, "_TEST_SUITE_decoder")
		results.append(t.assertIsInstance(r, dict, "addDecoder returns dict"))
		if "id" in r:
			createdID = r["id"]
	except Exception as e:
		results.append(t.safeTry(lambda: (_ for _ in ()).throw(e), "addDecoder"))

	if createdID:
		try:
			r = decoders.decoder.updateDecoder(
				fix.TEST_TENANT_ID, createdID, "_TEST_SUITE_decoder",
				"function decode(p) { return {}; }", "JS"
			)
			results.append(t.assertIsInstance(r, dict, "updateDecoder returns dict"))
		except Exception as e:
			results.append(t.safeTry(lambda: (_ for _ in ()).throw(e), "updateDecoder"))

	# Teardown: no deleteDecoder function exposed, decoder will remain
	# but is harmless with _TEST_SUITE_ prefix

	return results