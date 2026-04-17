import tests.utils.utils as t

def run():
	results = []

	results.append(t.knownDefect(
		"processSystemUpload is empty stub",
		"utils.systemProvisioning.processSystemUpload() has no implementation"
	))

	return results