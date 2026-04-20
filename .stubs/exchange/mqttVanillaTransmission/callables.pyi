from typing import Any

def resolvePublishParameters(tagPathFull, tagQualifiedValue, readTagProps, qos, retain, rootPathsToCut, topicPrefix, payloadFormat, timestampFormat, qualityFormat, ConfigError, DropReason) -> Any:
	"""Function that will resolve publish parameters such as topic, payload, QoS, retain
based on given tag change data and config tags 

Parameters
--------------
tagPathFull : string : Full path passed from tag change event
tagQualifiedValue : Object : Qualified Value object passed from tag change event
qos : int : Description in UDT tag's documentation
retain : bool : Description in UDT tag's documentation
rootPathsToCut : list : String array tag Cut From Tag Path, Description in its documentation
topicPrefix : string : Description in UDT tag's documentation
payloadFormat : string : Description in UDT tag's documentation
includeDataType : bool : Description in UDT tag's documentation
timestampFormat : string : Description in UDT tag's documentation
qualityFormat : string : Description in UDT tag's documentation

Returns
--------------
Topic : string : 
Payload : string : 
Qos : int : 
Retain : int : Cirrus Link publish methods expects integer"""
	...
def publish(module, server, topic, payload, qos, retain, checkServerValidity) -> Any:
	"""Function that will publish MQTT messages, using one of Cirrus Link modules (based on parameter module)

Parameters
--------------
module : string : Which module to use to publish message
server : string : Valid server connection name configured in Ignition Gateway under relevant module 
topic : string : 
payload : string : 
qos : int : Enum:[0,1,2]
retain : int : Enum:[0,1]

Returns
--------------
None"""
	...
def writeStatistics(udtInstancePath, count, errorMessage, dropMessage) -> Any:
	"""Function that will write result of previous operations to statistics tags of UDT instance

Parameters
--------------
udtInstancePath : string : Full path to instance of MQTT Vanilla Transmission UDT
count : int : default = 1
errorMessage : string : default = ""
dropMessage : string : default = ""

Returns
--------------
None"""
	...
def tagChangeEvent(initialChange, event, udtInstancePath) -> Any:
	"""Trigger function that should be called from Gateway Tag Change event.


Parameters
--------------
initialValue : Bool : Event parameter, that indicates first change (new tag, after restart,...)
event : Object : Event parameter, that holds all required tag data (path, value, quality, timestamp,...)
udtInstancePath : String : User input parameter, that indicates path to instance of UDT (MQTT Vanilla Transmission)

Returns
--------------
None"""
	...
