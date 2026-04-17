import tests.utils.utils as t
import tests.fixtures.fixtures as fix

def run():
	results = []

	# getMqttSettings
	try:
		settings = connections.mqtt.getMqttSettings(fix.TEST_TENANT_ID)
		if settings is not None:
			results.append(t.assertIsInstance(settings, dict, "getMqttSettings returns dict"))
			# Boolean conversion check
			results.append(t.assertIsInstance(
				settings.get("useTls"), bool,
				"getMqttSettings useTls is bool"
			))
			results.append(t.assertIsInstance(
				settings.get("useAuthentication"), bool,
				"getMqttSettings useAuthentication is bool"
			))
		else:
			results.append(t.assertIsNone(settings, "getMqttSettings returns None (no MQTT configured)"))
	except Exception as e:
		results.append(t.safeTry(lambda: (_ for _ in ()).throw(e), "getMqttSettings"))

	# saveMqttSettings -- skip to avoid modifying broker config
	results.append(t.skip("saveMqttSettings", "Skipped: would modify live MQTT broker config"))

	# saveMqttTopics -- skip
	results.append(t.skip("saveMqttTopics", "Skipped: would modify live MQTT topics"))

	# getMqttTopics -- only if settings exist
	try:
		settings = connections.mqtt.getMqttSettings(fix.TEST_TENANT_ID)
		if settings and "id" in settings:
			topic = connections.mqtt.getMqttTopics(settings["id"])
			results.append(t.assertIsInstance(topic, str, "getMqttTopics returns string"))
		else:
			results.append(t.skip("getMqttTopics", "no broker configured"))
	except Exception as e:
		results.append(t.safeTry(lambda: (_ for _ in ()).throw(e), "getMqttTopics"))

	# startMQTTConnection -- skip
	results.append(t.skip("startMQTTConnection", "Skipped: would start live MQTT connection"))

	# stopMQTTConnection -- skip
	results.append(t.skip("stopMQTTConnection", "Skipped: would stop live MQTT connection"))

	return results