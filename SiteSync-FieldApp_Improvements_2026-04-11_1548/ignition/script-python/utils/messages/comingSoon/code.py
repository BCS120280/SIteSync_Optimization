def show(messageText):
	system.perspective.openPopup("comingSoon", "Popups/comingSoon", params={"messageText": str(messageText)})

def hide():
	system.perspective.closePopup("comingSoon")