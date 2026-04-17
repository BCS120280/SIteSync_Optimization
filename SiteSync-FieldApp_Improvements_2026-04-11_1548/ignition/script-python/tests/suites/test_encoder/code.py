import tests.utils.utils as t

def run():
	results = []
	fn = decoders.encoder.unflattenAnswers

	# Simple flat keys
	r = fn({"threshold": 10, "enabled": True})
	results.append(t.assertEqual(r["threshold"], 10, "unflatten simple key"))
	results.append(t.assertEqual(r["enabled"], True, "unflatten simple bool"))

	# Dotted keys -> nested
	r = fn({"threshold.high": 90, "threshold.low": 10})
	results.append(t.assertEqual(r["threshold"]["high"], 90, "unflatten nested high"))
	results.append(t.assertEqual(r["threshold"]["low"], 10, "unflatten nested low"))

	# input. prefix stripping
	r = fn({"input.threshold.high": 90, "input.enabled": True})
	results.append(t.assertEqual(r["threshold"]["high"], 90, "unflatten strips input. prefix"))
	results.append(t.assertEqual(r["enabled"], True, "unflatten strips input. for simple key"))

	# Deeper nesting
	r = fn({"a.b.c.d": "deep"})
	results.append(t.assertEqual(r["a"]["b"]["c"]["d"], "deep", "unflatten 4-level nesting"))

	# Empty dict
	r = fn({})
	results.append(t.assertEqual(r, {}, "unflatten empty dict"))

	# Mixed input. and non-input. keys
	r = fn({"input.x": 1, "y": 2})
	results.append(t.assertEqual(r["x"], 1, "unflatten mixed: input.x stripped"))
	results.append(t.assertEqual(r["y"], 2, "unflatten mixed: y preserved"))

	return results