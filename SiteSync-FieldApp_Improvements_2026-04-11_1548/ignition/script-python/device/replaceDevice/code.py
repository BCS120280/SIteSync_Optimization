import json

def replace(oldDevEUI, newDevEUI, preserveMetadata=True):
	"""
	Replace an existing device with a new one.

	Transfers all metadata, configuration, and associations from the old device
	to the new device, then archives the old device.

	Args:
		oldDevEUI: The EUI of the device being replaced
		newDevEUI: The EUI of the new replacement device
		preserveMetadata: If True, copy metadata from old to new device

	Returns:
		Standard result object with messageType and message
	"""
	try:
		if not oldDevEUI or len(oldDevEUI) != 16:
			return utils.resultParser.createResults(False, "Invalid old device EUI")

		if not newDevEUI or len(newDevEUI) != 16:
			return utils.resultParser.createResults(False, "Invalid new device EUI")

		if oldDevEUI.lower() == newDevEUI.lower():
			return utils.resultParser.createResults(False, "New EUI cannot be same as old EUI")

		oldDevice = device.get.getDevice(oldDevEUI)
		if oldDevice is None or 'status' in oldDevice and oldDevice['status'] == 'ERROR':
			return utils.resultParser.createResults(False, "Old device not found")

		existingNew = device.get.getDevice(newDevEUI)
		if existingNew is not None and 'devEUI' in existingNew:
			return utils.resultParser.createResults(False, "New device EUI already exists in system")

		deviceTypeID = oldDevice.get('deviceTypeID', -1)
		deviceName = oldDevice.get('deviceName', '')
		tenantID = oldDevice.get('tenantID', 1)

		createResult = json.loads(system.sitesync.createDevice(
			newDevEUI,
			deviceName,
			deviceTypeID,
			tenantID
		))

		if not utils.resultParser.isResultSuccess(createResult):
			return createResult

		if preserveMetadata:
			oldTagPath = oldDevice.get('fullTagPath', '')
			newDevice = device.get.getDevice(newDevEUI)
			newTagPath = newDevice.get('fullTagPath', '') if newDevice else ''

			if oldTagPath and newTagPath:
				metadataTransferResult = _transferMetadata(oldTagPath, newTagPath)
				if not utils.resultParser.isResultSuccess(metadataTransferResult):
					system.perspective.print("Warning: Metadata transfer incomplete: " + utils.resultParser.getResultMessage(metadataTransferResult))

		archiveResult = _archiveDevice(oldDevEUI)
		if not utils.resultParser.isResultSuccess(archiveResult):
			system.perspective.print("Warning: Could not archive old device: " + utils.resultParser.getResultMessage(archiveResult))

		_logReplacement(oldDevEUI, newDevEUI, preserveMetadata)

		return utils.resultParser.createResults(True, "Device replaced successfully. New EUI: " + newDevEUI)

	except Exception as e:
		system.perspective.print("Error replacing device: " + str(e))
		return utils.resultParser.createResults(False, "Error replacing device: " + str(e))


def _transferMetadata(oldTagPath, newTagPath):
	"""Transfer metadata tags from old device to new device."""
	try:
		metadataTags = [
			'/metaData/locationDescription',
			'/metaData/install_latitude',
			'/metaData/install_longitude',
			'/metaData/image',
			'/metaData/configuration'
		]

		oldPaths = [oldTagPath + tag for tag in metadataTags]
		values = system.tag.readBlocking(oldPaths)

		newPaths = [newTagPath + tag for tag in metadataTags]
		newValues = []

		for val in values:
			if val.quality.isGood():
				newValues.append(val.value)
			else:
				newValues.append(None)

		validPaths = []
		validValues = []
		for i, v in enumerate(newValues):
			if v is not None:
				validPaths.append(newPaths[i])
				validValues.append(v)

		if validPaths:
			system.tag.writeBlocking(validPaths, validValues)

		return utils.resultParser.createResults(True, "Metadata transferred")

	except Exception as e:
		return utils.resultParser.createResults(False, "Error transferring metadata: " + str(e))


def _archiveDevice(devEUI):
	"""Archive a device by marking it as replaced."""
	try:
		result = system.sitesync.archiveDevice(devEUI)
		if result is not None:
			return json.loads(result)
		return utils.resultParser.createResults(True, "Device archived")
	except Exception as e:
		return utils.resultParser.createResults(False, "Error archiving device: " + str(e))


def _logReplacement(oldDevEUI, newDevEUI, preserveMetadata):
	"""Log the device replacement for audit purposes."""
	try:
		logMessage = "Device {0} replaced with {1}. Metadata preserved: {2}".format(
			oldDevEUI, newDevEUI, preserveMetadata
		)
		system.sitesync.logDeviceActivity(newDevEUI, "DEVICE_REPLACED", logMessage)
	except Exception as e:
		system.perspective.print("Could not log replacement: " + str(e))