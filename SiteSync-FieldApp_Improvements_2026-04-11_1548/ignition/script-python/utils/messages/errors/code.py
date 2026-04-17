def showErrorMessage(errorText):
	system.perspective.print(errorText)
	try:
		system.perspective.openPopup("error", "Popups/error",  params = {"errorText":str(errorText)})
	except Exception as e:
		system.perspective.print(e)
	
def hideErrorMessage(errorText):
	system.perspective.closePopup("error")