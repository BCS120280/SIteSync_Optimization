def getTopic(tagPath):
	#customizabl
	standardTopic = "mpc/{0}"
	tagName = tagPath.split(']')[1]
	return standardTopic.format(tagName)