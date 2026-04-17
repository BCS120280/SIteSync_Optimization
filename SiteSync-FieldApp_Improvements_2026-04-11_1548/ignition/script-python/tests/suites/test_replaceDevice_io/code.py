import tests.utils.utils as t
import tests.fixtures.fixtures as fix

def _cleanup():
	for eui in [fix.TEST_DEVEUI_01, fix.TEST_DEVEUI_02]:
		try:
			system.sitesync.archiveDevice(eui)
		except:
			pass

def run():
	results = []
	_cleanup()

	# replace -- invalid old EUI
	try:
		r = device.replaceDevice.replace("short", fix.TEST_DEVEUI_02)
		results.append(t.assertResultFailure(r, "replace invalid old EUI"))
		results.append(t.assertContains(
			utils.resultParser.getResultMessage(r), "Invalid old",
			"replace invalid old EUI message"
		))
	except Exception as e:
		results.append(t.safeTry(lambda: (_ for _ in ()).throw(e), "replace invalid old"))

	# replace -- invalid new EUI
	try:
		r = device.replaceDevice.replace(fix.TEST_DEVEUI_01, "short")
		results.append(t.assertResultFailure(r, "replace invalid new EUI"))
	except Exception as e:
		results.append(t.safeTry(lambda: (_ for _ in ()).throw(e), "replace invalid new"))

	# replace -- same EUI
	try:
		r = device.replaceDevice.replace(fix.TEST_DEVEUI_01, fix.TEST_DEVEUI_01)
		results.append(t.assertResultFailure(r, "replace same EUI"))
		results.append(t.assertContains(
			utils.resultParser.getResultMessage(r), "same",
			"replace same EUI message"
		))
	except Exception as e:
		results.append(t.safeTry(lambda: (_ for _ in ()).throw(e), "replace same EUI"))

	# replace -- old device not found
	try:
		r = device.replaceDevice.replace("0000000000000000", fix.TEST_DEVEUI_02)
		results.append(t.assertResultFailure(r, "replace old device not found"))
	except Exception as e:
		results.append(t.safeTry(lambda: (_ for _ in ()).throw(e), "replace not found"))

	_cleanup()
	return results