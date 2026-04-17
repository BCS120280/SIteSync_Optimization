import tests.utils.utils as t

def run():
	results = []

	# getDefaultColumnPreferences returns a dict copy
	defaults = userPreferences.db.getDefaultColumnPreferences()
	results.append(t.assertIsInstance(defaults, dict, "getDefaultColumnPreferences returns dict"))
	results.append(t.assertIn("devEUI", defaults, "defaults contain devEUI"))
	results.append(t.assertTrue(defaults["devEUI"], "devEUI default is True"))

	# Verify it returns a copy, not the original
	defaults["devEUI"] = False
	fresh = userPreferences.db.getDefaultColumnPreferences()
	results.append(t.assertTrue(fresh["devEUI"], "getDefaultColumnPreferences returns a copy"))

	# getColumnDisplayName
	results.append(t.assertEqual(
		userPreferences.db.getColumnDisplayName("devEUI"), "devEUI",
		"getColumnDisplayName devEUI"
	))
	results.append(t.assertEqual(
		userPreferences.db.getColumnDisplayName("deviceType"), "Sensor Type",
		"getColumnDisplayName deviceType -> Sensor Type"
	))
	results.append(t.assertEqual(
		userPreferences.db.getColumnDisplayName("pandID"), "P&ID",
		"getColumnDisplayName pandID -> P&ID"
	))
	results.append(t.assertEqual(
		userPreferences.db.getColumnDisplayName("unknownKey"), "unknownKey",
		"getColumnDisplayName unknown returns key itself"
	))

	# getColumnOrder
	order = userPreferences.db.getColumnOrder()
	results.append(t.assertIsInstance(order, list, "getColumnOrder returns list"))
	results.append(t.assertIn("status", order, "getColumnOrder includes status"))
	results.append(t.assertIn("devEUI", order, "getColumnOrder includes devEUI"))
	results.append(t.assertEqual(order[0], "status", "getColumnOrder first is status"))

	# Constants
	results.append(t.assertEqual(
		userPreferences.db.PREFERENCE_KEY_COLUMNS,
		"device_manager_columns",
		"PREFERENCE_KEY_COLUMNS constant"
	))

	return results