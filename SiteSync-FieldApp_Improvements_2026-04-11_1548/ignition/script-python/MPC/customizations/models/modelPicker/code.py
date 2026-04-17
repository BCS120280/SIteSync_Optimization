def getDeviceTypes():
	##returns device types as outlined by PI Model types
	results = []

	tags = system.tag.browse("[default]_types_/SiteSyncModels").results
	
	for r in tags:
		#print(r['name'])
		results.append({"label":r['name'], "value":r['name']})
		
	return results
	
	
def filterLimitedModels(folderName):
	tags = system.tag.browse("[default]_types_/SiteSyncModels/{0}".format(folderName)).results
	results = []
	for r in tags:
		if "Template" not in r['name']:
			modelPath = str(r['fullPath']).split("_types_/SiteSyncModels/")[1]
			modelName = modelPath.split('/')[-1]
			results.append({"label":modelName, "value":modelPath})
	return results
	