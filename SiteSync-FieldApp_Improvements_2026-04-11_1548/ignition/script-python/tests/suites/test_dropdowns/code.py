import tests.utils.utils as t

def run():
	results = []

	r = utils.dropdowns.formatDropdownOption("My Label", 42)
	results.append(t.assertEqual(r["label"], "My Label", "formatDropdownOption label"))
	results.append(t.assertEqual(r["value"], 42, "formatDropdownOption value"))

	r2 = utils.dropdowns.formatDropdownOption("", None)
	results.append(t.assertEqual(r2["label"], "", "formatDropdownOption empty label"))
	results.append(t.assertIsNone(r2["value"], "formatDropdownOption None value"))

	return results