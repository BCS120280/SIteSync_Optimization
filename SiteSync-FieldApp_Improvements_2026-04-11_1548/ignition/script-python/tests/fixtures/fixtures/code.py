# Test tenant and reserved EUI namespace for I/O tests.
# Configure TEST_TENANT_ID to match your dedicated test tenant before running I/O suites.
TEST_TENANT_ID = 1

# Reserved devEUI namespace -- never collides with real devices
TEST_DEVEUI_PREFIX = "ffff000000000"
TEST_DEVEUI_01 = "ffff000000000001"
TEST_DEVEUI_02 = "ffff000000000002"
TEST_DEVEUI_03 = "ffff000000000003"
TEST_DEVEUI_04 = "ffff000000000004"
TEST_DEVEUI_05 = "ffff000000000005"

# Valid keys for device creation
VALID_APP_KEY = "00112233445566778899aabbccddeeff"
VALID_JOIN_EUI = "0000000000000000"

# Tag provider for test devices
TEST_TAG_PROVIDER = "default"
TEST_TAG_PATH = "TestDevices"

# Placeholder model ID -- set to a real device profile ID in your system
TEST_MODEL_ID = 1

# Default app ID
TEST_APP_ID = 2

# Sample metadata
SAMPLE_META = {"custom_field": "test_value", "install_notes": "automated test"}

# Sample image (1x1 white PNG, base64)
SAMPLE_IMAGE_B64 = (
	"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR4"
	"nGP4z8BQDwAEgAF/pooBPQAAAABJRU5ErkJggg=="
)

# QR code test data
QR_SITESYNC = "00112233445566778899aabbccddeeff:FFFF000000000001:A107"
QR_SITESYNC_WITH_APPEUI = "00112233445566778899aabbccddeeff:FFFF000000000001:A107:1234567890abcdef"
QR_LORA = "L0:D0:1234567890abcdef:FFFF000000000001"
QR_VEGA = "L0:D0:1234567890abcdef:FFFF000000000001:extra1:extra2:00112233445566778899aabbccddeeff"
QR_EUI_ONLY = "FFFF000000000001"
QR_SHORT = "abc"

# Sample device profile list (mimics dropdown options)
SAMPLE_PROFILE_LIST = [
	{"label": "TEPressure", "value": 1},
	{"label": "SushiVibration", "value": 2},
	{"label": "RadioBridge4-20ma", "value": 3},
]

# Sample model list (mimics decoders.model.listDeviceProfiles result)
SAMPLE_MODEL_LIST = [
	{"id": 1, "model_name": "TEPressure", "device_type": "PRESSURE", "manufacturer": "TESolution"},
	{"id": 2, "model_name": "SushiVibration", "device_type": "VIBRATION", "manufacturer": "Sushi"},
	{"id": 3, "model_name": "RadioBridge4-20ma", "device_type": "420MA", "manufacturer": "RadioBridge"},
]

# Bulk upload sample rows
SAMPLE_UPLOAD_ROW = {
	"dev_eui": "FFFF000000000001",
	"join_eui": "0000000000000000",
	"app_key": "00112233445566778899AABBCCDDEEFF",
	"name": "TestDevice0001",
	"description": "bulk upload test",
	"deviceType": "",
	"firmware_version": "1.0",
	"hardware_version": "2.0",
	"location": "Building A",
	"serial_number": "SN001",
	"custom_col": "custom_val",
}

SAMPLE_UPLOAD_ROW_NAMED_TYPE = {
	"dev_eui": "FFFF000000000002",
	"join_eui": "0000000000000000",
	"app_key": "00112233445566778899AABBCCDDEEFF",
	"name": "",
	"description": "",
	"deviceType": "TEPressure",
	"firmware_version": "",
	"hardware_version": "",
	"location": "",
}

SAMPLE_UPLOAD_ROW_BAD_EUI = {
	"dev_eui": "ABC",
	"join_eui": "short",
	"app_key": "tooshort",
	"name": "",
	"description": "",
	"deviceType": "",
}