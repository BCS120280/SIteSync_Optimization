import tests.utils.utils as t

def run():
	results = []

	# createResults -- success
	r = utils.resultParser.createResults(True, "it worked")
	results.append(t.assertEqual(r["messageType"], "SUCCESS", "createResults success messageType"))
	results.append(t.assertEqual(r["message"], "it worked", "createResults success message"))

	# createResults -- failure
	r = utils.resultParser.createResults(False, "it broke")
	results.append(t.assertEqual(r["messageType"], "FAILURE", "createResults failure messageType"))
	results.append(t.assertEqual(r["message"], "it broke", "createResults failure message"))

	# isResultSuccess -- true via messageType
	results.append(t.assertTrue(
		utils.resultParser.isResultSuccess({"messageType": "SUCCESS", "message": "ok"}),
		"isResultSuccess with messageType SUCCESS"
	))

	# isResultSuccess -- false via messageType
	results.append(t.assertFalse(
		utils.resultParser.isResultSuccess({"messageType": "FAILURE", "message": "no"}),
		"isResultSuccess with messageType FAILURE"
	))

	# isResultSuccess -- true via status key
	results.append(t.assertTrue(
		utils.resultParser.isResultSuccess({"status": "SUCCESS", "message": "ok"}),
		"isResultSuccess with status SUCCESS"
	))

	# isResultSuccess -- false via status key
	results.append(t.assertFalse(
		utils.resultParser.isResultSuccess({"status": "ERROR", "message": "bad"}),
		"isResultSuccess with status ERROR"
	))

	# isResultSuccess -- missing both keys
	results.append(t.assertFalse(
		utils.resultParser.isResultSuccess({"foo": "bar"}),
		"isResultSuccess with neither key"
	))

	# getResultMessage -- normal
	results.append(t.assertEqual(
		utils.resultParser.getResultMessage({"message": "hello"}),
		"hello",
		"getResultMessage normal"
	))

	# getResultMessage -- missing message key
	r = utils.resultParser.getResultMessage({"noMessage": True})
	results.append(t.assertContains(r, "Error getting results", "getResultMessage missing key"))

	return results