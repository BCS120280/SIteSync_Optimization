import tests.utils.utils as t
import tests.fixtures.fixtures as fix

def run():
	results = []
	createdID = None

	# listUDTs
	try:
		udts = decoders.udt.listUDTs(fix.TEST_TENANT_ID)
		results.append(t.assertIsInstance(udts, list, "listUDTs returns list"))
	except Exception as e:
		results.append(t.safeTry(lambda: (_ for _ in ()).throw(e), "listUDTs"))

	# createUDT
	try:
		r = decoders.udt.createUDT("_TEST_SUITE_udt", fix.TEST_TENANT_ID)
		results.append(t.assertIsInstance(r, dict, "createUDT returns dict"))
		if "id" in r:
			createdID = r["id"]
	except Exception as e:
		results.append(t.safeTry(lambda: (_ for _ in ()).throw(e), "createUDT"))

	# getUDT
	if createdID:
		try:
			udt = decoders.udt.getUDT(createdID)
			results.append(t.assertIsInstance(udt, dict, "getUDT returns dict"))
		except Exception as e:
			results.append(t.safeTry(lambda: (_ for _ in ()).throw(e), "getUDT"))

	# saveUDT (update)
	if createdID:
		try:
			r = decoders.udt.saveUDT(createdID, "_TEST_SUITE_udt", '{"tags":[]}')
			results.append(t.assertIsInstance(r, dict, "saveUDT returns dict"))
		except Exception as e:
			results.append(t.safeTry(lambda: (_ for _ in ()).throw(e), "saveUDT"))

	# generateUDT
	try:
		r = decoders.udt.generateUDT('{"temperature": 22.5}', "_TEST_SUITE_gen")
		results.append(t.assertIsInstance(r, dict, "generateUDT returns dict"))
	except Exception as e:
		results.append(t.safeTry(lambda: (_ for _ in ()).throw(e), "generateUDT"))

	# No delete function for UDTs is exposed, created UDT remains with _TEST_SUITE_ prefix

	return results