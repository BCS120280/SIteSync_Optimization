import json
import tests.utils.utils as t

def run():
	results = []

	raw = device.updateDevice.formatUpdateDeviceRequest("ffff000000000001", "TestDev", "A test device")
	r = json.loads(raw)

	results.append(t.assertEqual(r["devEUI"], "ffff000000000001", "formatUpdate devEUI"))
	results.append(t.assertEqual(r["name"], "TestDev", "formatUpdate name"))
	results.append(t.assertEqual(r["description"], "A test device", "formatUpdate description"))
	results.append(t.assertIsInstance(raw, str, "formatUpdate returns JSON string"))

	# Ensure only expected keys
	results.append(t.assertEqual(len(r.keys()), 3, "formatUpdate has exactly 3 keys"))

	return results