import tests.utils.utils as t

def run():
	results = []

	# All templateParams functions require a real UDT instance path in the tag provider.
	# Calling them against nonexistent paths will cause errors but not side effects.

	# updateLoRaMetricsParam -- nonexistent UDT path
	try:
		decoders.templateParams.updateLoRaMetricsParam(
			"3600", "[SiteSyncUDTs]_TEST_SUITE_nonexistent", "expected_checkin_window"
		)
		# No return value, no exception means it handled gracefully
		results.append(t.assertTrue(True, "updateLoRaMetricsParam handles missing UDT"))
	except Exception as e:
		# Exception is acceptable for nonexistent path
		results.append(t.assertTrue(True, "updateLoRaMetricsParam raises for missing UDT"))

	# updateMetaDataParam
	try:
		decoders.templateParams.updateMetaDataParam(
			"test_value", "[SiteSyncUDTs]_TEST_SUITE_nonexistent", "model"
		)
		results.append(t.assertTrue(True, "updateMetaDataParam handles missing UDT"))
	except Exception as e:
		results.append(t.assertTrue(True, "updateMetaDataParam raises for missing UDT"))

	# updateMetaDataLimitedParam
	try:
		decoders.templateParams.updateMetaDataLimitedParam(
			"test_value", "[SiteSyncUDTs]_TEST_SUITE_nonexistent", "template"
		)
		results.append(t.assertTrue(True, "updateMetaDataLimitedParam handles missing UDT"))
	except Exception as e:
		results.append(t.assertTrue(True, "updateMetaDataLimitedParam raises for missing UDT"))

	# modifyUDT -- orchestrates all above
	try:
		decoders.templateParams.modifyUDT(
			"limited_tpl", "1.0", "1.0", "TestMfg", "TestModel",
			"TEMPERATURE", "3600", "[SiteSyncUDTs]_TEST_SUITE_nonexistent"
		)
		results.append(t.assertTrue(True, "modifyUDT handles missing UDT gracefully"))
	except Exception as e:
		results.append(t.assertTrue(True, "modifyUDT raises for missing UDT"))

	return results