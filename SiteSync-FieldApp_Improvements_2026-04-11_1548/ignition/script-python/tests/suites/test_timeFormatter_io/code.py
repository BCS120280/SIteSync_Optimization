import tests.utils.utils as t

def run():
	results = []

	# time_elapsed_since_date -- uses system.date.parse and system.date.now
	try:
		r = utils.timeFormatter.time_elapsed_since_date("2020-01-01 12:0:0 AM")
		results.append(t.assertIsInstance(r, str, "time_elapsed_since_date returns string"))
		results.append(t.assertContains(r, "ago", "time_elapsed_since_date contains 'ago'"))
	except Exception as e:
		results.append(t.safeTry(lambda: (_ for _ in ()).throw(e), "time_elapsed_since_date"))

	# timestampLastSeen -- uses epoch seconds
	try:
		r = utils.timeFormatter.timestampLastSeen(946684800)
		results.append(t.assertIsInstance(r, str, "timestampLastSeen returns string"))
		results.append(t.assertContains(r, "ago", "timestampLastSeen contains 'ago'"))
	except Exception as e:
		results.append(t.safeTry(lambda: (_ for _ in ()).throw(e), "timestampLastSeen"))

	# time_elapsed_since_dateTag -- uses system.date.now and getYear
	try:
		pastDate = system.date.parse("2020-06-15 12:00:00", "yyyy-MM-dd HH:mm:ss")
		r = utils.timeFormatter.time_elapsed_since_dateTag(pastDate)
		results.append(t.assertContains(r, "ago", "time_elapsed_since_dateTag recent date"))
	except Exception as e:
		results.append(t.safeTry(lambda: (_ for _ in ()).throw(e), "time_elapsed_since_dateTag recent"))

	# time_elapsed_since_dateTag -- old date returns "Never seen"
	try:
		oldDate = system.date.parse("2022-01-01 00:00:00", "yyyy-MM-dd HH:mm:ss")
		r = utils.timeFormatter.time_elapsed_since_dateTag(oldDate)
		results.append(t.assertEqual(r, "Never seen", "time_elapsed_since_dateTag old date"))
	except Exception as e:
		results.append(t.safeTry(lambda: (_ for _ in ()).throw(e), "time_elapsed_since_dateTag old"))

	return results