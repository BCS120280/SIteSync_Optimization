# Code Review — SiteSync EnterpriseManagementScripts `MPC/customizations/`

**Platform:** Ignition 8.1.50 · Jython 2.7 (Python 2.7 on JVM) · Azul OpenJDK 17.0.16  
**Scope:** 4 files under `script-python/MPC/customizations/`  
**Files reviewed:**
- `MPC/customizations/PIIntegration/code.py` (71 lines)
- `MPC/customizations/actility/code.py` (85 lines)
- `MPC/customizations/device/createDevice/code.py` (152 lines)
- `MPC/customizations/models/modelPicker/code.py` (22 lines)

---

## A.1 `MPC/customizations/` *(all four files)*

**[CRITICAL] Entire MPC.customizations layer is unreachable — no external caller exists anywhere in the project**

**File:** All four files under `SiteSYnc EnterpriseManagementScripts/script-python/MPC/customizations/`

**Impact.** Every function in all four modules is dead code at runtime. The only reference to `MPC.customizations` in the entire Enterprise project — across every `.py`, `.json`, and all other file types — is `MPC/customizations/device/createDevice/code.py:23`, which is *inside* the MPC layer itself. No Perspective view, no gateway event, and no other script module calls into `MPC.customizations.*`. All callers of the device-creation flow use `device.createDevice.saveDevice` (the non-MPC version), bypassing every improvement and fix that MPC engineers added here. The features that depend on this layer — modelID-aware PI instance creation, Actility extra-connection provisioning, device-domain assignment — are silently skipped on every device onboard.

**Explanation.** A full corpus grep confirms the call map:

| Module | External callers found |
|---|---|
| `MPC.customizations.device.createDevice.saveDevice` | **0** — all callers reference `device.createDevice.saveDevice` |
| `MPC.customizations.PIIntegration.createInstance` | **0** external — only called from the orphaned `saveDevice` above |
| `MPC.customizations.actility.*` (all 6 functions) | **0** |
| `MPC.customizations.models.modelPicker.*` | **0** |

The non-MPC `device/createDevice/code.py:saveDevice` calls `createPITemplate.createInstance(fullTagPath, name)` (the two-argument legacy version with no `modelID`, no retry, and no structured error propagation). The MPC three-argument version with retry logic and proper error surfacing is never reached.

**Recommended Fix.** Wire Perspective view button scripts and bulk-upload callers to `MPC.customizations.device.createDevice.saveDevice` instead of `device.createDevice.saveDevice`. Specifically:
- `device/bulkuploadV2/code.py:229` calls `device.createDevice.saveDevice(...)` — redirect to `MPC.customizations.device.createDevice.saveDevice(...)`
- Any Perspective component `onActionPerformed` scripts that invoke `device.createDevice.saveDevice` must be updated to the MPC path.

---

## A.2 `MPC/customizations/actility/code.py`

**[CRITICAL] `setProfile()` ignores both parameters — hardcodes model ID `1` and connection ID `2`** — `code.py:46–50`

**File:** `SiteSYnc EnterpriseManagementScripts/script-python/MPC/customizations/actility/code.py`, lines 46–50

**Impact.** `setProfile(profileID, connectionStrings)` is called by `addDeviceToExtraActilityConnections` with the device's actual profile ID and the computed Actility connection string (e.g., `"TWA_100000163.991.AS"`). But the function ignores both. It fetches device-profile record #1 regardless of which device is being onboarded, injects the hardcoded integer `2` as the connection ID instead of the real Actility TWA string, and saves this corrupted record back. If this code were ever reached, it would overwrite the global profile #1 with a wrong connection ID on every single device onboard — a destructive write affecting every device that shares that profile.

**Explanation.** The parameters `profileID` and `connectionStrings` are accepted but never referenced inside the function body. Both values are replaced by literals.

**Source.** Current code (defective):
```python
46  def setProfile(profileID, connectionStrings):
47      profile = decoders.model.getModel(1)          # ignores profileID
48      profile['profileConnectionId'] = 2            # ignores connectionStrings
49      res = decoders.model.updateModel(profile)
50      return res
```

**Recommended Fix.**
```python
46  def setProfile(profileID, connectionStrings):
47      profile = decoders.model.getModel(profileID)
48      profile['profileConnectionId'] = connectionStrings
49      res = decoders.model.updateModel(profile)
50      return res
```

---

## A.3 `MPC/customizations/PIIntegration/code.py`

**[HIGH] `time.sleep(5)` blocks the gateway thread for up to 15 seconds — comment claims 500 ms** — `code.py:11`

**File:** `SiteSYnc EnterpriseManagementScripts/script-python/MPC/customizations/PIIntegration/code.py`, lines 6–11

**Impact.** `createInstance` is called synchronously from `saveDevice`, which is triggered from a Perspective button or bulk-upload gateway script. The retry loop runs up to 3 times with a 5-second sleep between attempts. If the template tag never propagates (device profile misconfigured, UDT not yet synced), the calling thread blocks for 10 seconds minimum before the third read attempt, then fails. In a Perspective button handler this freezes the UI session. In a gateway script it holds a gateway execution thread. The inline comment `# Retry up to 3 times with 500ms delay` is wrong by a factor of 10 — `time.sleep(5)` is 5 000 ms, not 500 ms.

**Source.** Current code (defective):
```python
 4      # Retry up to 3 times with 500ms delay to handle UDT propagation lag after createTag
 5      tagRead = None
 6      for attempt in range(3):
 7          tagRead = system.tag.readBlocking([...])[0]
 8          if "Good" in str(tagRead.quality) and tagRead.value:
 9              break
10          if attempt < 2:
11              time.sleep(5)    # 5 000 ms, not 500 ms
```

**Recommended Fix.**
```python
10          if attempt < 2:
11              time.sleep(0.5)  # 500 ms as documented
```

---

## A.4 `MPC/customizations/PIIntegration/code.py`

**[HIGH] Greedy `.replace(tagName, "")` corrupts `assembledPath` when the tag name appears in a parent folder** — `code.py:22`

**File:** `SiteSYnc EnterpriseManagementScripts/script-python/MPC/customizations/PIIntegration/code.py`, line 22

**Impact.** For any device whose name matches a segment of its own folder path — e.g., device `Pump` inside folder `SPP/Pump/` giving `tagPath = "[default]SPP/Pump/Pump"` — `str.replace` strips every occurrence of the name, yielding `assembledPath = "SPP//"`. The resulting `baseTagPath` contains a double-slash and `addTagToPi` receives a malformed path. `system.tag.configure` either fails silently or creates the UDT at an unintended location.

**Explanation.** `str.replace(old, new)` replaces all non-overlapping occurrences globally. The intent is to remove only the terminal segment (the device name). The fix is a positional strip.

**Source.** Current code (defective):
```python
22      assembledPath = tagPath.replace('[default]', '').replace(tagName, "")
```

**Recommended Fix.**
```python
22      stripped = tagPath.replace('[default]', '').strip('/')
23      assembledPath = '/'.join(stripped.split('/')[:-1]) + '/'
```

---

## A.5 `MPC/customizations/PIIntegration/code.py`

**[HIGH] `addTagToPi` always returns success — PI adapter and AF failures are silently swallowed** — `code.py:68`

**File:** `SiteSYnc EnterpriseManagementScripts/script-python/MPC/customizations/PIIntegration/code.py`, lines 60–70

**Impact.** `createInstance` calls `addTagToPi`, checks whether it succeeded with `isResultSuccess`, and propagates the result back to `saveDevice`. Because `addTagToPi` unconditionally returns `createResults(True, ...)` on line 68, `isResultSuccess` always returns `True` even when `PIIntegration.adapter.addToDataSelection` or `PIIntegration.AF.createPITag` returned an error object. The `saveDevice` caller receives a success response; the device is reported as fully onboarded; the PI historian tag was never actually created.

**Source.** Current code (defective):
```python
65      adapterResults = PIIntegration.adapter.addToDataSelection(tagPathArray)
66      results = PIIntegration.AF.createPITag(tagPath)
67      logger.info("Adapter add result: " + str(adapterResults) + " PI tag creation results: " + str(results))
68      return utils.resultParser.createResults(True, "Adapter add result: ..." )   # always True
```

**Recommended Fix.**
```python
65      adapterResults = PIIntegration.adapter.addToDataSelection(tagPathArray)
66      if not utils.resultParser.isResultSuccess(adapterResults):
67          return adapterResults
68      results = PIIntegration.AF.createPITag(tagPath)
69      if not utils.resultParser.isResultSuccess(results):
70          return results
71      logger.info("PI tag created: " + tagPath)
72      return utils.resultParser.createResults(True, "Adapter: " + str(adapterResults) + " AF: " + str(results))
```

---

## A.6 `MPC/customizations/device/createDevice/code.py`

**[HIGH] `saveTagPathForDevice`: unguarded `json.loads(results)` raises `TypeError` when API returns `None`** — `code.py:149`

**File:** `SiteSYnc EnterpriseManagementScripts/script-python/MPC/customizations/device/createDevice/code.py`, line 149

**Impact.** `system.sitesync.createTag(t)` can return `None` on network timeout or backend error. `json.loads(None)` raises `TypeError: the JSON object must be str, not 'NoneType'`. This exception propagates uncaught through `saveDevice`, silently aborting the onboard after the device was already registered in the backend — leaving the system in a half-provisioned state (device record exists, no tag path record).

**Source.** Current code (defective):
```python
147      results = system.sitesync.createTag(t)
148      system.perspective.print(type(results))
149      result = json.loads(results)
```

**Recommended Fix.**
```python
147      results = system.sitesync.createTag(t)
148      if results is None:
149          return utils.resultParser.createResults(False, "No response from createTag")
150      result = json.loads(results)
```

---

## A.7 `MPC/customizations/actility/code.py`

**[HIGH] `addToDomain`: unguarded `json.loads(results)` raises `TypeError` when API returns `None`** — `code.py:80`

**File:** `SiteSYnc EnterpriseManagementScripts/script-python/MPC/customizations/actility/code.py`, line 80

**Impact.** `system.sitesync.associateDeviceWithDomain` can return `None`. `json.loads(None)` raises `TypeError`. The exception propagates uncaught; the caller receives no structured error result, only an unhandled exception in the gateway log.

**Source.** Current code (defective):
```python
79      results = system.sitesync.associateDeviceWithDomain(devEUI, siteName, mainNWSID, group)
80      return json.loads(results)
```

**Recommended Fix.**
```python
79      results = system.sitesync.associateDeviceWithDomain(devEUI, siteName, mainNWSID, group)
80      if not results:
81          return utils.resultParser.createResults(False, "No response from associateDeviceWithDomain")
82      return json.loads(results)
```

---

## A.8 `MPC/customizations/actility/code.py`

**[HIGH] `enterprise.tenant.getDefaultApp()` is hardcoded to return `3` — dynamic lookup is commented out** — `enterprise/tenant/code.py:3`

**File:** `SiteSYnc EnterpriseManagementScripts/script-python/enterprise/tenant/code.py`, lines 2–8

**Impact.** Every call in the MPC actility module that obtains the network-server ID — `applyConnectionID` (line 67) and `addToDomain` (line 78) — receives the hardcoded integer `3`. In a multi-tenant or reconfigured deployment where the primary network-server account has a different ID, all Actility provisioning calls would target the wrong NWS account. This would silently associate every device with the wrong Actility account, causing devices to receive no downlinks or wrong join parameters.

**Source.** Current code (defective):
```python
# enterprise/tenant/code.py
2  def getDefaultApp():
3      return 3
4  #   j = system.sitesync.getPrimaryNetworkServerAccount()
5  #   if j != "null":
6  #       app = json.loads(j)
7  #       return app['id']
8  #   else:
9  #       return -16
```

**Recommended Fix.** Restore the dynamic lookup:
```python
2  def getDefaultApp():
3      j = system.sitesync.getPrimaryNetworkServerAccount()
4      if j and j != "null":
5          return json.loads(j)['id']
6      return -1
```

---

## A.9 `MPC/customizations/actility/code.py`

**[MEDIUM] `addToDomain`: `siteID` parameter is silently ignored** — `code.py:77–80`

**File:** `SiteSYnc EnterpriseManagementScripts/script-python/MPC/customizations/actility/code.py`, lines 77–80

**Impact.** The function signature declares `siteID` as a required parameter, so callers must pass a value for it. But the function body never references `siteID` — only `siteName` is passed to `associateDeviceWithDomain`. Any caller that looks at the signature and assumes `siteID` drives a lookup (e.g., an internal numeric ID resolved to a domain name) will silently pass a value that is discarded.

**Source.** Current code (defective):
```python
77  def addToDomain(devEUI, siteID, siteName, group = "Refining"):
78      mainNWSID = enterprise.tenant.getDefaultApp()
79      results = system.sitesync.associateDeviceWithDomain(devEUI, siteName, mainNWSID, group)
80      return json.loads(results)
```

**Recommended Fix.** Either use `siteID` to look up the domain name, or remove it from the signature if `siteName` is always the right value:
```python
77  def addToDomain(devEUI, siteName, group="Refining"):
```

---

## A.10 `MPC/customizations/actility/code.py`

**[MEDIUM] `setTags` and `getIsJoined` are silent stubs with no exception or deprecation marker** — `code.py:43–44, 83–85`

**File:** `SiteSYnc EnterpriseManagementScripts/script-python/MPC/customizations/actility/code.py`, lines 43–44, 83–85

**Impact.** Both functions return a `createResults(False, "Coming soon")` payload. Any caller that checks `isResultSuccess` will see a failure and may silently skip provisioning steps without any exception, log entry, or user-visible error explaining why. The stub functions look complete from the outside — they have proper signatures and return structured results — so callers will not know they hit unimplemented code.

**Source.** Current code (defective):
```python
43  def setTags(devEUI, tagArray):
44      return utils.resultParser.createResults(False, "Coming soon")

83  def getIsJoined(devEUI):
84      ##checks if device has joined in actility
85      return utils.resultParser.createResults(False, "Coming soon")
```

**Recommended Fix.** Raise `NotImplementedError` so callers fail loudly, or log a warning so the stub is visible in the gateway log:
```python
43  def setTags(devEUI, tagArray):
44      raise NotImplementedError("setTags not yet implemented")
```

---

## A.11 `MPC/customizations/device/createDevice/code.py`

**[MEDIUM] Pervasive `system.perspective.print` debug calls throughout the device-creation flow** — `code.py:6,9,13,17,74,119,146,148`

**File:** `SiteSYnc EnterpriseManagementScripts/script-python/MPC/customizations/device/createDevice/code.py`, lines 6, 9, 13, 17, 74, 119, 146, 148

**Impact.** Eight `system.perspective.print` calls remain across `saveDevice`, `validateDevice`, `createDevice`, and `saveTagPathForDevice`. Called from any non-Perspective context (gateway event, bulk-upload script) these raise `AttributeError`, aborting the function mid-execution. In a Perspective session they leak the full device JSON — including `devEUI`, `applicationKey`, and `joinEUI` — to the browser developer console, creating a credential-exposure risk.

**Source.** Examples (defective):
```python
 6      system.perspective.print(deviceJSON)       # leaks appKey, devEUI, joinEUI
 9      system.perspective.print("pre-create device")
74      system.perspective.print(device)           # leaks full device dict in validateDevice
```

**Recommended Fix.** Remove all eight calls. Route any necessary diagnostic output through a gateway logger:
```python
logger = system.util.getLogger("SiteSync-DeviceOnboarding")
logger.debug("Creating device: devEUI={0}, model={1}".format(devEUI, modelID))
```

---

## A.12 `MPC/customizations/models/modelPicker/code.py`

**[MEDIUM] `filterLimitedModels`: `.split("_types_/SiteSyncModels/")[1]` raises `IndexError` if path structure changes** — `code.py:19`

**File:** `SiteSYnc EnterpriseManagementScripts/script-python/MPC/customizations/models/modelPicker/code.py`, line 19

**Impact.** If any tag returned by `system.tag.browse` has a `fullPath` that does not contain the literal string `_types_/SiteSyncModels/` — for example after a provider rename, a path refactor, or an unexpected UDT type location — `split(...)` returns a one-element list and `[1]` raises `IndexError`, crashing the model-picker dropdown for the entire device-onboarding form.

**Source.** Current code (defective):
```python
19          modelPath = str(r['fullPath']).split("_types_/SiteSyncModels/")[1]
```

**Recommended Fix.**
```python
19          parts = str(r['fullPath']).split("_types_/SiteSyncModels/")
20          if len(parts) < 2:
21              continue
22          modelPath = parts[1]
```

---

## A.13 `MPC/customizations/PIIntegration/code.py`

**[MEDIUM] `"Good" in str(createResult)` is a fragile string-match quality check** — `code.py:51`

**File:** `SiteSYnc EnterpriseManagementScripts/script-python/MPC/customizations/PIIntegration/code.py`, line 51

**Impact.** `system.tag.configure` returns a `List<QualityCode>`. Converting the list to a string and searching for the substring `"Good"` would produce a false positive if an error message ever contained the word "Good" (e.g., `"Not Good — tag already exists"`). It also produces a false negative if the quality representation ever changes format. The safe check is to inspect the quality code directly.

**Source.** Current code (defective):
```python
51      if "Good" in str(createResult):
```

**Recommended Fix.**
```python
51      if createResult and createResult[0].isGood():
```

---

## A.14 `MPC/customizations/actility/code.py`

**[LOW] `addToDomain` default group `"Refining"` is a customer-specific literal** — `code.py:77`

**File:** `SiteSYnc EnterpriseManagementScripts/script-python/MPC/customizations/actility/code.py`, line 77

**Impact.** The default value `"Refining"` is a business-domain group name specific to MPC's deployment. If this code is ever reused by another SiteSync customer or if MPC renames its Actility domain group, every call that relies on the default silently associates devices with a non-existent or wrong group. Actility returns no error for an unknown group name in some API versions — devices just fail to receive profiles.

**Source.** Current code (defective):
```python
77  def addToDomain(devEUI, siteID, siteName, group = "Refining"):
```

**Recommended Fix.** Read the group name from a configuration tag or named query rather than embedding it in the function default:
```python
77  def addToDomain(devEUI, siteName, group):
    # caller must supply group; read from config: system.tag.readBlocking(["[default]Config/ActilityGroup"])[0].value
```

---

## Summary

| ID | File | Severity | Title |
|----|------|----------|-------|
| A.1 | All 4 files | **CRITICAL** | Entire MPC.customizations layer unreachable — zero external callers |
| A.2 | `actility/code.py` | **CRITICAL** | `setProfile()` ignores both params; hardcodes model `1` and connection ID `2` |
| A.3 | `PIIntegration/code.py` | HIGH | `time.sleep(5)` blocks thread 15 s; comment says 500 ms |
| A.4 | `PIIntegration/code.py` | HIGH | Greedy `.replace(tagName,"")` corrupts path on name collision |
| A.5 | `PIIntegration/code.py` | HIGH | `addTagToPi` always returns success — PI errors swallowed |
| A.6 | `device/createDevice/code.py` | HIGH | Unguarded `json.loads` in `saveTagPathForDevice` — None raises TypeError |
| A.7 | `actility/code.py` | HIGH | Unguarded `json.loads` in `addToDomain` — None raises TypeError |
| A.8 | `enterprise/tenant/code.py` | HIGH | `getDefaultApp()` hardcoded to `3` — dynamic lookup commented out |
| A.9 | `actility/code.py` | MEDIUM | `addToDomain` silently ignores `siteID` parameter |
| A.10 | `actility/code.py` | MEDIUM | `setTags` / `getIsJoined` are silent stubs returning "Coming soon" |
| A.11 | `device/createDevice/code.py` | MEDIUM | 8× `system.perspective.print` debug calls leak credentials, break non-Perspective contexts |
| A.12 | `models/modelPicker/code.py` | MEDIUM | `split(...)[1]` raises `IndexError` if path structure changes |
| A.13 | `PIIntegration/code.py` | MEDIUM | `"Good" in str(createResult)` fragile string-match quality check |
| A.14 | `actility/code.py` | LOW | Hardcoded default group `"Refining"` is customer-specific |
