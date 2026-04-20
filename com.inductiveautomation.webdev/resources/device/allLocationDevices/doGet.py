def doGet(request, session):
	try:
		results = LocationAPI.getLocationData()
		return {"json": results}
	except Exception as e:
		 return {"json": {"status":"ERROR", "message":str(e)}}		