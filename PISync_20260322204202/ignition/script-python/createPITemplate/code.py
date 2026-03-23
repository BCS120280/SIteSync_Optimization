

def createInstance(tagPath, tagName):
	limitedModel = system.tag.readBlocking(["{0}/metaData/sparkplug/template".format(tagPath)])[0].value
	if limitedModel != None:
		baseTagPath = "[default]PI Integration"
	  
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
		system.perspective.print(createReult)
		system.tag.writeBlocking([tagPath + ".activated"], [True])
		return createReult
	