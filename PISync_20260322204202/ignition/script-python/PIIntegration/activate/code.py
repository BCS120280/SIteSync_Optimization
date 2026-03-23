import time
import json

def forceCheckIn(tagList):
	return False
def replaceNull(value):
	if value == None:
		return 0
	else:
		return 0

def publishDevice(rootTag):
	logger = system.util.getLogger("MQTTPublish")
	try:
		logger.info("Starting publish")
		tags = system.tag.browse(path=rootTag, filter={"recursive":False})
		deviceJSON = {}
		for t in tags:
			tagName = str(t['fullPath']).split('/')[-1]
			deviceJSON[tagName] = replaceNull(t['value'].value)
			
		topic = rootTag.replace("[default]PI Integration", "mpc")
		
		system.cirruslink.transmission.publish("Chariot", topic, json.dumps(deviceJSON), 0, 0)
		#system.tag.writeBlocking([rootTag], [sourceTagPath])
		now = system.date.now()
		today = system.date.format(now, "dd-MM-yyyy")
		system.tag.writeBlocking(["{0}.sentToPI".format(rootTag)], [today])
		return True
	except Exception as e:
		logger.error("error publishing device {0}".format(str(e)))
		return False

	
def moveToFolder(tagList):
	system.tag.writeBlocking(tagList, [True])
	
	
def selectAll(tableData):
	for row in tableData:
		row['selected'] = True
	return tableData
	
	
def flickerDevice(rootTag):
	publishDevice(rootTag)
#	try:
#		tagType = system.tag.readBlocking([rootTag + ".valueSource"])[0].value
#		if tagType == "reference":
#			sourceTagPath = system.tag.readBlocking([rootTag + ".sourceTagPath"])[0].value
#			system.tag.writeBlocking([rootTag + ".sourceTagPath"], [None])
#			time.sleep(.5)
#			system.tag.writeBlocking([rootTag + ".sourceTagPath"], [sourceTagPath])
#		elif tagType == "memory":
#			sourceTagPath = system.tag.readBlocking([rootTag])[0].value
#			system.tag.writeBlocking([rootTag], [None])
#			time.sleep(.5)
#			system.tag.writeBlocking([rootTag], [sourceTagPath])
#		return "Success"
#	except Exception as e:
#		return str(e)
		
	
def activateDevice(tagPath):
	system.tag.writeBlocking([tagPath + "/PIactivate"], [True])
	
	
def createInstance(tagPath, tagName):
	limitedModel = system.tag.readBlocking(["{0}/metaData/sparkplug/template".format(tagPath)])[0].value
	if limitedModel != None:
		baseTagPath = "[default]PI Integration/{0}".format(tagPath.replace(tagName, '').replace('[default]', ''))
	  
		# Properties that will be configured on that Tag.
		typeId = "SiteSyncModels/" + limitedModel
		tagType = "UdtInstance"
		# Parameters to pass in.
		sourceTagPath = tagPath
		  
		# Configure the Tag.
		tag = {
		            "name": tagName,         
		            "typeId" : typeId,
		            "tagType" : tagType,
		            "parameters" : {
		              "tagPath" :sourceTagPath
		              }
		       }
		 
		# Set the collision policy to Abort. That way if a tag already exists at the base path,
		# we will not override the Tag. If you are overwriting an existing Tag, then set this to "o".
		collisionPolicy = "a"
		  
		# Create the Tag.
		createReult = system.tag.configure(baseTagPath, [tag], collisionPolicy)
		#system.perspective.print(createReult)
		system.tag.writeBlocking([tagPath + ".activated"], [True])
		return createReult
		
		
def getAllDevicesInTargetFolder(searchDirectory):
	tagPaths = []
	results = system.tag.browse(path = "[default]PI Integration", filter = { "recursive":True, 'tagType': "UdtInstance"})
	for result in results.getResults():
		if "/LoRaMetrics" not in str(result['fullPath']): 
			tagPaths.append(str(result['fullPath']))
		
	return tagPaths
	
def getAllFlickerableTagsTargetFolder(searchDirectory):
	tagPaths = []
	results = system.tag.browse(path = "[default]PI Integration", filter = { "recursive":True, 'tagType': "AtomicTag"})
	for result in results.getResults():
		tagPaths.append(str(result['fullPath']))
		
	return tagPaths



def selectAll(dataset, select):
	system.perspective.print(select)
	for row in dataset:
		system.perspective.print(row)
		row['selected'] = select
		system.perspective.print(row)
	return dataset