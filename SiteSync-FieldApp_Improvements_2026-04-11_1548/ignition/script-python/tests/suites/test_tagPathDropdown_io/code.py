import tests.utils.utils as t

def run():
	results = []

	try:
		providers = utils.tagPathDropdown.getTagProviders()
		results.append(t.assertIsInstance(providers, list, "getTagProviders returns list"))

		# Verify excluded providers are not present
		providerNames = [p["label"] for p in providers]
		results.append(t.assertNotIn("SiteSync", providerNames, "SiteSync excluded"))
		results.append(t.assertNotIn("MQTT Engine", providerNames, "MQTT Engine excluded"))
		results.append(t.assertNotIn("MQTT Transmission", providerNames, "MQTT Transmission excluded"))
		results.append(t.assertNotIn("System", providerNames, "System excluded"))

		# Each entry has label and value
		if len(providers) > 0:
			results.append(t.assertIn("label", providers[0], "provider has label"))
			results.append(t.assertIn("value", providers[0], "provider has value"))
		else:
			results.append(t.skip("provider structure", "no providers found"))

	except Exception as e:
		results.append(t.safeTry(lambda: (_ for _ in ()).throw(e), "getTagProviders"))

	return results