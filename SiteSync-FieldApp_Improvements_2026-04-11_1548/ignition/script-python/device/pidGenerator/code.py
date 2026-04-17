import json


def createLoopHolder(siteName):
	# Import system library (available in Ignition's script environment)
	# This script can be run in the Script Console or in a Gateway/Client event.
	
	# Define the base path where the tag will be created
	basePath = "[PID Loops]{0}".format(siteName)  # The tag provider (default provider in this case)
	
	# Define the tag configuration as a Python dictionary
	newTag = {
	    "name": "Loop Number",          # Tag name
	    "tagType": "AtomicTag",
	    "valueSource": "memory" ,# Memory, OPC, Query, etc.
	    "dataType": "Int4",          # Data type (Int4 = 32-bit integer)
	    "value": 1000                 # Initial value

	}
	
	# Create the tag
	try:
	    results = system.tag.configure(
	        basePath,
	        [newTag],                # Must be a list of tag dictionaries
	        "o"                      # Collision policy: "o" = overwrite, "m" = merge, "a" = abort
	    )
	    print("Tag creation result:", results)
	except Exception as e:
	    print("Error creating tag:", e)

# Device type to abbreviation mapping
TYPE_ABBREVIATIONS = {
	'LEVEL': 'LI',
	'POSITION': 'ZI',
	'VALVEPOSITION': 'ZI',
	'TEMPERATURE': 'TI',
	'PRESSURE': 'PI',
	'VIBRATION': 'VI',
	'STEAMTRAP': 'X',
	'VOLTAGE': 'EI',
	'CURRENT': 'II',
	'HOTDROP': 'II',
	'FLOW': 'FI',
	'FLOWMETER': 'FI'
}

def getTypeAbbreviation(deviceType):
	"""
	Maps a device type string to its PID abbreviation.
	Returns 'X' for unknown types.
	"""
	if deviceType is None:
		return 'X'

	upperType = str(deviceType).upper().strip()
	return TYPE_ABBREVIATIONS.get(upperType, 'X')


def getNextLoopNumber(siteName):
	"""
	Reads the current loop number from the tag, increments it,
	writes back the new value, and returns it.
	Tag path: [SiteSyncUDTs]loopNumbers/{siteName}/loop
	"""
	tagPath = "[PID Loops]{0}/Loop Number".format(siteName)
	exists = system.tag.exists(tagPath)
	if not exists:
		createLoopHolder(siteName)
	try:
		currentValues = system.tag.readBlocking([tagPath])
		currentValue = currentValues[0].value

		if currentValue is None:
			currentValue = 0

		newValue = currentValue + 1

		writeResults = system.tag.writeBlocking([tagPath], [newValue])

		if writeResults[0].isGood():
			return newValue
		else:
			system.perspective.print("Warning: Failed to write loop number to tag")
			return newValue

	except Exception as e:
		system.perspective.print("Error accessing loop number tag: {0}".format(str(e)))
		return utils.resultParser.createResults(False, "Error accessing loop number: {0}".format(str(e)))


def generatePidName(unitNumber, deviceType, siteName):
	"""
	Generates a PID name in format: {unitNumber}-{typeAbbreviation}-{loopNumber:03d}
	Example: 63-ZI-001

	Returns a result object with the generated name or error message.
	"""
	if not unitNumber or str(unitNumber).strip() == '':
		return utils.resultParser.createResults(False, "Unit number is required")

	if not deviceType or str(deviceType).strip() == '':
		return utils.resultParser.createResults(False, "Device type is required")

	if not siteName or str(siteName).strip() == '':
		return utils.resultParser.createResults(False, "Site name is required")

	abbreviation = getTypeAbbreviation(deviceType)

	loopResult = getNextLoopNumber(siteName)

	if isinstance(loopResult, dict) and 'messageType' in loopResult:
		return loopResult

	loopNumber = loopResult

	pidName = "{0}-{1}-{2:03d}".format(
		str(unitNumber).strip(),
		abbreviation,
		loopNumber
	)

	result = {
		'messageType': 'SUCCESS',
		'message': pidName,
		'pidName': pidName,
		'loopNumber': loopNumber,
		'abbreviation': abbreviation
	}

	return result


def getDeviceTypeFromProfile(modelID):
	"""
	Fetches the device profile by ID and returns the device_type field.
	Returns None if the profile cannot be found.
	"""
	try:
		if modelID is None or modelID == -1:
			return None

		profile = decoders.model.getModel(modelID)

		if profile and 'device_type' in profile:
			return profile['device_type']

		return None

	except Exception as e:
		system.perspective.print("Error getting device type from profile: {0}".format(str(e)))
		return None


def getSiteNameFromTenant(tenantID):
	"""
	Looks up the site/tenant name from the tenant ID.
	This is used to construct the tag path for loop numbers.

	NOTE: This function may need to be updated based on how
	your system determines the site name for the tag path.
	"""
	try:
		if tenantID is None:
			return None

		sites = utils.sitehandler.getSites()

		for site in sites:
			if site.get('id') == tenantID:
				tenantName = site.get('tenantName', '')
				return tenantName.replace(' ', '_')

		return None

	except Exception as e:
		system.perspective.print("Error getting site name from tenant: {0}".format(str(e)))
		return None