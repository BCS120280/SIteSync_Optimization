import tests.utils.utils as t

def run():
	results = []

	results.append(t.assertEqual(
		enterprise.tenant.getDefaultApp(),
		2,
		"getDefaultApp returns hardcoded 2"
	))

	results.append(t.assertIsInstance(
		enterprise.tenant.getDefaultApp(),
		int,
		"getDefaultApp returns an integer"
	))

	return results