import tests.utils.utils as t

def run():
	results = []
	fn = connections.networkserver.showAppropriateOptions

	# ChirpStack
	results.append(t.assertTrue(fn("ChirpStack", "TOKEN"), "ChirpStack shows TOKEN"))
	results.append(t.assertFalse(fn("ChirpStack", "OAUTH"), "ChirpStack hides OAUTH"))
	results.append(t.assertTrue(fn("ChirpStack", "DEVICEPROFILE"), "ChirpStack shows DEVICEPROFILE"))

	# TTN
	results.append(t.assertTrue(fn("TTN", "TOKEN"), "TTN shows TOKEN"))
	results.append(t.assertFalse(fn("TTN", "OAUTH"), "TTN hides OAUTH"))
	results.append(t.assertFalse(fn("TTN", "DEVICEPROFILE"), "TTN hides DEVICEPROFILE"))

	# LORIOT
	results.append(t.assertTrue(fn("LORIOT", "TOKEN"), "LORIOT shows TOKEN"))
	results.append(t.assertFalse(fn("LORIOT", "OAUTH"), "LORIOT hides OAUTH"))
	results.append(t.assertFalse(fn("LORIOT", "DEVICEPROFILE"), "LORIOT hides DEVICEPROFILE"))

	# Other (e.g. ThingPark)
	results.append(t.assertFalse(fn("ThingPark", "TOKEN"), "ThingPark hides TOKEN"))
	results.append(t.assertTrue(fn("ThingPark", "OAUTH"), "ThingPark shows OAUTH"))
	results.append(t.assertFalse(fn("ThingPark", "DEVICEPROFILE"), "ThingPark hides DEVICEPROFILE"))

	# Case insensitivity
	results.append(t.assertTrue(fn("chirpstack", "token"), "case insensitive lowercase"))
	results.append(t.assertTrue(fn("CHIRPSTACK", "TOKEN"), "case insensitive uppercase"))

	return results