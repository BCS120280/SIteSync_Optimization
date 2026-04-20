def showErrorMessage(errorText):
	system.perspective.openPopup("error", "Popups/error",  params = {"errorText":errorText})
	system.db.runNamedQuery(path= "createLog", parameters = {'message':errorText})
	
def hideErrorMessage(errorText):
	try:
		system.perspective.closePopup("error")
	except Exception as e:
		system.util.getLogger("Popups.Error").warn("closePopup('error') failed: {}".format(str(e)))