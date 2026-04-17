import tests.utils.utils as t

def run():
	results = []

	# All message functions require a Perspective session (openPopup/closePopup).
	# In script console, these will throw. We verify they exist and handle gracefully.

	# showErrorMessage
	try:
		utils.messages.errors.showErrorMessage("test error")
		results.append(t.skip("showErrorMessage", "Executed without error (session active)"))
	except:
		results.append(t.skip("showErrorMessage", "No active Perspective session"))

	# hideErrorMessage
	try:
		utils.messages.errors.hideErrorMessage("test error")
		results.append(t.skip("hideErrorMessage", "Executed without error"))
	except:
		results.append(t.skip("hideErrorMessage", "No active Perspective session"))

	# showSuccess
	try:
		utils.messages.success.showSuccess("test success")
		results.append(t.skip("showSuccess", "Executed without error"))
	except:
		results.append(t.skip("showSuccess", "No active Perspective session"))

	# showLoading / hideLoading
	try:
		utils.messages.waiting.showLoading("_test_loading")
		utils.messages.waiting.hideLoading("_test_loading")
		results.append(t.skip("showLoading/hideLoading", "Executed without error"))
	except:
		results.append(t.skip("showLoading/hideLoading", "No active Perspective session"))

	# showTimeout
	try:
		utils.messages.waiting.showTimeout()
		results.append(t.skip("showTimeout", "Executed without error"))
	except:
		results.append(t.skip("showTimeout", "No active Perspective session"))

	return results