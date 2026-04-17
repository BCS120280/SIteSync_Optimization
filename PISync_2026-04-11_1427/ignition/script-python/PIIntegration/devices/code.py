import json
def findUnactivatedDevices(searchDirectory, activationName):
	results = system.tag.browse(path = searchDirectory, filter = {'name':activationName, "recursive":True})
	unactivatedPaths = []
	
	for result in results.getResults():
		if "_types_" not in str(result['fullPath']): 
			print result['value'].value
			if result['value'].value == False:
				print "Found unactivated node"
				unactivatedPaths.append(str(result['fullPath']))
	return unactivatedPaths
	
	
def getDeviceNameFromPath(tagPath, activationName):
	tagName = tagPath.replace("/{0}".format(activationName), "").split('/')[-1]
	return tagName
	
	
def findDevices():
	deviceList = []
	devices = json.loads(system.sitesync.listDevices(1))
	tagPaths = []
	for d in devices:
		if d['fullTagPath'] != "" and d['fullTagPath'] != "[]":
			activated = system.tag.readBlocking(["[default]PI Integration/{0}.sentToPI".format(d['fullTagPath'].replace("[default]", "")), "{0}/metaData/sparkplug/template".format(d['fullTagPath'])])
			system.perspective.print(d['fullTagPath'])
			
			system.perspective.print(activated)
			##if "SPP" in str(d['fullTagPath']):
				
			if activated[0].value == None:
				
				if activated[1].value != None and activated[1].value != "":
					device = {
							"tagPath":d['fullTagPath'],
							"name": d['deviceName'], 
							"deviceType":d['deviceType']
							}
					deviceList.append(device)
			else:
				formattedDate = system.date.parse(activated[0].value, "dd-MM-yyyy")
				activatedToday =  system.date.daysBetween(formattedDate, system.date.now())
				system.perspective.print(activatedToday)
				system.perspective.print(activatedToday <= 1)
				if activatedToday <= 1:
					
					device = {
							"tagPath":d['fullTagPath'],
							"name": d['deviceName'], 
							"deviceType":d['deviceType']
							}
					deviceList.append(device)


		
	return deviceList
	
	
	
	