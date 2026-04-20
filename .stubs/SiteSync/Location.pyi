from typing import Any

def _buildDevEUICache() -> Any:
    """Scan all device folders and build a devEUI -> folderName lookup."""
    ...
def _findDeviceFolder(devEUI) -> Any:
    """Find the tag folder name for a given devEUI. Returns None if not found."""
    ...
def _getDevicePath(devEUI) -> Any:
    """Get the full tag path for a device by devEUI. Returns None if not found."""
    ...
def _readSiteTempF() -> Any:
    """Read the site-wide TempF tag from the GVL root."""
    ...
def parseThingParkUplink(payload) -> Any:
    """Parse a standard Actility ThingPark uplink message.
Returns dict with devEUI, latitude, longitude, etc., or None."""
    ...
def parseTPXLocation(payload) -> Any:
    """Parse a ThingPark X Location Engine resolved location callback.
Returns dict with devEUI, latitude, longitude, etc., or None."""
    ...
def updateDeviceTags(devEUI, data) -> Any:
    """Write parsed uplink data into the EXISTING tag structure.
Looks up device folder by devEUI via metaData/devEUI scan."""
    ...
def getAllDevices() -> Any:
    """Read all tracker devices and return a list of dicts."""
    ...
def getDevice(devEUI) -> Any:
    """Read a single tracker device by DevEUI.
Returns dict or None."""
    ...
def getDeviceByName(folderName) -> Any:
    """Read a single tracker device by its tag folder name (e.g. 'Cart-72-SC-272322').
Returns dict or None."""
    ...
