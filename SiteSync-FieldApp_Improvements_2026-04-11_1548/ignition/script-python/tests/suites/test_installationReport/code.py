import tests.utils.utils as t

def run():
	results = []

	# _checkIcon -- truthy
	html = reports.installationReport._checkIcon(True)
	results.append(t.assertContains(html, "10004", "_checkIcon(True) has checkmark entity"))
	results.append(t.assertContains(html, "#006B3E", "_checkIcon(True) has green color"))
	results.append(t.assertContains(html, "Confirmed", "_checkIcon(True) says Confirmed"))

	# _checkIcon -- falsy
	html = reports.installationReport._checkIcon(False)
	results.append(t.assertContains(html, "10008", "_checkIcon(False) has cross entity"))
	results.append(t.assertContains(html, "#ED2938", "_checkIcon(False) has red color"))
	results.append(t.assertContains(html, "Not Confirmed", "_checkIcon(False) says Not Confirmed"))

	# _checkIcon -- None (falsy)
	html = reports.installationReport._checkIcon(None)
	results.append(t.assertContains(html, "Not Confirmed", "_checkIcon(None) is Not Confirmed"))

	# _formatCoordinates -- valid
	coords = {"latitude": 29.7604, "longitude": -95.3698}
	result = reports.installationReport._formatCoordinates(coords)
	results.append(t.assertContains(result, "29.7604", "_formatCoordinates has latitude"))
	results.append(t.assertContains(result, "95.3698", "_formatCoordinates has longitude"))
	results.append(t.assertContains(result, "N", "_formatCoordinates positive lat is N"))
	results.append(t.assertContains(result, "W", "_formatCoordinates negative lon is W"))

	# _formatCoordinates -- southern/eastern hemisphere
	coords2 = {"latitude": -33.8688, "longitude": 151.2093}
	result2 = reports.installationReport._formatCoordinates(coords2)
	results.append(t.assertContains(result2, "S", "_formatCoordinates negative lat is S"))
	results.append(t.assertContains(result2, "E", "_formatCoordinates positive lon is E"))

	# _formatCoordinates -- None
	results.append(t.assertEqual(
		reports.installationReport._formatCoordinates(None),
		"N/A",
		"_formatCoordinates(None) -> N/A"
	))

	# _formatCoordinates -- missing keys
	results.append(t.assertEqual(
		reports.installationReport._formatCoordinates({"latitude": 1.0}),
		"N/A",
		"_formatCoordinates missing longitude -> N/A"
	))

	# _buildReportHTML -- produces valid HTML structure
	html = reports.installationReport._buildReportHTML(
		deviceName="TestDev",
		devEUI="ffff000000000001",
		installDate="2026-01-15",
		installerName="admin",
		config={"manufacturer": "Acme", "sensorType": "TEMPERATURE"},
		checklist={"sensorMounted": True, "powerConfirmed": False},
		health={"connectivityStatus": "Connected", "rssi": "-85 dBm"}
	)
	results.append(t.assertContains(html, "TestDev", "_buildReportHTML contains device name"))
	results.append(t.assertContains(html, "ffff000000000001", "_buildReportHTML contains devEUI"))
	results.append(t.assertContains(html, "2026-01-15", "_buildReportHTML contains install date"))
	results.append(t.assertContains(html, "Acme", "_buildReportHTML contains manufacturer"))
	results.append(t.assertContains(html, "TEMPERATURE", "_buildReportHTML contains sensor type"))
	results.append(t.assertContains(html, "Connected", "_buildReportHTML contains health status"))
	results.append(t.assertContains(html, "<!DOCTYPE html>", "_buildReportHTML is valid HTML"))

	return results