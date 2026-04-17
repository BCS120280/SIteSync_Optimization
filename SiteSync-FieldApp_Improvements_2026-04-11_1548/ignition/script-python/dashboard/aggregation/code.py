def getFleetHealth(tenantID):
	"""Aggregate fleet-wide KPI metrics for dashboard summary cards."""
	import json
	devices = system.sitesync.listDevices(tenantID)
	deviceList = json.loads(devices)

	totalDevices = len(deviceList)
	online = 0
	lowBattery = 0

	checkinPaths = []
	batteryPaths = []
	for d in deviceList:
		path = d['fullTagPath']
		checkinPaths.append(path + "/LoRaMetrics/checkin_overdue")
		batteryPaths.append(path + "/displayValues/Battery")

	if totalDevices > 0:
		checkinValues = system.tag.readBlocking(checkinPaths)
		batteryValues = system.tag.readBlocking(batteryPaths)

		for i in range(totalDevices):
			cv = checkinValues[i]
			if cv.quality.isGood() and cv.value != True:
				online += 1

			bv = batteryValues[i]
			if bv.quality.isGood() and bv.value is not None:
				try:
					if float(bv.value) < 20:
						lowBattery += 1
				except:
					pass

	alarmCount = 0
	try:
		alarmResults = system.alarm.queryStatus()
		alarmCount = alarmResults.getDataset().rowCount
	except:
		pass

	return {
		'totalDevices': totalDevices,
		'online': online,
		'alarms': alarmCount,
		'lowBattery': lowBattery
	}