import tests.utils.utils as t
import tests.fixtures.fixtures as fix

def run():
	results = []

	try:
		options, mfgOptions = utils.deviceProfileDropDown.getDeviceProfiles(fix.TEST_TENANT_ID)

		results.append(t.assertIsInstance(options, list, "getDeviceProfiles options is list"))
		results.append(t.assertIsInstance(mfgOptions, list, "getDeviceProfiles mfgOptions is list"))

		if len(options) > 0:
			results.append(t.assertIn("label", options[0], "option has label"))
			results.append(t.assertIn("value", options[0], "option has value"))
		else:
			results.append(t.skip("option structure", "no profiles found"))

		if len(mfgOptions) > 0:
			results.append(t.assertIn("label", mfgOptions[0], "mfgOption has label (manufacturer)"))
			results.append(t.assertIn("value", mfgOptions[0], "mfgOption has value (list of models)"))
		else:
			results.append(t.skip("mfgOption structure", "no manufacturers found"))

	except Exception as e:
		results.append(t.safeTry(lambda: (_ for _ in ()).throw(e), "getDeviceProfiles"))

	return results