import tests.utils.utils as t
import tests.fixtures.fixtures as fix

def _cleanup():
	"""Remove leftover test tag paths."""
	try:
		allPaths = utils.normalizedTagPaths.getAllTagPaths()
		for p in allPaths:
			if p.get("tagPathBase", "").startswith("_TEST_SUITE_"):
				try:
					utils.normalizedTagPaths.deleteTagPath(p["id"])
				except:
					pass
	except:
		pass

def run():
	results = []
	_cleanup()
	createdID = None

	# getAllTagPaths
	try:
		paths = utils.normalizedTagPaths.getAllTagPaths()
		results.append(t.assertIsInstance(paths, list, "getAllTagPaths returns list"))
	except Exception as e:
		results.append(t.safeTry(lambda: (_ for _ in ()).throw(e), "getAllTagPaths"))

	# getTagPathsForTenant
	try:
		paths = utils.normalizedTagPaths.getTagPathsForTenant(fix.TEST_TENANT_ID)
		results.append(t.assertIsInstance(paths, list, "getTagPathsForTenant returns list"))
	except Exception as e:
		results.append(t.safeTry(lambda: (_ for _ in ()).throw(e), "getTagPathsForTenant"))

	# createNewTag
	try:
		r = utils.normalizedTagPaths.createNewTag(fix.TEST_TENANT_ID)
		results.append(t.assertResultSuccess(r, "createNewTag success"))
		if "id" in r:
			createdID = r["id"]
		elif "message" in r:
			try:
				createdID = int(r["message"])
			except:
				pass
	except Exception as e:
		results.append(t.safeTry(lambda: (_ for _ in ()).throw(e), "createNewTag"))

	# updateNormalizedTagPath
	if createdID:
		try:
			r = utils.normalizedTagPaths.updateNormalizedTagPath(createdID, "_TEST_SUITE_path", fix.TEST_TENANT_ID)
			results.append(t.assertResultSuccess(r, "updateNormalizedTagPath success"))
		except Exception as e:
			results.append(t.safeTry(lambda: (_ for _ in ()).throw(e), "updateNormalizedTagPath"))

	# deleteTagPath
	if createdID:
		try:
			r = utils.normalizedTagPaths.deleteTagPath(createdID)
			results.append(t.assertResultSuccess(r, "deleteTagPath success"))
			createdID = None
		except Exception as e:
			results.append(t.safeTry(lambda: (_ for _ in ()).throw(e), "deleteTagPath"))

	# Teardown
	if createdID:
		try:
			utils.normalizedTagPaths.deleteTagPath(createdID)
		except:
			pass
	_cleanup()

	return results