def getLocationData():
	folderPath = "[default]Location"
	results = []
	
	# Browse the folder to get all tag instances
	browse = system.tag.browse(folderPath)
	
	tagPaths = []
	tagNames = []
	tags = system.tag.browse("[default]Location", {"tagType":"UdtInstance", "recursive":True}).results
	for tag in tags:
		tagName = tag["name"]
		tagNames.append(tagName)
		fullPath = str(tag['fullPath'])
		latPath = "{0}/LAT".format(fullPath)
		lonPath = "{0}/LNG".format(fullPath)
		
		tagPaths.append(latPath)
		tagPaths.append(lonPath)

	# Batch read all GPS values
	values = system.tag.readBlocking(tagPaths)
	
	# Build response
	index = 0
	for name in tagNames:
	
	    lat = values[index].value
	    lon = values[index + 1].value
	    index += 2
	    results.append({"name": name,
	        "lat": lat,
	        "lon": lon })
	resultMessage = {"status":"SUCCESS", "data":results}
	return resultMessage