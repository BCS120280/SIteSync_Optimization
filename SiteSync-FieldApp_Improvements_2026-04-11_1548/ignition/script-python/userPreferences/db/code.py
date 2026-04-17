# =============================================================================
# User Preferences Database Module
# Uses Ignition Named Queries for database operations
# =============================================================================

# Preference key for column visibility
PREFERENCE_KEY_COLUMNS = "device_manager_columns"

# Default column preferences (all visible)
DEFAULT_COLUMN_PREFERENCES = {
	"status": True,
	"devEUI": True,
	"name": True,
	"deviceType": True,
	"pandID": True,
	"equipmentNumber": True,
	"deviceTypeID": True,
	"MOC": True, 
	"value":True, 
	"lastSeen":True, 
	"unit": True
}

# Column display name mapping
COLUMN_DISPLAY_NAMES = {
	"status": "Status",
	"devEUI": "devEUI",
	"name": "Name",
	"deviceType": "Sensor Type",
	"pandID": "P&ID",
	"lastSeen": "Last Seen",
	"value": "Value",
	"equipmentNumber": "Equipment #",
	"MOC": "MOC #", 
	"unit":"Unit #"
}

DEFAULT_HEALTH_METRICS = {
	"connectivityStatus": "Connected",
	"rssi": "-85 dBm",
	"snr": "10.5 dB",
	"gatewayId": "GW-Placeholder",
	"batteryVoltage": "3.6 V (95%)",
	"firmwareVersion": "v2.1.4",
	"capturedAt": None,
	"isPlaceholder": True
}


# =============================================================================
# User Preferences Functions
# =============================================================================

def getUserPreference(userId, preferenceKey):
	"""Get a user preference value."""
	try:
		result = system.db.runNamedQuery(
			"userPreferences/getUserPreference",
			{"userId": str(userId), "preferenceKey": preferenceKey}
		)
		if result.rowCount > 0:
			import json
			return json.loads(result.getValueAt(0, 0))
		return None
	except:
		return None


def setUserPreference(userId, preferenceKey, preferenceValue):
	"""Set a user preference value (insert or update)."""
	try:
		import json
		valueJson = json.dumps(preferenceValue)
		system.db.runNamedQuery(
			"userPreferences/setUserPreference",
			{
				"userId": str(userId),
				"preferenceKey": preferenceKey,
				"preferenceValue": valueJson
			}
		)
		return True
	except:
		return False


def getColumnPreferences(userId):
	"""Get column preferences for a user. Returns defaults if none saved."""
	prefs = getUserPreference(userId, PREFERENCE_KEY_COLUMNS)
	if prefs is None:
		return dict(DEFAULT_COLUMN_PREFERENCES)

	# Merge with defaults in case new columns were added
	merged = dict(DEFAULT_COLUMN_PREFERENCES)
	merged.update(prefs)
	return merged


def setColumnPreferences(userId, columnPreferences):
	"""Save column preferences for a user."""
	return setUserPreference(userId, PREFERENCE_KEY_COLUMNS, columnPreferences)


def updateSingleColumnPreference(userId, columnKey, isVisible):
	"""Update a single column's visibility preference."""
	prefs = getColumnPreferences(userId)
	prefs[columnKey] = isVisible
	if setColumnPreferences(userId, prefs):
		return prefs
	return None


def getColumnDisplayName(columnKey):
	"""Get the display name for a column key."""
	return COLUMN_DISPLAY_NAMES.get(columnKey, columnKey)


def getDefaultColumnPreferences():
	"""Get a copy of the default column preferences."""
	return dict(DEFAULT_COLUMN_PREFERENCES)


def getColumnOrder():
	"""Get the ordered list of column keys for display."""
	return ["status", "devEUI", "name", "deviceType", "description", "tagPathBase", "deviceTypeID", "tenantName"]


# =============================================================================
# Installation Records Functions
# =============================================================================

def saveInstallationRecord(devEUI, deviceConfig, checklistResults, installerUserId, installerDisplayName=None):
	"""Save an installation record for a device."""
	try:
		import json

		# Add completion timestamp
		checklistWithTimestamp = dict(checklistResults)
		checklistWithTimestamp["completedAt"] = system.date.format(system.date.now(), "yyyy-MM-dd'T'HH:mm:ss'Z'")

		deviceId = devEUI
		
		system.db.runNamedQuery(
			"userPreferences/saveInstallationRecord",
			{
				"deviceId": deviceId,
				"devEUI": devEUI,
				"installerUserId": str(installerUserId),
				"installerDisplayName": installerDisplayName or "",
				"checklistResults": json.dumps(checklistWithTimestamp),
				"configurationSnapshot": "",
				"healthMetrics": ""
			}
		)

		return {
			"success": True,
			"devEUI": devEUI,
			"message": "Installation record saved successfully"
		}
	except Exception as e:
		return {
			"success": False,
			"error": str(e),
			"message": "Failed to save installation record: " + str(e)
		}


def getInstallationRecord(devEUI):
	"""Get the installation record for a device."""
	try:
		import json
		result = system.db.runNamedQuery(
			"userPreferences/getInstallationRecord",
			{"devEUI": devEUI}
		)

		if result.rowCount > 0:
			return {
				"id": result.getValueAt(0, "id"),
				"deviceId": result.getValueAt(0, "device_id"),
				"devEUI": result.getValueAt(0, "dev_eui"),
				"installationDate": result.getValueAt(0, "installation_date"),
				"installerUserId": result.getValueAt(0, "installer_user_id"),
				"installerDisplayName": result.getValueAt(0, "installer_display_name"),
				"checklistResults": json.loads(result.getValueAt(0, "checklist_results") or "{}"),
				"configurationSnapshot": json.loads(result.getValueAt(0, "configuration_snapshot") or "{}"),
				"healthMetrics": json.loads(result.getValueAt(0, "health_metrics") or "{}"),
				"photoPath": result.getValueAt(0, "photo_path")
			}
		return None
	except:
		return None


def checkInstallationExists(devEUI):
	"""Check if an installation record exists for a device."""
	return getInstallationRecord(devEUI) is not None


def getAllInstallationRecords(limit=100, offset=0):
	"""Get all installation records with pagination."""
	try:
		result = system.db.runNamedQuery(
			"userPreferences/getAllInstallationRecords",
			{"limit": limit, "offset": offset}
		)

		records = []
		for row in range(result.rowCount):
			records.append({
				"id": result.getValueAt(row, "id"),
				"deviceId": result.getValueAt(row, "device_id"),
				"devEUI": result.getValueAt(row, "dev_eui"),
				"installationDate": result.getValueAt(row, "installation_date"),
				"installerUserId": result.getValueAt(row, "installer_user_id"),
				"installerDisplayName": result.getValueAt(row, "installer_display_name")
			})
		return records
	except:
		return []


def deleteInstallationRecord(devEUI):
	"""Delete an installation record for a device."""
	try:
		rowsAffected = system.db.runNamedQuery(
			"userPreferences/deleteInstallationRecord",
			{"devEUI": devEUI}
		)

		if rowsAffected > 0:
			return {"success": True, "message": "Installation record deleted successfully"}
		else:
			return {"success": False, "message": "No installation record found for device"}
	except Exception as e:
		return {"success": False, "error": str(e), "message": "Failed to delete: " + str(e)}
