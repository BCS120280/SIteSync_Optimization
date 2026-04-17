import tests.utils.utils as t
import tests.fixtures.fixtures as fix

def run():
	results = []

	# getFleetHealth
	try:
		health = dashboard.aggregation.getFleetHealth(fix.TEST_TENANT_ID)
		results.append(t.assertIsInstance(health, dict, "getFleetHealth returns dict"))
		results.append(t.assertIn("totalDevices", health, "getFleetHealth has totalDevices"))
		results.append(t.assertIn("online", health, "getFleetHealth has online"))
		results.append(t.assertIn("alarms", health, "getFleetHealth has alarms"))
		results.append(t.assertIn("lowBattery", health, "getFleetHealth has lowBattery"))

		# Values should be non-negative integers
		results.append(t.assertTrue(
			health["totalDevices"] >= 0,
			"getFleetHealth totalDevices >= 0"
		))
		results.append(t.assertTrue(
			health["online"] >= 0,
			"getFleetHealth online >= 0"
		))
	except Exception as e:
		results.append(t.safeTry(lambda: (_ for _ in ()).throw(e), "getFleetHealth"))

	return results