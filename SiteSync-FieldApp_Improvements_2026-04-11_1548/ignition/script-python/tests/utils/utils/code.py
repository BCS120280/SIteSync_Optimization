def assertEqual(actual, expected, testName=""):
	if actual == expected:
		return {"name": testName, "status": "PASS", "message": ""}
	return {
		"name": testName,
		"status": "FAIL",
		"message": "Expected {0!r}, got {1!r}".format(expected, actual)
	}

def assertNotEqual(actual, unexpected, testName=""):
	if actual != unexpected:
		return {"name": testName, "status": "PASS", "message": ""}
	return {
		"name": testName,
		"status": "FAIL",
		"message": "Expected value to differ from {0!r}".format(unexpected)
	}

def assertTrue(value, testName=""):
	if value:
		return {"name": testName, "status": "PASS", "message": ""}
	return {
		"name": testName,
		"status": "FAIL",
		"message": "Expected truthy, got {0!r}".format(value)
	}

def assertFalse(value, testName=""):
	if not value:
		return {"name": testName, "status": "PASS", "message": ""}
	return {
		"name": testName,
		"status": "FAIL",
		"message": "Expected falsy, got {0!r}".format(value)
	}

def assertIsNone(value, testName=""):
	if value is None:
		return {"name": testName, "status": "PASS", "message": ""}
	return {
		"name": testName,
		"status": "FAIL",
		"message": "Expected None, got {0!r}".format(value)
	}

def assertIsNotNone(value, testName=""):
	if value is not None:
		return {"name": testName, "status": "PASS", "message": ""}
	return {
		"name": testName,
		"status": "FAIL",
		"message": "Expected non-None value"
	}

def assertIn(item, collection, testName=""):
	if item in collection:
		return {"name": testName, "status": "PASS", "message": ""}
	return {
		"name": testName,
		"status": "FAIL",
		"message": "{0!r} not found in {1!r}".format(item, collection)
	}

def assertNotIn(item, collection, testName=""):
	if item not in collection:
		return {"name": testName, "status": "PASS", "message": ""}
	return {
		"name": testName,
		"status": "FAIL",
		"message": "{0!r} unexpectedly found in {1!r}".format(item, collection)
	}

def assertGreater(a, b, testName=""):
	if a > b:
		return {"name": testName, "status": "PASS", "message": ""}
	return {
		"name": testName,
		"status": "FAIL",
		"message": "Expected {0!r} > {1!r}".format(a, b)
	}

def assertLen(collection, expectedLen, testName=""):
	actual = len(collection)
	if actual == expectedLen:
		return {"name": testName, "status": "PASS", "message": ""}
	return {
		"name": testName,
		"status": "FAIL",
		"message": "Expected length {0}, got {1}".format(expectedLen, actual)
	}

def assertResultSuccess(result, testName=""):
	try:
		mt = result.get("messageType", result.get("status", "")).upper()
		if mt == "SUCCESS":
			return {"name": testName, "status": "PASS", "message": ""}
		return {
			"name": testName,
			"status": "FAIL",
			"message": "Expected SUCCESS result, got {0!r}".format(result)
		}
	except Exception as e:
		return {
			"name": testName,
			"status": "FAIL",
			"message": "Result is not a valid dict: {0!r}".format(e)
		}

def assertResultFailure(result, testName=""):
	try:
		mt = result.get("messageType", result.get("status", "")).upper()
		if mt != "SUCCESS":
			return {"name": testName, "status": "PASS", "message": ""}
		return {
			"name": testName,
			"status": "FAIL",
			"message": "Expected failure result, got SUCCESS"
		}
	except Exception as e:
		return {
			"name": testName,
			"status": "FAIL",
			"message": "Result is not a valid dict: {0!r}".format(e)
		}

def assertRaises(exceptionType, func, args=None, kwargs=None, testName=""):
	args = args or []
	kwargs = kwargs or {}
	try:
		func(*args, **kwargs)
		return {
			"name": testName,
			"status": "FAIL",
			"message": "Expected {0} to be raised".format(exceptionType.__name__)
		}
	except exceptionType:
		return {"name": testName, "status": "PASS", "message": ""}
	except Exception as e:
		return {
			"name": testName,
			"status": "FAIL",
			"message": "Expected {0}, got {1}: {2}".format(
				exceptionType.__name__, type(e).__name__, str(e)
			)
		}

def assertContains(haystack, needle, testName=""):
	if needle in haystack:
		return {"name": testName, "status": "PASS", "message": ""}
	return {
		"name": testName,
		"status": "FAIL",
		"message": "{0!r} not found in string".format(needle)
	}

def assertStartsWith(string, prefix, testName=""):
	if str(string).startswith(prefix):
		return {"name": testName, "status": "PASS", "message": ""}
	return {
		"name": testName,
		"status": "FAIL",
		"message": "{0!r} does not start with {1!r}".format(string, prefix)
	}

def assertIsInstance(obj, cls, testName=""):
	if isinstance(obj, cls):
		return {"name": testName, "status": "PASS", "message": ""}
	return {
		"name": testName,
		"status": "FAIL",
		"message": "Expected instance of {0}, got {1}".format(cls.__name__, type(obj).__name__)
	}

def skip(testName="", reason=""):
	return {"name": testName, "status": "SKIP", "message": reason}

def knownDefect(testName="", reason=""):
	return {"name": testName, "status": "KNOWN_DEFECT", "message": reason}

def safeTry(func, testName=""):
	try:
		return func()
	except Exception as e:
		return {
			"name": testName,
			"status": "FAIL",
			"message": "Unexpected exception: {0}: {1}".format(type(e).__name__, str(e))
		}