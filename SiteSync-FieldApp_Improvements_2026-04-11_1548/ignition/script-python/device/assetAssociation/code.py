import json

def linkToAsset(devEUI, assetID):
	"""
	Link a device to an existing asset.

	Args:
		devEUI: The device EUI to associate
		assetID: The ID of the asset to link to

	Returns:
		Standard result object with messageType and message
	"""
	try:
		if not devEUI or len(devEUI) != 16:
			return utils.resultParser.createResults(False, "Invalid device EUI")

		if assetID is None or assetID < 0:
			return utils.resultParser.createResults(False, "Invalid asset ID")

		deviceData = device.get.getDevice(devEUI)
		if deviceData is None or 'status' in deviceData and deviceData['status'] == 'ERROR':
			return utils.resultParser.createResults(False, "Device not found")

		assetData = _getAsset(assetID)
		if assetData is None:
			return utils.resultParser.createResults(False, "Asset not found")

		result = system.sitesync.linkDeviceToAsset(devEUI, assetID)
		if result is not None:
			parsedResult = json.loads(result)
			if utils.resultParser.isResultSuccess(parsedResult):
				tagPath = deviceData.get('fullTagPath', '')
				if tagPath:
					_updateAssetTag(tagPath, assetID, assetData.get('name', ''))

				_logAssociation(devEUI, assetID, assetData.get('name', ''))

			return parsedResult

		return utils.resultParser.createResults(True, "Device linked to asset")

	except Exception as e:
		system.perspective.print("Error linking device to asset: " + str(e))
		return utils.resultParser.createResults(False, "Error linking device to asset: " + str(e))


def unlinkFromAsset(devEUI):
	"""
	Unlink a device from its current asset association.

	Args:
		devEUI: The device EUI to unlink

	Returns:
		Standard result object with messageType and message
	"""
	try:
		if not devEUI or len(devEUI) != 16:
			return utils.resultParser.createResults(False, "Invalid device EUI")

		deviceData = device.get.getDevice(devEUI)
		if deviceData is None:
			return utils.resultParser.createResults(False, "Device not found")

		result = system.sitesync.unlinkDeviceFromAsset(devEUI)
		if result is not None:
			parsedResult = json.loads(result)
			if utils.resultParser.isResultSuccess(parsedResult):
				tagPath = deviceData.get('fullTagPath', '')
				if tagPath:
					_clearAssetTag(tagPath)

			return parsedResult

		return utils.resultParser.createResults(True, "Device unlinked from asset")

	except Exception as e:
		system.perspective.print("Error unlinking device from asset: " + str(e))
		return utils.resultParser.createResults(False, "Error unlinking device from asset: " + str(e))


def getDeviceAsset(devEUI):
	"""
	Get the asset associated with a device.

	Args:
		devEUI: The device EUI to look up

	Returns:
		Asset data dictionary or None if not associated
	"""
	try:
		if not devEUI:
			return None

		result = system.sitesync.getDeviceAsset(devEUI)
		if result is not None:
			return json.loads(result)

		return None

	except Exception as e:
		system.perspective.print("Error getting device asset: " + str(e))
		return None


def listAssetDevices(assetID):
	"""
	List all devices associated with an asset.

	Args:
		assetID: The ID of the asset

	Returns:
		List of device data dictionaries
	"""
	try:
		if assetID is None or assetID < 0:
			return []

		result = system.sitesync.listAssetDevices(assetID)
		if result is not None:
			return json.loads(result)

		return []

	except Exception as e:
		system.perspective.print("Error listing asset devices: " + str(e))
		return []


def _getAsset(assetID):
	"""Get asset data by ID."""
	try:
		result = system.sitesync.getAsset(assetID)
		if result is not None:
			return json.loads(result)
		return None
	except Exception as e:
		system.perspective.print("Error getting asset: " + str(e))
		return None


def _updateAssetTag(tagPath, assetID, assetName):
	"""Update the device tag with asset association info."""
	try:
		paths = [
			tagPath + '/metaData/assetID',
			tagPath + '/metaData/assetName'
		]
		values = [assetID, assetName]
		system.tag.writeBlocking(paths, values)
	except Exception as e:
		system.perspective.print("Error updating asset tag: " + str(e))


def _clearAssetTag(tagPath):
	"""Clear the asset association from device tag."""
	try:
		paths = [
			tagPath + '/metaData/assetID',
			tagPath + '/metaData/assetName'
		]
		values = [None, '']
		system.tag.writeBlocking(paths, values)
	except Exception as e:
		system.perspective.print("Error clearing asset tag: " + str(e))


def _logAssociation(devEUI, assetID, assetName):
	"""Log the asset association for audit purposes."""
	try:
		logMessage = "Device associated with asset: {0} (ID: {1})".format(assetName, assetID)
		system.sitesync.logDeviceActivity(devEUI, "ASSET_LINKED", logMessage)
	except Exception as e:
		system.perspective.print("Could not log association: " + str(e))