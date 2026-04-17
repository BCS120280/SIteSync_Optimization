import time

# Registry of all test suite module paths
PURE_SUITES = [
	"tests.suites.test_resultParser",
	"tests.suites.test_boolConverters",
	"tests.suites.test_dropdowns",
	"tests.suites.test_createDevice",
	"tests.suites.test_tagOperations",
	"tests.suites.test_updateDevice",
	"tests.suites.test_bulkuploadV2",
	"tests.suites.test_QRCodeParser",
	"tests.suites.test_model",
	"tests.suites.test_encoder",
	"tests.suites.test_networkserver",
	"tests.suites.test_icons",
	"tests.suites.test_pidGenerator",
	"tests.suites.test_historyconfig",
	"tests.suites.test_dashmanager",
	"tests.suites.test_userPreferences",
	"tests.suites.test_installationReport",
	"tests.suites.test_routing",
	"tests.suites.test_tenant",
]

IO_SUITES = [
	"tests.suites.test_sitehandler_io",
	"tests.suites.test_timeFormatter_io",
	"tests.suites.test_normalizedTagPaths_io",
	"tests.suites.test_tagPathDropdown_io",
	"tests.suites.test_deviceProfileDropDown_io",
	"tests.suites.test_getDevice_io",
	"tests.suites.test_createDevice_io",
	"tests.suites.test_updateDevice_io",
	"tests.suites.test_tagOperations_io",
	"tests.suites.test_images_io",
	"tests.suites.test_diagnostics_io",
	"tests.suites.test_bulkUpload_io",
	"tests.suites.test_bulkuploadV2_io",
	"tests.suites.test_pidGenerator_io",
	"tests.suites.test_replaceDevice_io",
	"tests.suites.test_assetAssociation_io",
	"tests.suites.test_decoder_io",
	"tests.suites.test_encoder_io",
	"tests.suites.test_downlinks_io",
	"tests.suites.test_LoRaSpecs_io",
	"tests.suites.test_udt_io",
	"tests.suites.test_templateParams_io",
	"tests.suites.test_mqtt_io",
	"tests.suites.test_aggregation_io",
	"tests.suites.test_messages_io",
	"tests.suites.test_systemProvisioning",
	"tests.suites.test_activateDevice_io",
]

def _importAndRun(modulePath):
	"""Import a test module by dotted path and call its run() function."""
	try:
		mod = __import__(modulePath, fromlist=["run"])
		return mod.run()
	except ImportError as e:
		return [{"name": modulePath, "status": "FAIL", "message": "Import error: {0}".format(str(e))}]
	except AttributeError:
		return [{"name": modulePath, "status": "FAIL", "message": "Module has no run() function"}]
	except Exception as e:
		return [{"name": modulePath, "status": "FAIL", "message": "Unexpected error: {0}".format(str(e))}]


def _runSuites(suiteList):
	"""Run a list of suite module paths, collect and summarize results."""
	allResults = []
	suiteResults = []
	startTime = time.time()

	for suitePath in suiteList:
		suiteStart = time.time()
		results = _importAndRun(suitePath)
		suiteElapsed = time.time() - suiteStart

		passed = sum(1 for r in results if r["status"] == "PASS")
		failed = sum(1 for r in results if r["status"] == "FAIL")
		skipped = sum(1 for r in results if r["status"] == "SKIP")
		knownDefects = sum(1 for r in results if r["status"] == "KNOWN_DEFECT")

		suiteResults.append({
			"suite": suitePath,
			"total": len(results),
			"passed": passed,
			"failed": failed,
			"skipped": skipped,
			"knownDefects": knownDefects,
			"elapsed": round(suiteElapsed, 2),
		})

		for r in results:
			r["suite"] = suitePath
		allResults.extend(results)

	totalElapsed = time.time() - startTime
	totalPassed = sum(s["passed"] for s in suiteResults)
	totalFailed = sum(s["failed"] for s in suiteResults)
	totalSkipped = sum(s["skipped"] for s in suiteResults)
	totalKnown = sum(s["knownDefects"] for s in suiteResults)
	totalTests = sum(s["total"] for s in suiteResults)

	# Print summary
	print("=" * 60)
	print("TEST RESULTS SUMMARY")
	print("=" * 60)
	for sr in suiteResults:
		status = "PASS" if sr["failed"] == 0 else "FAIL"
		print("  [{0}] {1}  ({2} passed, {3} failed, {4} skipped, {5} known defects) [{6}s]".format(
			status, sr["suite"].split(".")[-1],
			sr["passed"], sr["failed"], sr["skipped"], sr["knownDefects"], sr["elapsed"]
		))
	print("-" * 60)
	print("  Total: {0} tests | {1} passed | {2} failed | {3} skipped | {4} known defects".format(
		totalTests, totalPassed, totalFailed, totalSkipped, totalKnown
	))
	print("  Elapsed: {0:.2f}s".format(totalElapsed))
	print("=" * 60)

	# Print failures in detail
	failures = [r for r in allResults if r["status"] == "FAIL"]
	if failures:
		print("")
		print("FAILURES:")
		print("-" * 60)
		for f in failures:
			print("  [{0}] {1}: {2}".format(f.get("suite", "?").split(".")[-1], f["name"], f["message"]))
		print("")

	return {
		"suites": suiteResults,
		"results": allResults,
		"totals": {
			"tests": totalTests,
			"passed": totalPassed,
			"failed": totalFailed,
			"skipped": totalSkipped,
			"knownDefects": totalKnown,
			"elapsed": round(totalElapsed, 2),
		}
	}


def runAll():
	"""Run all test suites (pure + I/O)."""
	return _runSuites(PURE_SUITES + IO_SUITES)


def runPureOnly():
	"""Run only pure logic suites (no system.* calls, fast and safe)."""
	return _runSuites(PURE_SUITES)


def runIOOnly():
	"""Run only I/O suites (requires live Ignition system)."""
	return _runSuites(IO_SUITES)


def runModule(modulePath):
	"""Run a single test suite by its full dotted path."""
	return _runSuites([modulePath])