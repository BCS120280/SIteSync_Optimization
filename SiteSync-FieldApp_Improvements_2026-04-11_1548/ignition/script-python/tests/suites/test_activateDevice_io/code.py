import tests.utils.utils as t

def run():
	results = []

	# createLimitedInstance -- KNOWN_DEFECT: references undefined baseTagPath
	results.append(t.knownDefect(
		"createLimitedInstance references undefined baseTagPath",
		"device.activateDevice.createLimitedInstance() uses 'baseTagPath' which is never defined"
	))

	# refreshSparkplugTransmission -- I/O, writes to MQTT Transmission tag
	# Skip to avoid triggering real MQTT operations
	results.append(t.skip(
		"refreshSparkplugTransmission",
		"Skipped: would trigger MQTT Transmission birth (2s sleep + tag write)"
	))

	return results