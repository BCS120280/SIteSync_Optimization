import json

def getConnectionID(siteName, deviceProfileID):
	#accepts site, deviceprofileID, returns any extra connectionIDs  
	if deviceProfileID == 29:
		if siteName == "LAR":
			return "TWA_100000163.991.AS"
		elif siteName == "SPP":
			return "TWA_100000163.802.AS"
		elif siteName == "GVL":
			return "TWA_100000163.628.AS"
		elif siteName == "SLC":
			return "TWA_100000163.1179.AS"
		elif siteName == "ROB":
			return "TWA_100000163.1176.AS"
		elif siteName == "MTZ":
			return "TWA_100000163.1173.AS"
		elif siteName == "MAN":
			return "TWA_100000163.1170.AS"
		elif siteName == "KEN":
			return "TWA_100000163.1167.AS"
		elif siteName == "GBR":
			return "TWA_100000163.1152.AS"
		elif siteName == "DIR":
			return "TWA_100000163.1149.AS"
		elif siteName == "DET":
			return "TWA_100000163.1125.AS"
		elif siteName == "CAN":
			return "TWA_100000163.1122.AS"
		elif siteName == "ANR":
			return "TWA_100000163.1119.AS"
		elif siteName == "ELP":
			return "TWA_100000163.1101.AS"
		elif siteName == "CBG":
			return "TWA_100000163.1095.AS"
		else:
			return None
	elif deviceProfileID == 24 or deviceProfileID == 58:
		return "TWA_100000163.661.AS"
			
	return None
	
def setTags(devEUI, tagArray):
	return utils.resultParser.createResults(False, "Coming soon")
	
def setProfile(profileID, connectionStrings):
	profile = decoders.model.getModel(1)
	profile['profileConnectionId'] = 2
	res = decoders.model.updateModel(profile)
	return res
	
def addDeviceToExtraActilityConnections(devEUI, deviceProfileID, siteName):
	connectionID = getConnectionID(siteName, deviceProfileID)
	if connectionID != None:
		
		results = setProfile(deviceProfileID, connectionID)
		if utils.resultParser.isResultSuccess(results):
			overallResult = applyConnectionID(devEUI)
			return overallResult
		else:
			return results
	else:
		results = utils.resultParser.createResults(True, "Extra connection not needed")
		return results 
	
def applyConnectionID(devEUI):
	NWSID = enterprise.tenant.getDefaultApp()
	res = system.sitesync.addDeviceToProfileConnection(devEUI, NWSID)
	if res != None and res != "":
		return json.loads(res)
	else:
		return utils.resultParser.createResults(False, "No response")
	
	
	
	
def addToDomain(devEUI, siteID, siteName, group = "Refining"):
	mainNWSID = enterprise.tenant.getDefaultApp()
	results = system.sitesync.associateDeviceWithDomain(devEUI, siteName, mainNWSID, group)
	return json.loads(results)
	
	
def getIsJoined(devEUI):
	##checks if device has joined in actility
	return utils.resultParser.createResults(False, "Coming soon")