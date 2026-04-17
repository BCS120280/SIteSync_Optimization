import time
def createInstance(tagPath, tagName, modelID):
	try:
		# Retry up to 3 times with 500ms delay to handle UDT propagation lag after createTag
		tagRead = None
		for attempt in range(3):
			tagRead = system.tag.readBlocking(["{0}/metaData/sparkplug/template".format(tagPath)])[0]
			if "Good" in str(tagRead.quality) and tagRead.value:
				break
			if attempt < 2:
				time.sleep(5)

		# Verify the tag read came back with Good quality before trusting the value
		if "Good" not in str(tagRead.quality):
			return utils.resultParser.createResults(False, "Template tag read failed for {0} (quality: {1}). UDT may not exist or has not propagated.".format(tagPath, tagRead.quality))

		limitedModel = tagRead.value
		# Guard against None and empty string — both produce a broken typeId
		if not limitedModel:
			return utils.resultParser.createResults(False, "PI Template not set for device profile {0}. Device still added, but will not be in PI".format(modelID))

		assembledPath = tagPath.replace('[default]', '').replace(tagName, "")

		baseTagPath = "[default]PI Integration/{0}".format(assembledPath)
		if modelID == 24 or modelID == 58:
			baseTagPath = "[default]Location/{0}".format(assembledPath)


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
		createResult = system.tag.configure(baseTagPath, [tag], collisionPolicy)
		if "Good" in str(createResult):
			results = addTagToPi("{0}{1}".format(baseTagPath, tagName))
			return results
		return utils.resultParser.createResults(False, "Error creating PI instance for {0}; {1}".format(tagName, createResult))
	except Exception as e:
		return utils.resultParser.createResults(False, str(e))
		
		
		
def addTagToPi(tagPath):
	logger = system.util.getLogger("SiteSync-PiTagCreator")
	logger.info("Creating PI tag: " + tagPath)
	try:
		tagPathArray = [tagPath]
		adapterResults = PIIntegration.adapter.addToDataSelection(tagPathArray)
		results = PIIntegration.AF.createPITag(tagPath)
		logger.info("Adapter add result: " + str(adapterResults) + " PI tag creation results: " + str(results))
		return utils.resultParser.createResults(True, "Adapter add result: " + str(adapterResults) + " PI tag creation results: " + str(results))
	except Exception as e:
		logger.error("Error creating PI tag: " + tagPath + "; " + str(e))
		return utils.resultParser.createResults(False, "Error creating PI tag: " + tagPath + "; " + str(e))