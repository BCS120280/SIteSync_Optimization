import time
def showSuccess(successMessage):

	system.perspective.openPopup("success", "Popups/success",  params = {"successText":successMessage})
	time.sleep(3)
	try:
		system.perspective.closePopup("success")
	except Exception as e:
		system.util.getLogger("Popups.Success").warn("closePopup('success') failed: {}".format(str(e)))

def showSuccessWait(successMessage):

	system.perspective.openPopup("success", "Popups/success",  params = {"successText":successMessage})
