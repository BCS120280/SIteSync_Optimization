import json
import utils.resultParser
import decoders.downlinks

def getEncoder(encoderId):
	try:
		if encoderId is None or encoderId == 0:
			return None
		encoder = system.sitesync.getEncoder(encoderId)
		if encoder is not None:
			return json.loads(encoder)
		return None
	except Exception as e:
		system.perspective.print('Error loading encoder: ' + str(e))
		return None

def getEncoderQuestions(encoderId):
	encoder = getEncoder(encoderId)
	if encoder is None:
		return []
	try:
		questionsStr = encoder.get('questions', None)
		if questionsStr is None or questionsStr == '':
			return []
		parsed = json.loads(questionsStr)
		if isinstance(parsed, dict) and 'questions' in parsed:
			return parsed['questions']
		elif isinstance(parsed, list):
			return parsed
		return []
	except Exception as e:
		system.perspective.print('Error parsing encoder questions: ' + str(e))
		return []

def unflattenAnswers(flatAnswers):
	nested = {}
	for key, val in flatAnswers.items():
		cleanKey = key
		if cleanKey.startswith('input.'):
			cleanKey = cleanKey[6:]
		parts = cleanKey.split('.')
		current = nested
		for i in range(len(parts) - 1):
			part = parts[i]
			if part not in current:
				current[part] = {}
			current = current[part]
		current[parts[-1]] = val
	return nested

def encodeAndSave(answers, encoderId, tenantId, deviceProfileId, name, description):
	try:
		nestedConfig = unflattenAnswers(answers)
		configJson = json.dumps(nestedConfig)
		encodeResult = system.sitesync.encodeDownlink(configJson, encoderId, tenantId)
		if encodeResult is None:
			return utils.resultParser.createResults(False, 'No response from encoder')
		parsed = json.loads(encodeResult)
		if not utils.resultParser.isResultSuccess(parsed):
			return parsed
		hexPayload = utils.resultParser.getResultMessage(parsed)
		if hexPayload is None or hexPayload == '':
			return utils.resultParser.createResults(False, 'Encoder returned empty payload')
		saveResult = decoders.downlinks.saveDownlink(0, deviceProfileId, hexPayload, 0, description, name)
		if not utils.resultParser.isResultSuccess(saveResult):
			return utils.resultParser.createResults(False, 'Encoded successfully but failed to save: ' + utils.resultParser.getResultMessage(saveResult))
		return utils.resultParser.createResults(True, hexPayload)
	except Exception as e:
		system.perspective.print('Error in encodeAndSave: ' + str(e))
		return utils.resultParser.createResults(False, str(e))