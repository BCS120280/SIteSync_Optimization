import tests.utils.utils as t
import tests.fixtures.fixtures as fix

def _cleanup():
	"""Remove any leftover test tenants from previous runs."""
	try:
		sites = utils.sitehandler.getSites()
		for s in sites:
			if s.get("tenantName", "").startswith("_TEST_SUITE_"):
				try:
					utils.sitehandler.deleteSite(s["id"])
				except:
					pass
	except:
		pass

def run():
	results = []
	_cleanup()
	createdID = None

	# getSites returns a list
	try:
		sites = utils.sitehandler.getSites()
		results.append(t.assertIsInstance(sites, list, "getSites returns list"))
	except Exception as e:
		results.append(t.safeTry(lambda: (_ for _ in ()).throw(e), "getSites"))

	# getSitesDropdown returns list of {label, value}
	try:
		dd = utils.sitehandler.getSitesDropdown()
		results.append(t.assertIsInstance(dd, list, "getSitesDropdown returns list"))
		if len(dd) > 0:
			results.append(t.assertIn("label", dd[0], "getSitesDropdown has label key"))
			results.append(t.assertIn("value", dd[0], "getSitesDropdown has value key"))
		else:
			results.append(t.skip("getSitesDropdown structure", "no tenants to inspect"))
	except Exception as e:
		results.append(t.safeTry(lambda: (_ for _ in ()).throw(e), "getSitesDropdown"))

	# createSite
	try:
		createdID = utils.sitehandler.createSite()
		results.append(t.assertIsNotNone(createdID, "createSite returns ID"))
		results.append(t.assertNotEqual(createdID, False, "createSite not False"))
	except Exception as e:
		results.append(t.safeTry(lambda: (_ for _ in ()).throw(e), "createSite"))

	# updateSite
	if createdID:
		try:
			r = utils.sitehandler.updateSite(createdID, "test notes", "US915", "_TEST_SUITE_updated")
			results.append(t.assertResultSuccess(r, "updateSite success"))
		except Exception as e:
			results.append(t.safeTry(lambda: (_ for _ in ()).throw(e), "updateSite"))

	# deleteSite
	if createdID:
		try:
			r = utils.sitehandler.deleteSite(createdID)
			results.append(t.assertResultSuccess(r, "deleteSite success"))
			createdID = None
		except Exception as e:
			results.append(t.safeTry(lambda: (_ for _ in ()).throw(e), "deleteSite"))

	# Teardown
	if createdID:
		try:
			utils.sitehandler.deleteSite(createdID)
		except:
			pass
	_cleanup()

	return results