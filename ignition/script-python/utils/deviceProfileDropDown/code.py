def getDeviceProfiles(profileSource):
	deviceModels = decoders.model.listDeviceProfiles(profileSource)
	mfgOptions = {}
	options = []
	for device in deviceModels:
	
		model = device["model_name"]
		if '-NA' not in model:
			modelID = device['id']
			mfg = device['manufacturer']
			options.append({"value": modelID, "label":model})
			if mfg in mfgOptions.keys():
				mfgOptions[mfg].append({"value": modelID, "label":model})
			else:
				mfgOptions[mfg] = []
				mfgOptions[mfg].append({"value": modelID, "label":model})
	
	sortedOptions = sorted(options, key=lambda p: p['label'].lower())
	mOptions = []
	for m in mfgOptions.keys():
		mOptions.append({"value": mfgOptions[m], "label":m})
	sortedMOptions = sorted(mOptions, key=lambda p: p['label'].lower())
	return sortedOptions, sortedMOptions
	
