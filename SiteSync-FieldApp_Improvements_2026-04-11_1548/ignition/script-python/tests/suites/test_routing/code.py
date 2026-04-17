import tests.utils.utils as t

def run():
	results = []

	# getTile uses `value` instead of `sensorType` parameter -- always NameError
	results.append(t.knownDefect(
		"getTile uses wrong variable name",
		"dashboard.routing.getTile() references undefined 'value' instead of 'sensorType' parameter"
	))

	return results