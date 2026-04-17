def createLog(text, user, entityID):
	if user != None:
		text = "{0} by {1}".format(text, user)
	system.sitesync.addLog(text, entityID)