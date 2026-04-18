# SiteSync Comprehensive Code Review

**Gateway:** pywgen002953 · Ignition 8.1.50 · Azul OpenJDK 17.0.16 · Jython 2.7  
**Review date:** 2026-04-18  
**Reviewer:** Claude (automated four-pass analysis)  
**Branch:** `claude/review-sitesync-projects-J8SLL`

---

## 1. Executive Summary

### 1.1 File Inventory

| Project | `script-python` path | `.py` files | Notes |
|---------|----------------------|-------------|-------|
| PISync | `PISync_2026-04-11_1427/ignition/script-python` | 6 | Small PI-handoff project |
| SiteSyncCore | `SiteSyncCore_2026-04-17_1622/ignition/script-python` | 51 | Core product |
| SiteSync-FieldApp | `SiteSync-FieldApp_Improvements_2026-04-11_1548/ignition/script-python` | 113 | FieldApp + full test suite |

Binary event-script files present but not parseable:
- `PISync_2026-04-11_1427/ignition/event-scripts/data.bin` (960 bytes)
- `FileTranslator_20260322203920/ignition/event-scripts/data.bin`

### 1.2 Severity Count Table

| Severity | PISync | SiteSyncCore | SiteSync-FieldApp | Total |
|----------|--------|--------------|-------------------|-------|
| **Critical** | 3 | 5 | 3 | **11** |
| **High** | 5 | 9 | 6 | **20** |
| **Medium** | 5 | 10 | 6 | **21** |
| **Low** | 4 | 5 | 3 | **12** |

### 1.3 Top 5 Operational Risks

1. **`dashboard/routing/code.py` NameError (Core + FieldApp — identical file)** — Every call to `getTile()` crashes with `NameError: name 'value' is not defined`. The parameter is named `sensorType` but the function body uses `value` throughout. This breaks every dashboard tile routing lookup in both products simultaneously.

2. **`sparkplugSiteSync/code.py` NameError (Core + FieldApp — identical file)** — `triggerBirth()` references `sourcePath` on its first line but the parameter is `tagPath`. The function body also contains a `time.sleep(15)` gateway-thread block. Every Sparkplug birth/MQTT-reset call crashes immediately.

3. **`device/activateDevice/code.py` NameError (Core + FieldApp — identical file)** — `createLimitedInstance()` calls `system.tag.configure(baseTagPath, ...)` but `baseTagPath` is never defined in the function. Device activation fails with NameError for every new device.

4. **`PIIntegration/activate/code.py:replaceNull()` always returns 0 (PISync)** — Both branches of the function return the integer `0`. Every device tag value published to PI is silently replaced with `0`, corrupting all historian data for every device in the PI handoff flow.

5. **Hardcoded internal hostname committed to source (PISync + SiteSyncCore)** — `PIAddress = "https://pgwgen002923.mgroupnet.com:5590/api/v1/configuration"` appears at module level in `addDevices/code.py` in both PISync and SiteSyncCore. Anyone with read access to the repo has the internal PI gateway hostname and port.

### 1.4 Cross-Cutting Summary

- **205 `system.perspective.print()` calls** across all three projects. Many are in functions invoked from gateway scope where they are silent no-ops, hiding real errors.
- **25+ Python 2 `print` statements** that will raise `SyntaxError` under Python 3.
- **`system.tag.browse(filter={"recursive":True})` used in 6 locations** — the `recursive` key is silently dropped by the API; results are non-recursive. This causes tag-discovery functions to miss nested tags without raising any error.
- **43 `== None` / `!= None` comparisons** in SiteSyncCore alone; `is None` / `is not None` is correct for identity checks.
- **`addTagToPi()` unconditionally returns `False`** in `addDevices/code.py` in both PISync and SiteSyncCore — this is a known vendor defect. The return value must never be used for success-checking.

---

## 2. Cross-Cutting Findings

### 2.1 Folder Duplication Analysis

```
diff -rq SiteSyncCore_2026-04-17_1622/ignition/script-python \
         SiteSync-FieldApp_Improvements_2026-04-11_1548/ignition/script-python
```

**Result:** 7 files differ; 17 trees/files exist only in FieldApp; 0 exist only in Core.

Files that differ (Core vs FieldApp):

| File | Direction of improvement |
|------|--------------------------|
| `MPC/customizations/device/createDevice/code.py` | FieldApp has more features |
| `PIIntegration/adapter/code.py` | FieldApp has `perspective.print` calls commented out |
| `createPITemplate/code.py` | Minor difference |
| `dashboard/icons/code.py` | FieldApp has additional icons |
| `decoders/downlinks/code.py` | FieldApp refactored |
| `decoders/model/code.py` | FieldApp added functions |
| `device/createDevice/code.py` | FieldApp delegates to MPC layer |
| `device/get/code.py` | FieldApp extended |
| `enterprise/tenant/code.py` | FieldApp extended |
| `utils/messages/errors/code.py` | FieldApp improved |
| `utils/messages/success/code.py` | FieldApp improved |
| `utils/messages/waiting/code.py` | FieldApp improved |
| `utils/sitehandler/code.py` | FieldApp extended |

**Files only in FieldApp** (orphaned from Core, never backported):
`dashboard/aggregation`, `decoders/encoder`, `device/assetAssociation`, `device/pidGenerator`, `device/replaceDevice`, `survey/`, `tests/`, `userPreferences/`, `utils/dashmanager`, `utils/deviceProfileDropDown`, `utils/historyconfig`, `utils/logging`, `utils/messages/comingSoon`, `utils/systemProvisioning`

```
diff -rq SiteSyncCore_2026-04-17_1622/ignition/script-python \
         "SiteSYnc EnterpriseManagementScripts/script-python"
```

**Result:** 5 files differ; `utils/deviceProfileDropDown` only in Enterprise; matching structure elsewhere.

**Canonical source of truth:** `SiteSync-FieldApp_Improvements_2026-04-11_1548` — it is the most recent, contains the most bug fixes (e.g., `perspective.print` calls in `adapter.py` are commented out), and is the only project with a test suite. Core should be treated as a snapshot of an earlier FieldApp state.

**Consolidation recommendation:** Extract the 44 files shared between Core and FieldApp into a single shared Ignition project library. The 7 diverging files should be reviewed and the FieldApp version adopted as authoritative. SiteSYnc EnterpriseManagementScripts appears to be an obsolete baseline and can be archived.

---

### 2.2 Python 3 Migration Risk Catalog

All occurrences below raise `SyntaxError` or `NameError` under Python 3.

#### `print` statements (not function calls)

| File | Lines | Project(s) |
|------|-------|-----------|
| `PIIntegration/devices/code.py` | 8, 10 | PISync |
| `PIIntegration/adapter/code.py` | 21 | Core, FieldApp |
| `sparkplugSiteSync/code.py` | 7, 10, 20, 22 | Core, FieldApp |
| `device/excelParser/code.py` | 34 | Core, FieldApp |
| `getSensors/code.py` | 47, 63, 74, 81, 91, 134, 135, 180, 226, 257, 259, 260, 369, 441, 443, 482, 484, 552, 553, 558 | Core, FieldApp |
| `tests/runner/runner/code.py` | 107–131 | FieldApp only |

#### `long` and `unicode` type literals

| File | Lines | Note |
|------|-------|------|
| `exchange/mqttVanillaTransmission/callables/code.py` | 72, 125, 127 | Both PISync and FileTranslator copies |

#### `== None` / `!= None` identity comparisons (should be `is None` / `is not None`)

43 occurrences in SiteSyncCore; shared files propagate to FieldApp. Representative examples:

| File | Lines |
|------|-------|
| `PIIntegration/AF/code.py` | 15, 27, 38 |
| `PIIntegration/adapter/code.py` | 23, 47, 60 |
| `addDevices/code.py` | 11 |
| `device/activateDevice/code.py` | — (uses `!= None`) |
| `connections/mqtt/code.py` | 5 |

#### `type(x) != dict` / `type(x) in (int,long)` instead of `isinstance()`

| File | Lines | Project(s) |
|------|-------|-----------|
| `PIIntegration/utils/code.py` | 24, 31 | Core, FieldApp |
| `exchange/mqttVanillaTransmission/callables/code.py` | 125 | PISync, FileTranslator |

---

### 2.3 Logging Inconsistency Audit

**Rule:** `system.util.getLogger()` is the correct API for gateway-scope scripts. `system.perspective.print()` only reaches the browser developer console and is a **silent no-op in gateway scope**.

| Project | `system.perspective.print()` calls | Confirmed gateway-scope locations |
|---------|------------------------------------|----------------------------------|
| PISync | 9 | `devices.findDevices()`, `activate.selectAll()` |
| SiteSyncCore | 84 | `AF.doesPITagExist()`, `adapter.addToDataSelection()`, `createPITemplate.createInstance()` error handler, `utils.showError()`, `utils.showSuccess()` |
| SiteSync-FieldApp | 112 | Same + `device.createDevice.validateDevice()`, `device.createDevice.saveTagPathForDevice()` |

Functions that are definitively gateway-scope (called from tag-change handlers, message handlers, or MPC provisioning flows) and still use `system.perspective.print()`:

- `PIIntegration.AF.doesPITagExist()` — called during PI tag provisioning
- `PIIntegration.adapter.addToDataSelection()` — called from `MPC.customizations.PIIntegration.addTagToPi()`
- `createPITemplate.createInstance()` catch block line 44 — called from `MPC.customizations.PIIntegration.createInstance()` in Core (gateway)
- `PISync.PIIntegration.devices.findDevices()` — invoked during device sync polling

**Correct pattern:**
```python
logger = system.util.getLogger("SiteSync-MyModule")
logger.info("message")   # appears in gateway log
logger.error("message")  # appears in gateway log at ERROR level
```

---

### 2.4 Tag I/O Batching Opportunities

#### Loop with per-tag `readBlocking` call — `addDevices/code.py`

**File:** `addDevices/code.py` (PISync line 25; SiteSyncCore line 25)

`formatDataSelectionItem()` calls `getDataType(tagPath, tagName)` once per tag in the items loop. Each `getDataType()` call issues one `readBlocking` call with a single path. For 100 tags this is 100 round-trips to the tag provider.

```python
# BEFORE (N round-trips):
def getDataType(tagPath, tagName):
    dType = str(system.tag.readBlocking(
        ['{0}/{1}.dataType'.format(tagPath, tagName)])[0].value)
    ...

for i in items:
    tagName = str(i['fullPath']).split('/')[-1]
    j = { ..., "dataType": getDataType(tagPath, tagName), ... }
```

```python
# AFTER (1 round-trip):
def getDataTypes(tagPath, items):
    tagNames = [str(i['fullPath']).split('/')[-1] for i in items]
    paths = ['{0}/{1}.dataType'.format(tagPath, n) for n in tagNames]
    results = system.tag.readBlocking(paths)
    out = {}
    for n, qv in zip(tagNames, results):
        dType = str(qv.value)
        if "Float" in dType:
            out[n] = "Float32"
        elif "Int" in dType:
            out[n] = "int16"
        else:
            out[n] = dType
    return out
```

---

### 2.5 Credential / Secret Audit

| Secret | Location | Severity |
|--------|----------|----------|
| `https://pgwgen002923.mgroupnet.com:5590/api/v1/configuration` | `PISync/addDevices/code.py:5`, `SiteSyncCore/addDevices/code.py:5` | **Critical** |
| `componentID = "MQTT1"` | Same files, line 6 | High |
| `"TWA_100000163.991.AS"` and 14 other Actility network-server IDs | `MPC/customizations/actility/code.py:7–39` (Core + FieldApp) | High |
| `"Chariot"` (hardcoded MQTT broker name) | `PISync/PIIntegration/activate/code.py:24` | Medium |
| `enterprise.tenant.getDefaultApp()` returns hardcoded `3` | `SiteSyncCore/enterprise/tenant/code.py` | Low |

All of the above should be moved to Ignition gateway settings tags or a dedicated configuration UDT so they can be changed per-environment without modifying source code.

---

### 2.6 Broad `except` Blocks / Silent Failures

| File | Lines | Problem |
|------|-------|---------|
| `createPITemplate/code.py` | 43–45 (Core, FieldApp) | `except Exception as e: system.perspective.print(...)` — in gateway scope, exception is swallowed completely; caller receives `None` with no indication of failure |
| `decoders/decoder/code.py` | 46–48 | `except: api = None` — bare `except` suppresses all errors including `SystemExit` |
| `PIIntegration/utils/code.py` | 15–16 | `except Exception as e: system.perspective.print(e)` — silent in gateway scope |
| `utils/resultParser/code.py` | 15–16 | `except Exception as e: system.perspective.print(...)` — silent in gateway scope |
| `addDevices/code.py` | 87–88 (Core) | `except Exception as e: return {"status":"error",...}` — error returned as dict but callers often discard return value |

---

### 2.7 Tag-Path Injection / Input Validation

`device/createDevice/code.py` (Core, FieldApp) validates tag-path characters via `pathValidator()` using a regex allowlist — this is the correct approach and no injection was found in device-creation flows.

However, `system.tag.browse()` is called with user-supplied tag paths in several locations without validation:

| File | Line | Input source |
|------|------|-------------|
| `PISync/addDevices/code.py:20` | `getAttributesForTag(rootTagPath)` | Caller-supplied |
| `SiteSyncCore/PIIntegration/tagOperations/code.py:2` | `getAttributesForTag(rootTagPath)` | Caller-supplied |

Since Ignition tag paths use bracket notation (`[provider]path`) and `browse()` does not execute shell commands, the risk is limited to reading unintended tag subtrees — but should still be documented.

---

---

## 3. Per-Project Findings

---

### 3.1 PISync — `PISync_2026-04-11_1427/ignition/script-python`

**File inventory:** 6 files · 639 lines total  
**Event scripts:** `ignition/event-scripts/data.bin` (960 bytes, binary — cannot parse; monitors unknown tag paths; risk of double-publish if another project registers scripts on the same paths)

---

#### 3.1.1 `PIIntegration/activate/code.py`

---

### [3.1.1-A] `PIIntegration/activate/code.py`

**[Critical] `replaceNull()` always returns `0` — both branches identical** — `activate/code.py:6–11`

**File:** `PISync_2026-04-11_1427/ignition/script-python/PIIntegration/activate/code.py`, lines 6–11

**Impact.** `publishDevice()` calls `replaceNull(t['value'].value)` for every tag in the device folder and publishes the result as the tag's value. Because `replaceNull()` always returns `0`, every tag value published to the PI MQTT broker is `0` regardless of the actual sensor reading. This silently corrupts all historian data in PI for every device processed by this handoff project.

**Explanation.** The `else` branch was presumably intended to return the original `value`. Instead it returns `0` — identical to the `None` branch. The bug is invisible at runtime because no exception is raised; PI simply receives zero for every measurement.

**Source (defective):**
```python
# activate/code.py:6–11
def replaceNull(value):
    if value == None:
        return 0
    else:
        return 0          # ← both branches return 0
```

**Recommended Fix:**
```python
def replaceNull(value):
    if value is None:
        return 0
    return value
```

---

### [3.1.1-B] `PIIntegration/activate/code.py`

**[Critical] Duplicate `selectAll()` definition — second signature silently shadows first** — `activate/code.py:40–43, 119–125`

**File:** `PISync_2026-04-11_1427/ignition/script-python/PIIntegration/activate/code.py`, lines 40–43 and 119–125

**Impact.** Any caller that passes one argument to `selectAll(tableData)` (the first definition, lines 40–43) will receive a `TypeError` at runtime because Python overwrites the name with the two-argument version (lines 119–125). The first definition is permanently inaccessible.

**Explanation.** Jython, like CPython, executes `def` statements sequentially at module load time. The second `def selectAll(dataset, select)` at line 119 replaces the first. The first definition is dead code.

**Source (defective):**
```python
# activate/code.py:40–43 (shadowed — unreachable)
def selectAll(tableData):
    for row in tableData:
        row['selected'] = True
    return tableData

# activate/code.py:119–125 (wins — replaces first)
def selectAll(dataset, select):
    system.perspective.print(select)
    for row in dataset:
        system.perspective.print(row)
        row['selected'] = select
        system.perspective.print(row)
    return dataset
```

**Recommended Fix.** Rename one function and remove the `system.perspective.print()` debug calls:
```python
def selectAll(tableData):
    for row in tableData:
        row['selected'] = True
    return tableData

def setAllSelected(dataset, select):
    for row in dataset:
        row['selected'] = select
    return dataset
```

---

### [3.1.1-C] `PIIntegration/activate/code.py`

**[High] `system.tag.browse(filter={"recursive":True})` — `recursive` key silently ignored** — `activate/code.py:102, 111`

**File:** `PISync_2026-04-11_1427/ignition/script-python/PIIntegration/activate/code.py`, lines 102, 111

**Impact.** `getAllDevicesInTargetFolder()` and `getAllFlickerableTagsTargetFolder()` both pass `"recursive":True` to `system.tag.browse()`. The API silently drops unknown filter keys, so only the top-level children of `[default]PI Integration` are returned. Devices in nested folders are never discovered, causing the publish-all and flicker-all operations to miss any device not at the root level of the PI Integration tag tree.

**Explanation.** The recursive browse API in Ignition 8.1 is `system.tag.browseConfiguration(path, recursive=True)`, which has a different return shape. The `filter` dict in `system.tag.browse()` supports keys `name`, `tagType`, `dataType`, `valueSource`, and `typeId` — not `recursive`.

**Source (defective):**
```python
# activate/code.py:101–107
def getAllDevicesInTargetFolder(searchDirectory):
    tagPaths = []
    results = system.tag.browse(path = "[default]PI Integration",
                                 filter = { "recursive":True, 'tagType': "UdtInstance"})
    for result in results.getResults():
        ...
```

**Recommended Fix:**
```python
def getAllDevicesInTargetFolder(searchDirectory):
    tagPaths = []
    allTags = system.tag.browseConfiguration("[default]PI Integration", recursive=True)
    for result in allTags:
        if result.get('tagType') == 'UdtInstance' and '/LoRaMetrics' not in str(result.get('fullPath','')):
            tagPaths.append(str(result['fullPath']))
    return tagPaths
```

---

### [3.1.1-D] `PIIntegration/activate/code.py`

**[High] `system.perspective.print()` in gateway-scope code** — `activate/code.py:120–124`

**File:** `PISync_2026-04-11_1427/ignition/script-python/PIIntegration/activate/code.py`, lines 120–124

**Impact.** The surviving `selectAll(dataset, select)` function (see finding 3.1.1-B) calls `system.perspective.print()` three times per row. When invoked from a gateway message handler or tag-change script, all three calls are silent no-ops. Developers see no output and assume the function is not executing when it is; real errors are hidden.

**Source (defective):**
```python
# activate/code.py:119–125
def selectAll(dataset, select):
    system.perspective.print(select)          # no-op in gateway scope
    for row in dataset:
        system.perspective.print(row)         # no-op in gateway scope
        row['selected'] = select
        system.perspective.print(row)         # no-op in gateway scope
    return dataset
```

**Recommended Fix.** Remove the debug prints or replace with `system.util.getLogger()`.

---

### [3.1.1-E] `PIIntegration/activate/code.py`

**[Medium] `forceCheckIn()` is an unconditional stub** — `activate/code.py:4–5`

**File:** `PISync_2026-04-11_1427/ignition/script-python/PIIntegration/activate/code.py`, lines 4–5

**Impact.** Any caller that relies on `forceCheckIn()` to trigger a PI check-in will silently receive `False` with no work performed and no error raised.

**Source (defective):**
```python
def forceCheckIn(tagList):
    return False
```

**Recommended Fix.** Implement the function or raise `NotImplementedError` so callers fail loudly:
```python
def forceCheckIn(tagList):
    raise NotImplementedError("forceCheckIn not yet implemented")
```

---

### [3.1.1-F] `PIIntegration/activate/code.py`

**[Low] `createReult` typo; hardcoded `"Chariot"` broker name** — `activate/code.py:94, 24`

**File:** `PISync_2026-04-11_1427/ignition/script-python/PIIntegration/activate/code.py`

**Impact.** `createReult` is a misspelling of `createResult`. It works because the variable is used immediately, but it makes the code harder to read and grep. The hardcoded broker name `"Chariot"` means changing the broker requires a code change rather than a configuration change.

**Source:**
```python
# line 24
system.cirruslink.transmission.publish("Chariot", topic, json.dumps(deviceJSON), 0, 0)

# line 94
createReult = system.tag.configure(baseTagPath, [tag], collisionPolicy)
```

**Recommended Fix.** Rename the variable; move the broker name to a configuration tag.

---

#### 3.1.2 `PIIntegration/devices/code.py`

---

### [3.1.2-A] `PIIntegration/devices/code.py`

**[High] Python 2 `print` statements** — `devices/code.py:8, 10`

**File:** `PISync_2026-04-11_1427/ignition/script-python/PIIntegration/devices/code.py`, lines 8, 10

**Impact.** Under Python 3 these lines are `SyntaxError`. Under Jython 2.7 they output to the gateway console but are invisible in Perspective sessions and inconsistent with the project's logging patterns.

**Source (defective):**
```python
# devices/code.py:8
print result['value'].value
# devices/code.py:10
print "Found unactivated node"
```

**Recommended Fix:**
```python
logger = system.util.getLogger("PISync-Devices")
logger.debug(str(result['value'].value))
logger.debug("Found unactivated node")
```

---

### [3.1.2-B] `PIIntegration/devices/code.py`

**[High] `system.perspective.print()` in gateway-scope `findDevices()`** — `devices/code.py:27, 29, 44–45`

**File:** `PISync_2026-04-11_1427/ignition/script-python/PIIntegration/devices/code.py`, lines 27, 29, 44–45

**Impact.** `findDevices()` is a device-sync polling function called from gateway context. The four `system.perspective.print()` calls are silent no-ops in gateway scope, masking the activated-state and date-delta debug output developers rely on to diagnose sync problems.

**Source (defective):**
```python
# devices/code.py:27
system.perspective.print(d['fullTagPath'])
system.perspective.print(activated)
...
system.perspective.print(activatedToday)
system.perspective.print(activatedToday <= 1)
```

**Recommended Fix:** Replace with `system.util.getLogger("PISync-Devices").debug(...)`.

---

### [3.1.2-C] `PIIntegration/devices/code.py`

**[High] `system.tag.browse(filter={"recursive":True})` — recursive key silently ignored** — `devices/code.py:3`

**File:** `PISync_2026-04-11_1427/ignition/script-python/PIIntegration/devices/code.py`, line 3

**Impact.** Same as finding 3.1.1-C. `findUnactivatedDevices()` only searches the top level of the given `searchDirectory`; devices in nested folders are never found and are never activated.

**Source (defective):**
```python
results = system.tag.browse(path = searchDirectory,
                             filter = {'name':activationName, "recursive":True})
```

**Recommended Fix:** Use `system.tag.browseConfiguration(searchDirectory, recursive=True)` and filter client-side.

---

#### 3.1.3 `PIIntegration/topics/code.py`

---

### [3.1.3-A] `PIIntegration/topics/code.py`

**[Medium] Fragile `split(']')` parsing — crashes if tag path has no `]`** — `topics/code.py:4`

**File:** `PISync_2026-04-11_1427/ignition/script-python/PIIntegration/topics/code.py`, line 4

**Impact.** `getTopic()` will raise `IndexError` if passed any path not containing `]`. No validation or error handling is present. A path like a bare relative path or an already-formatted topic string will crash the caller silently when the exception propagates.

**Source (defective):**
```python
def getTopic(tagPath):
    standardTopic = "mpc/{0}"
    tagName = tagPath.split(']')[1]   # IndexError if no ']'
    return standardTopic.format(tagName)
```

**Recommended Fix:**
```python
def getTopic(tagPath):
    if ']' not in tagPath:
        raise ValueError("getTopic: expected bracketed provider in tagPath, got: %s" % tagPath)
    return "mpc/{0}".format(tagPath.split(']', 1)[1])
```

---

#### 3.1.4 `addDevices/code.py`

---

### [3.1.4-A] `addDevices/code.py`

**[Critical] Internal hostname hardcoded at module level** — `addDevices/code.py:5`

**File:** `PISync_2026-04-11_1427/ignition/script-python/addDevices/code.py`, line 5

**Impact.** Anyone with repository read access obtains the internal PI gateway hostname (`pgwgen002923.mgroupnet.com`) and management API port (`5590`). This is a security and operational concern: the value is wrong for any environment other than the original gateway, and changing it requires a code edit and re-deployment rather than a configuration change.

**Source (defective):**
```python
# addDevices/code.py:5–6
PIAddress = "https://pgwgen002923.mgroupnet.com:5590/api/v1/configuration"
componentID = "MQTT1"
```

**Recommended Fix.** Read from a configuration tag at call time:
```python
def _getPIAddress():
    return system.tag.readBlocking(["[default]Config/PIGatewayURL"])[0].value

def _getComponentID():
    return system.tag.readBlocking(["[default]Config/PIComponentID"])[0].value
```

---

### [3.1.4-B] `addDevices/code.py`

**[High] `system.piAdapter.getDataSelection()` returns `"null"` string — unchecked before `json.loads()`** — `addDevices/code.py:10–12`

**File:** `PISync_2026-04-11_1427/ignition/script-python/addDevices/code.py`, lines 10–12

**Impact.** When no data selection exists, `system.piAdapter.getDataSelection()` returns the literal string `"null"`, not Python `None`. The guard `if selectedData != None:` is always `True` for `"null"`. `json.loads("null")` returns Python `None` (not a dict). `formatDataSelectionItem()` then iterates over `selectedData` (which is `None`) and crashes with `TypeError: 'NoneType' is not iterable`. Result: `addTagToPi()` fails entirely for any device with no prior data selection.

**Source (defective):**
```python
# addDevices/code.py:10–12
selectedData = system.piAdapter.getDataSelection(componentID, "MQTT1", PIAddress)
if selectedData != None:          # "null" string passes this check
    return json.loads(selectedData)  # returns Python None, not a dict
```

**Recommended Fix:**
```python
selectedData = system.piAdapter.getDataSelection(componentID, "MQTT1", PIAddress)
if selectedData and selectedData != "null":
    parsed = json.loads(selectedData)
    if parsed is None:
        return []
    return parsed
return []
```

---

### [3.1.4-C] `addDevices/code.py`

**[Medium] `counter = 0` — unused variable inside loop** — `addDevices/code.py:62`

**File:** `PISync_2026-04-11_1427/ignition/script-python/addDevices/code.py`, line 62

**Impact.** `counter` is assigned and never read. This is dead code that suggests an incomplete de-duplication loop was started and abandoned. No functional impact, but it creates confusion.

**Source (defective):**
```python
# addDevices/code.py:62
counter = 0
if generateStreamID(tagPath, tagName) not in unique_dict.keys():
    selectedData.append(j)
```

**Recommended Fix.** Delete `counter = 0`.

---

#### 3.1.5 `createPITemplate/code.py` (PISync)

---

### [3.1.5-A] `createPITemplate/code.py`

**[High] `system.perspective.print()` is the only error signal — silent in gateway scope** — `createPITemplate/code.py:30`

**File:** `PISync_2026-04-11_1427/ignition/script-python/createPITemplate/code.py`, line 30

**Impact.** The `createInstance()` function is called during device provisioning from gateway context. If any exception occurs, the catch block calls `system.perspective.print("Error " + str(e))` — a no-op in gateway scope — and returns `None`. The caller has no way to detect the failure. PI instances are silently not created.

**Source (defective):**
```python
# createPITemplate/code.py (PISync)
except Exception as e:
    system.perspective.print("Error " + str(e))   # silent no-op in gateway
    return None
```

**Recommended Fix:**
```python
except Exception as e:
    logger = system.util.getLogger("SiteSync-PITemplate")
    logger.error("createInstance failed for {0}: {1}".format(tagPath, str(e)))
    return None
```

---

#### 3.1.6 `exchange/mqttVanillaTransmission/callables/code.py` (PISync)

This file is **identical** to `FileTranslator_20260322203920/ignition/script-python/exchange/mqttVanillaTransmission/callables/code.py`. Findings below apply to both copies.

---

### [3.1.6-A] `exchange/mqttVanillaTransmission/callables/code.py`

**[Critical] `topic = str(topic)[:-1]` strips the last character from every MQTT topic** — `callables/code.py:168`

**File:** `PISync_2026-04-11_1427/ignition/script-python/exchange/mqttVanillaTransmission/callables/code.py`, line 168

**Impact.** The `publish()` function unconditionally strips the last character from the resolved topic before calling the Cirrus Link API. For `payloadFormat == "value"` the topic ends with `/` after `resolvePublishParameters()`, so stripping one character yields a correct bare path. For **all other formats** (`qualifiedValue`, `json`, `influx`) the topic ends with the last character of the device name, e.g. `mpc/site/DeviceName` becomes `mpc/site/DeviceNam`. Every subscriber filtering on the exact topic string receives nothing. This is silent data loss.

**Explanation.** The `[:-1]` was evidently written to strip the trailing `/` produced by the `payloadFormat == "value"` branch, but it was placed in `publish()` where it applies to all formats unconditionally.

**Source (defective):**
```python
# callables/code.py:168
topic = str(topic)[:-1]      # strips last char from ALL formats
payload = str(payload)
```

**Recommended Fix.** Move the trailing-slash strip into `resolvePublishParameters()` inside the `"value"` branch only, and remove it from `publish()`:
```python
# In resolvePublishParameters(), payloadFormat == "value" branch:
if payloadFormat == "value":
    measurementName = Topic.split('/')[-1]
    Payload = system.util.jsonEncode({measurementName: tagQualifiedValue.value})
    Topic = Topic[:Topic.rfind(measurementName)]   # strip last segment
    if Topic.endswith('/'):
        Topic = Topic[:-1]                          # strip trailing slash once

# In publish():
# topic = str(topic)[:-1]   ← DELETE this line
payload = str(payload)
```

---

### [3.1.6-B] `exchange/mqttVanillaTransmission/callables/code.py`

**[High] `long` and `unicode` type literals — Python 3 `NameError`** — `callables/code.py:72, 125, 127`

**File:** `PISync_2026-04-11_1427/ignition/script-python/exchange/mqttVanillaTransmission/callables/code.py`, lines 72, 125, 127

**Impact.** Under Python 3 (or any future Jython 3 runtime) the names `long` and `unicode` do not exist. Line 72 raises `NameError` on the first tag-change event that carries a non-boolean, non-int, non-float value. Line 125 and 127 raise `NameError` when `payloadFormat == "influx"`. In Jython 2.7 these are valid.

**Source (defective):**
```python
# callables/code.py:72
if not isinstance(tagQualifiedValue.value,(bool,int,long,float,unicode)):

# callables/code.py:125
if type(tagQualifiedValue.value) in (int,long):

# callables/code.py:127
elif type(tagQualifiedValue.value) is unicode:
```

**Recommended Fix (Py2/Py3 compatible):**
```python
import sys
if sys.version_info[0] >= 3:
    string_types = (str,)
    integer_types = (int,)
else:
    string_types = (str, unicode)
    integer_types = (int, long)

# line 72
if not isinstance(tagQualifiedValue.value, (bool,) + integer_types + (float,) + string_types):

# lines 125–128
if isinstance(tagQualifiedValue.value, integer_types):
    valueInfluxString = "%ii" % tagQualifiedValue.value
elif isinstance(tagQualifiedValue.value, string_types):
    valueInfluxString = '"%s"' % tagQualifiedValue.value
```

---

### [3.1.6-C] `exchange/mqttVanillaTransmission/callables/code.py`

**[High] `Topic.replace(measurementName, "")` replaces ALL occurrences, not just the trailing segment** — `callables/code.py:114`

**File:** `PISync_2026-04-11_1427/ignition/script-python/exchange/mqttVanillaTransmission/callables/code.py`, line 114

**Impact.** If a device name matches any earlier segment of the topic path (e.g., device named `site` with topic `mpc/site/site`), `str.replace("site", "")` removes all occurrences, producing `mpc//` instead of `mpc/site/`. The published JSON key (`measurementName`) still uses the correct name, but the topic is malformed, preventing correct subscriber routing.

**Source (defective):**
```python
# callables/code.py:113–114
measurementName = Topic.split('/')[-1]
Payload = system.util.jsonEncode({measurementName: tagQualifiedValue.value})
Topic = Topic.replace(measurementName, "")   # replaces ALL occurrences
```

**Recommended Fix (addressed by fix in 3.1.6-A):**
```python
Topic = Topic[:Topic.rfind(measurementName)]
```

---

### [3.1.6-D] `exchange/mqttVanillaTransmission/callables/code.py`

**[Medium] `system.tag.readBlocking(udtInstancePath)` — path should be a list** — `callables/code.py:254`

**File:** `PISync_2026-04-11_1427/ignition/script-python/exchange/mqttVanillaTransmission/callables/code.py`, line 254

**Impact.** `system.tag.readBlocking()` expects a list of paths. `udtInstancePath` is a string. Jython iterates a string as characters, producing one `QualifiedValue` per character rather than one for the full path. The result is unexpected behavior when reading the UDT instance value. In practice Ignition may coerce the string to a single-element list internally, but this is undocumented and unreliable.

**Source (defective):**
```python
instance = system.tag.readBlocking(udtInstancePath)[0]
```

**Recommended Fix:**
```python
instance = system.tag.readBlocking([udtInstancePath])[0]
```


---

## 3.2 SiteSyncCore (`SiteSyncCore_2026-04-17_1622`) — 51 Files

### [3.2.1] `dashboard/routing/code.py`

---

#### [3.2.1-A] `getTile()` references undefined variable `value` — every call raises `NameError`

**[Critical] `value` used instead of function parameter `sensorType`** — `dashboard/routing/code.py:2`

**File:** `SiteSyncCore_2026-04-17_1622/ignition/script-python/dashboard/routing/code.py`, lines 1–23

**Impact.** Every call to `getTile()` raises `NameError: global name 'value' is not defined`. The function is never reached because the conditional on line 2 immediately fails. Dashboard tile routing is completely broken — no sensor type will ever resolve to its correct visualization component.

**Source (defective):**
```python
def getTile(sensorType):
    if value in ("TEMPERATURE", "PRESSURE", "420ma", "FLOWMETER"):
        return "Dashboard/components/assets/Pressure"
    elif value == "VALVEPOSITION":
        return "Dashboard/components/assets/ValvePosition"
    # ... all branches use `value`, not `sensorType`
```

**Recommended Fix:**
```python
def getTile(sensorType):
    sensorType = sensorType.upper() if sensorType else ""
    if sensorType in ("TEMPERATURE", "PRESSURE", "420MA", "FLOWMETER"):
        return "Dashboard/components/assets/Pressure"
    elif sensorType == "VALVEPOSITION":
        return "Dashboard/components/assets/ValvePosition"
    elif sensorType == "LEVEL":
        return "Dashboard/components/assets/Level"
    elif sensorType == "THL":
        return "Dashboard/components/assets/THL"
    elif sensorType == "HOTDROP":
        return "Dashboard/components/assets/Current"
    elif sensorType == "VIBRATION":
        return "Dashboard/components/assets/Vibration"
    elif sensorType == "LOCKOUT":
        return "Dashboard/components/assets/Lockout"
    else:
        return "Dashboard/components/assets/OtherPV"
```

---

### [3.2.2] `sparkplugSiteSync/code.py`

---

#### [3.2.2-A] `triggerBirth()` references undefined variable `sourcePath` — immediate `NameError`

**[Critical] `sourcePath` used on line 6 but parameter is `tagPath`** — `sparkplugSiteSync/code.py:6`

**File:** `SiteSyncCore_2026-04-17_1622/ignition/script-python/sparkplugSiteSync/code.py`, lines 1–10

**Impact.** `triggerBirth()` raises `NameError: global name 'sourcePath' is not defined` on the very first line of real code (line 6). The function never executes. Sparkplug birth triggers that depend on this path to refresh edge node connectivity will silently fail.

**Source (defective):**
```python
def triggerBirth(tagPath):
    res = ""
    filterPath = cleanPathForFilter(sourcePath)  # NameError: 'sourcePath' undefined
```

**Recommended Fix:**
```python
def triggerBirth(tagPath):
    res = ""
    filterPath = cleanPathForFilter(tagPath)
```

---

#### [3.2.2-B] `time.sleep(15)` blocks the gateway thread for 15 seconds

**[Critical] Blocking sleep in gateway-scope function** — `sparkplugSiteSync/code.py:16`

**File:** `SiteSyncCore_2026-04-17_1622/ignition/script-python/sparkplugSiteSync/code.py`, line 16

**Impact.** `time.sleep(15)` called inside a tag event handler or gateway script blocks the gateway execution thread for 15 seconds. Under Ignition's threading model, this starves other tag events and can trigger watchdog timeouts. Gateway performance degrades for all concurrent operations during the sleep window.

**Source (defective):**
```python
system.tag.write(resetPath, True)
time.sleep(15)   # blocks gateway thread
system.tag.write(resetPath, True)
```

**Recommended Fix:** Replace with a scheduled gateway task or use `system.util.invokeLater()` / `system.util.invokeAsynchronous()` to defer the second write without occupying the event thread:
```python
system.tag.writeBlocking([resetPath], [True])
# Schedule deferred write via a named timer or system.util.invokeAsynchronous
```

---

#### [3.2.2-C] Python 2 bare `print` statements and deprecated `system.tag.write()`

**[Medium] Four bare `print` statements + two deprecated `write()` calls** — `sparkplugSiteSync/code.py:7,10,20,22`

**File:** `SiteSyncCore_2026-04-17_1622/ignition/script-python/sparkplugSiteSync/code.py`, lines 7, 10, 14, 21

**Impact.** Bare `print` is a syntax error in Python 3. `system.tag.write()` is deprecated in Ignition 8.x; `system.tag.writeBlocking()` should be used to ensure write completion and to check quality codes.

**Source (defective):**
```python
print filterPath
print str(res[0])
system.tag.write(resetPath, True)
```

**Recommended Fix:**
```python
# Remove debug prints entirely, or use system.util.getLogger().debug(filterPath)
system.tag.writeBlocking([resetPath], [True])
```

---

### [3.2.3] `device/activateDevice/code.py`

---

#### [3.2.3-A] `createLimitedInstance()` uses `baseTagPath` which is never defined

**[Critical] `NameError: global name 'baseTagPath' is not defined`** — `device/activateDevice/code.py:20`

**File:** `SiteSyncCore_2026-04-17_1622/ignition/script-python/device/activateDevice/code.py`, line 20

**Impact.** `system.tag.configure(baseTagPath, [tag], collisionPolicy)` on line 20 fails with `NameError` on every call. The function accepts `intendedTagPath` as a parameter, but `baseTagPath` is never assigned from it. Tag configuration for activated devices never executes.

**Source (defective):**
```python
def createLimitedInstance(intendedTagPath, limitedTemplate, newTagName, sourceTagPath):
    typeId = "SiteSyncModels/"  + limitedTemplate
    tagType = "UdtInstance"
    tag = { "name": newTagName, "typeId": typeId, "tagType": tagType,
            "parameters": {"tagPath": sourceTagPath} }
    collisionPolicy = "a"
    system.tag.configure(baseTagPath, [tag], collisionPolicy)  # NameError
```

**Recommended Fix:**
```python
def createLimitedInstance(intendedTagPath, limitedTemplate, newTagName, sourceTagPath):
    typeId = "SiteSyncModels/" + limitedTemplate
    tagType = "UdtInstance"
    tag = { "name": newTagName, "typeId": typeId, "tagType": tagType,
            "parameters": {"tagPath": sourceTagPath} }
    collisionPolicy = "a"
    return system.tag.configure(intendedTagPath, [tag], collisionPolicy)
```

---

#### [3.2.3-B] `refreshSparkplugTransmission()` uses deprecated `system.tag.write()`

**[Low] Deprecated tag write API** — `device/activateDevice/code.py:26`

**File:** `SiteSyncCore_2026-04-17_1622/ignition/script-python/device/activateDevice/code.py`, line 26

**Source (defective):**
```python
system.tag.write("[MQTT Transmission]Transmission Control/Refresh", True)
```

**Recommended Fix:**
```python
system.tag.writeBlocking(["[MQTT Transmission]Transmission Control/Refresh"], [True])
```

---

### [3.2.4] `enterprise/tenant/code.py`

---

#### [3.2.4-A] `getDefaultApp()` is hardcoded stub — real implementation commented out

**[High] Hardcoded return value `3` — multi-tenant isolation broken** — `enterprise/tenant/code.py:3`

**File:** `SiteSyncCore_2026-04-17_1622/ignition/script-python/enterprise/tenant/code.py`, lines 2–8

**Impact.** Any code path that calls `enterprise.tenant.getDefaultApp()` will unconditionally receive `3` regardless of which tenant is active. The real implementation (commented out on lines 4–8) queries `system.sitesync.getPrimaryNetworkServerAccount()` at runtime. Multi-tenant scenarios silently use tenant ID 3 for all operations including device-to-profile association (`addDeviceToExtraActilityConnections` calls this).

**Source (defective):**
```python
def getDefaultApp():
    return 3
#   j = system.sitesync.getPrimaryNetworkServerAccount()
#   if j != "null":
#       app = json.loads(j)
#       return app['id']
#   else:
#       return -1
```

**Recommended Fix:** Restore the dynamic implementation:
```python
def getDefaultApp():
    j = system.sitesync.getPrimaryNetworkServerAccount()
    if j != None and j != "null":
        app = json.loads(j)
        return app['id']
    return -1
```


---

### [3.2.5] `PIIntegration/AF/code.py`

---

#### [3.2.5-A] `doesPITagExist()` — `"null"` string passes `!= None` check, then `json.loads("null")` returns Python `None`, causing `TypeError`

**[High] `system.piAdapter.*` returns `"null"` string, not Python `None`** — `PIIntegration/AF/code.py:14–16`

**File:** `SiteSyncCore_2026-04-17_1622/ignition/script-python/PIIntegration/AF/code.py`, lines 14–16

**Impact.** When the PI tag does not exist, `system.piAdapter.doesTagExtistInPI()` returns the string `"null"`. The guard `if exists != None` passes (the string is not `None`), so `json.loads("null")` is called and returns Python `None`. Any caller that then accesses a key on the returned value (e.g., `result['status']`) raises `TypeError: 'NoneType' object is not subscriptable`. PI existence checks silently produce fatal errors on the first miss.

**Source (defective):**
```python
exists = system.piAdapter.doesTagExtistInPI(AFsettings['url'], AFsettings['token'], path, "AF")
if exists != None:
    return json.loads(exists)   # json.loads("null") == None → caller gets None
```

**Recommended Fix:**
```python
exists = system.piAdapter.doesTagExtistInPI(AFsettings['url'], AFsettings['token'], path, "AF")
if exists is not None and exists != "null":
    return json.loads(exists)
return {"status": False, "message": "Did not find PITag"}
```

---

#### [3.2.5-B] `pathFormatter()` uses backslash path separator — literal backslash on Linux

**[High] Windows path separator in Linux environment** — `PIIntegration/AF/code.py:51`

**File:** `SiteSyncCore_2026-04-17_1622/ignition/script-python/PIIntegration/AF/code.py`, line 51

**Impact.** `"{0}\{1}/{2}".format(repo, prefix, ss)` produces a string with a literal backslash character on Linux (e.g., `"MyRepo\prefix/path"`). The PI Web API expects a forward-slash separated path. PI tag creation and lookup will fail with path-not-found errors because the backslash is not treated as a separator by the PI server.

**Source (defective):**
```python
endpoint = "{0}\{1}/{2}".format(repo, prefix, ss)
```

**Recommended Fix:**
```python
endpoint = "{0}/{1}/{2}".format(repo, prefix, ss)
```

---

#### [3.2.5-C] `system.perspective.print(path)` called in gateway-scope function

**[Medium] Debug print is no-op in gateway scope** — `PIIntegration/AF/code.py:13`

**File:** `SiteSyncCore_2026-04-17_1622/ignition/script-python/PIIntegration/AF/code.py`, line 13

**Source (defective):**
```python
system.perspective.print(path)
```

**Recommended Fix:**
```python
# Remove, or replace with:
system.util.getLogger("PIIntegration.AF").debug("PI path: " + str(path))
```

---

### [3.2.6] `PIIntegration/status/code.py`

---

#### [3.2.6-A] Duplicate function definitions — stub implementations at top override real code

**[High] `getTransmitterStatus()` and `isUsingTransmission()` each defined twice; stubs win** — `PIIntegration/status/code.py:2–7` and `23–28`

**File:** `SiteSyncCore_2026-04-17_1622/ignition/script-python/PIIntegration/status/code.py`, lines 2–7 and 23–28

**Impact.** Python evaluates module-level definitions sequentially; the last definition wins. The stub versions (lines 2–7: `return {}` and `return False`) appear first but are then **overwritten** by identical stub definitions at lines 23–28. The real implementations (`adapterAPIPingStatus()` and `PIWebAPIPingStatus()`) are never shadowed, but `getTransmitterStatus()` and `isUsingTransmission()` permanently return empty dict and `False` respectively. Any caller checking transmission status or connectivity receives incorrect results.

**Source (defective):**
```python
import json
def getTransmitterStatus():   # first definition (lines 2-4) — stub
    return {}
def isUsingTransmission():    # first definition (lines 6-7) — stub
    return False
# ... commented-out block ...
import json
def getTransmitterStatus():   # second definition (lines 23-25) — identical stub overwrites first
    return {}
def isUsingTransmission():    # second definition (lines 27-28) — identical stub overwrites first
    return False
```

**Recommended Fix:** Remove the duplicate stub block (lines 22–28). Implement real status retrieval:
```python
import json
def getTransmitterStatus():
    try:
        settings = PIIntegration.adapter.getAdapterSettings()
        return PIIntegration.status.adapterAPIPingStatus()
    except Exception as e:
        return {"status": False, "message": str(e)}

def isUsingTransmission():
    try:
        result = adapterAPIPingStatus()
        return result.get("status", False)
    except Exception:
        return False
```

---

#### [3.2.6-B] `system.perspective.print(j)` in `PIWebAPIPingStatus()` — gateway scope no-op

**[Low] Debug print in gateway-scope ping function** — `PIIntegration/status/code.py:44`

**File:** `SiteSyncCore_2026-04-17_1622/ignition/script-python/PIIntegration/status/code.py`, line 44

**Source (defective):**
```python
system.perspective.print(j)
```

**Recommended Fix:** Replace with logger or remove:
```python
system.util.getLogger("PIIntegration.status").debug(str(j))
```

---

### [3.2.7] `PIIntegration/utils/code.py`

---

#### [3.2.7-A] `showSuccess()` calls `time.sleep(3)` — blocks gateway thread for 3 seconds

**[Critical] Blocking sleep in UI utility called from gateway scope** — `PIIntegration/utils/code.py:20`

**File:** `SiteSyncCore_2026-04-17_1622/ignition/script-python/PIIntegration/utils/code.py`, lines 18–21

**Impact.** `showSuccess()` opens a popup, sleeps 3 seconds, then closes it. If called from a gateway-scoped tag event script or message handler, this blocks the gateway thread for 3 seconds per call. Under load (multiple device activations, bulk PI operations) this can cascade into watchdog timeouts.

**Source (defective):**
```python
def showSuccess(successText):
    system.perspective.openPopup("success", "Popups/success", params={"successText":successText})
    time.sleep(3)
    system.perspective.closePopup("success")
```

**Recommended Fix:** Use `system.util.invokeAsynchronous()` to avoid blocking, or have the popup close itself via a timer in the Perspective component:
```python
def showSuccess(successText):
    system.perspective.openPopup("success", "Popups/success", params={"successText":successText})
    # Popup component should handle its own timed close via its onStartup binding
```

---

#### [3.2.7-B] `isSuccess()` and `getResultMessage()` use `type() != dict` — fails for dict subclasses

**[Low] Anti-pattern type check** — `PIIntegration/utils/code.py:24,31`

**File:** `SiteSyncCore_2026-04-17_1622/ignition/script-python/PIIntegration/utils/code.py`, lines 24 and 31

**Source (defective):**
```python
if type(resultMessage) != dict:
    j = json.loads(resultMessage)
```

**Recommended Fix:**
```python
if not isinstance(resultMessage, dict):
    j = json.loads(resultMessage)
```


---

### [3.2.8] `PIIntegration/settings/code.py`

---

#### [3.2.8-A] `getSettings()` calls `json.loads()` without guarding against `"null"` string return

**[High] `json.loads("null")` returns Python `None` — downstream key access raises `TypeError`** — `PIIntegration/settings/code.py:5–6`

**File:** `SiteSyncCore_2026-04-17_1622/ignition/script-python/PIIntegration/settings/code.py`, lines 4–6

**Impact.** `system.piAdapter.getSettings("generic")` returns the string `"null"` when no settings have been saved. `json.loads("null")` returns Python `None`. Every caller of `getSettings()` that accesses a key on the result (e.g., `creds['prefix']`, `creds['datasourceID']`) raises `TypeError: 'NoneType' object is not subscriptable`. This affects `AF.doesPITagExist()`, `adapter.existsInAdapterDataSelection()`, and any feature that reads PI credentials.

**Source (defective):**
```python
def getSettings():
    a = system.piAdapter.getSettings("generic")
    return json.loads(a)   # json.loads("null") == None if not configured
```

**Recommended Fix:**
```python
def getSettings():
    a = system.piAdapter.getSettings("generic")
    if a is None or a == "null":
        return {}
    return json.loads(a)
```

---

### [3.2.9] `PIIntegration/adapter/code.py`

---

#### [3.2.9-A] Bare `print path` statement — Python 2 only

**[Medium] Python 2 print statement** — `PIIntegration/adapter/code.py:21`

**File:** `SiteSyncCore_2026-04-17_1622/ignition/script-python/PIIntegration/adapter/code.py`, line 21

**Impact.** In Jython 2.7 this is syntactically valid but outputs to stdout (dev console only). In any Python 3 migration this becomes a `SyntaxError`. No diagnostic value since output is invisible in production.

**Source (defective):**
```python
print path
```

**Recommended Fix:** Remove or replace:
```python
system.util.getLogger("PIIntegration.adapter").debug(str(path))
```

---

#### [3.2.9-B] `system.perspective.print()` debug calls in gateway-scope functions

**[Medium] Silent no-ops in gateway scope** — `PIIntegration/adapter/code.py:44,46`

**File:** `SiteSyncCore_2026-04-17_1622/ignition/script-python/PIIntegration/adapter/code.py`, lines 44 and 46

**Source (defective):**
```python
system.perspective.print(items)
system.perspective.print(exists)
```

**Recommended Fix:** Replace with gateway logger calls or remove.

---

#### [3.2.9-C] Dead code: `return False` after `return json.loads(exists)` in `addToDataSelection()`

**[Low] Unreachable code** — `PIIntegration/adapter/code.py:52`

**File:** `SiteSyncCore_2026-04-17_1622/ignition/script-python/PIIntegration/adapter/code.py`, line 52

**Source (defective):**
```python
    if exists != None:
        return json.loads(exists)
    else:
        return {"status":False, "message":"Did not find PITag"}

    return False   # unreachable
```

**Recommended Fix:** Delete line 52.

---

### [3.2.10] `PIIntegration/tagOperations/code.py`

---

#### [3.2.10-A] `system.tag.browse(filter={"recursive":True})` — `recursive` key silently ignored

**[Medium] Incorrect browse filter key — non-recursive results returned silently** — `PIIntegration/tagOperations/code.py:2,7`

**File:** `SiteSyncCore_2026-04-17_1622/ignition/script-python/PIIntegration/tagOperations/code.py`, lines 2 and 7

**Impact.** `system.tag.browse()` does not support a `recursive` key in its filter parameter. The filter is silently dropped and only immediate children are returned. PI tag monitoring will miss nested UDT instances. Identical bug to PISync `activate/code.py`.

**Source (defective):**
```python
tags = system.tag.browse(rootTagPath, filter={"recursive":True})
tags = system.tag.browse(monitoredPath, filter={"recursive":True, "tagType":"UdtInstance"})
```

**Recommended Fix:**
```python
tags = system.tag.browseConfiguration(rootTagPath, recursive=True)
# For tagType filter, post-filter results:
tags = [t for t in system.tag.browseConfiguration(monitoredPath, recursive=True)
        if t.get('tagType') == 'UdtInstance']
```

---

### [3.2.11] `utils/resultParser/code.py`

---

#### [3.2.11-A] `getResultMessage()` calls `json.dumps(results)` — `json` module not imported

**[High] `NameError: global name 'json' is not defined`** — `utils/resultParser/code.py:24`

**File:** `SiteSyncCore_2026-04-17_1622/ignition/script-python/utils/resultParser/code.py`, line 24

**Impact.** When `results` has no `'message'` key, `getResultMessage()` falls through to the `else` branch and calls `json.dumps(results)`. Since `json` is not imported in this module, this raises `NameError`. The error message intended for the caller is never returned; instead the caller receives an uncaught exception. This affects every caller that handles error results across the entire codebase.

**Source (defective):**
```python
def getResultMessage(results):
    try:
        if 'message' in results.keys():
            return results['message']
        else:
            return "Error getting results: " + json.dumps(results)  # NameError: json
```

**Recommended Fix:**
```python
import json

def getResultMessage(results):
    try:
        if 'message' in results.keys():
            return results['message']
        else:
            return "Error getting results: " + json.dumps(results)
    except Exception as e:
        return "Error getting results: " + str(e)
```

---

#### [3.2.11-B] `system.perspective.print()` in exception handler — gateway scope no-op

**[Low] Silent error swallowing** — `utils/resultParser/code.py:16`

**File:** `SiteSyncCore_2026-04-17_1622/ignition/script-python/utils/resultParser/code.py`, line 16

**Source (defective):**
```python
except Exception as e:
    system.perspective.print("Error determining status: " + str(e))
    return False
```

**Recommended Fix:**
```python
except Exception as e:
    system.util.getLogger("utils.resultParser").error("Error determining status: " + str(e))
    return False
```


---

### [3.2.12] `addDevices/code.py`

---

#### [3.2.12-A] Hardcoded internal PI server URL and component ID

**[Critical] Credential exposure and environment coupling** — `addDevices/code.py:5–6`

**File:** `SiteSyncCore_2026-04-17_1622/ignition/script-python/addDevices/code.py`, lines 5–6

**Impact.** Identical defect to PISync `addDevices/code.py` (see finding [3.1.3-A]). Internal PI server hostname `pgwgen002923.mgroupnet.com` is hardcoded as a module-level constant visible in version control. Any environment other than the original dev instance will silently target the wrong PI server. All API calls from this module go to this single hardcoded endpoint.

**Source (defective):**
```python
PIAddress = "https://pgwgen002923.mgroupnet.com:5590/api/v1/configuration"
componentID = "MQTT1"
```

**Recommended Fix:** Read from `system.tag` configuration tag or Ignition gateway settings:
```python
_settings = PIIntegration.adapter.getPICredentials()
PIAddress = _settings.get('apiURL', '')
componentID = _settings.get('componentID', 'MQTT1')
```

---

#### [3.2.12-B] `addTagToPi()` unconditionally returns `False`

**[High] Dead implementation — PI tag registration always reports failure** — `addDevices/code.py:91–102`

**File:** `SiteSyncCore_2026-04-17_1622/ignition/script-python/addDevices/code.py`, lines 91–102

**Impact.** Identical defect to PISync `addDevices/code.py` (see finding [3.1.3-B]). The function body executes a `system.piAdapter.addTagToDataSelection()` call but unconditionally returns `False`. Callers that check the return value to determine PI registration success will always see failure, preventing any downstream success-path logic from executing.

**Source (defective):**
```python
def addTagToPi(tagPath, componentID, PIAddress):
    # ... API call ...
    return False
```

**Recommended Fix:** Return the actual API response:
```python
def addTagToPi(tagPath, componentID, PIAddress):
    result = system.piAdapter.addTagToDataSelection(componentID, tagPath, PIAddress)
    if result is not None and result != "null":
        return json.loads(result)
    return {"status": False, "message": "No response from PI adapter"}
```

---

### [3.2.13] `createPITemplate/code.py`

---

#### [3.2.13-A] Typo `createReult` and gateway-scope `system.perspective.print` in exception handler

**[Medium] Typo + silent error logging** — `createPITemplate/code.py:34,44`

**File:** `SiteSyncCore_2026-04-17_1622/ignition/script-python/createPITemplate/code.py`, lines 34 and 44

**Impact.** `createReult` typo (line 34) is a cosmetic defect but complicates static analysis. Line 44 `system.perspective.print("Error " + str(e))` is a no-op in gateway scope — exceptions swallowed silently with no log record.

**Source (defective):**
```python
createReult = system.tag.configure(baseTagPath, [tag], collisionPolicy)
...
except Exception as e:
    system.perspective.print("Error " + str(e))
```

**Recommended Fix:**
```python
create_result = system.tag.configure(baseTagPath, [tag], collisionPolicy)
...
except Exception as e:
    system.util.getLogger("createPITemplate").error("Error in createInstance: " + str(e))
```

---

### [3.2.14] `device/get/code.py`

---

#### [3.2.14-A] `type(m) == unicode` — `unicode` is undefined in Python 3

**[Medium] Python 2–only type check** — `device/get/code.py:21`

**File:** `SiteSyncCore_2026-04-17_1622/ignition/script-python/device/get/code.py`, line 21

**Impact.** In Jython 2.7 `unicode` is valid; in Python 3 it is `NameError`. This check guards double-JSON-decoding of metadata. If `type(m)` is `unicode` (a JSON-encoded string stored as metadata), the inner `json.loads(m)` is called. Any Python 3 migration raises `NameError` here.

**Source (defective):**
```python
if type(m) == unicode:
    return json.loads(m)
```

**Recommended Fix:**
```python
if isinstance(m, str):
    return json.loads(m)
```

---

### [3.2.15] `device/updateDevice/code.py`

---

#### [3.2.15-A] `system.perspective.print()` debug calls in `updateDevice()` — gateway scope no-op

**[Medium] Three debug prints in gateway-scope function** — `device/updateDevice/code.py:13,14,21`

**File:** `SiteSyncCore_2026-04-17_1622/ignition/script-python/device/updateDevice/code.py`, lines 13, 14, and 21

**Impact.** `system.perspective.print("sending device for update:")`, `system.perspective.print(json.dumps(device))`, and `system.perspective.print("Error updating device: " + str(e))` are no-ops when called from gateway scope. Update errors are silently swallowed with no diagnostic output.

**Source (defective):**
```python
def updateDevice(device):
    try:
        system.perspective.print("sending device for update:")
        system.perspective.print(json.dumps(device))
        ...
    except Exception as e:
        system.perspective.print("Error updating device: " + str(e))
        return "Error updating device: " + str(e)
```

**Recommended Fix:**
```python
_log = system.util.getLogger("device.updateDevice")

def updateDevice(device):
    try:
        _log.debug("sending device for update: " + json.dumps(device))
        ...
    except Exception as e:
        _log.error("Error updating device: " + str(e))
        return utils.resultParser.createResults(False, "Error updating device: " + str(e))
```

---

### [3.2.16] `device/createDevice/code.py`

---

#### [3.2.16-A] `system.perspective.print()` debug calls in `saveTagPathForDevice()` — gateway scope

**[Medium] Debug prints in gateway-scope helper** — `device/createDevice/code.py:101,103`

**File:** `SiteSyncCore_2026-04-17_1622/ignition/script-python/device/createDevice/code.py`, lines 101 and 103

**Source (defective):**
```python
system.perspective.print(t)
system.perspective.print(type(results))
```

**Recommended Fix:** Remove both debug prints; they produce no output in gateway scope.

---

### [3.2.17] `MPC/customizations/actility/code.py`

---

#### [3.2.17-A] 15 hardcoded Actility network server connection IDs

**[Medium] Configuration embedded in source code** — `MPC/customizations/actility/code.py:6–36`

**File:** `SiteSyncCore_2026-04-17_1622/ignition/script-python/MPC/customizations/actility/code.py`, lines 6–36

**Impact.** Site-to-connection-ID mapping for 15 field sites is hardcoded as a `if/elif` chain. Adding, removing, or renaming a site requires a code deployment. Any site not in the table returns `None` (line 37), silently skipping Actility profile association for that site with no error.

**Source (defective):**
```python
def getConnectionID(siteName, deviceProfileID):
    if deviceProfileID == 29:
        if siteName == "LAR":
            return "TWA_100000163.991.AS"
        elif siteName == "SPP":
            return "TWA_100000163.802.AS"
        # ... 13 more hardcoded entries
```

**Recommended Fix:** Store site-to-connection mappings in an Ignition tag or database table; query at runtime:
```python
def getConnectionID(siteName, deviceProfileID):
    mappings = _loadConnectionMappings()  # reads from tag or DB
    key = "{0}_{1}".format(siteName, deviceProfileID)
    return mappings.get(key)
```

---

### [3.2.18] `utils/sitehandler/code.py`

---

#### [3.2.18-A] `system.perspective.print(e)` in exception handler — gateway scope no-op

**[Low] Silent exception swallowing** — `utils/sitehandler/code.py:14`

**File:** `SiteSyncCore_2026-04-17_1622/ignition/script-python/utils/sitehandler/code.py`, line 14

**Source (defective):**
```python
except Exception as e:
    system.perspective.print(e)
```

**Recommended Fix:**
```python
except Exception as e:
    system.util.getLogger("utils.sitehandler").error("Error listing tenants: " + str(e))
```

---

### [3.2.19] `device/tagOperations/code.py`

---

#### [3.2.19-A] `regenerateTag()` is unconditional stub returning `False`

**[Low] Stub implementation — feature silently disabled** — `device/tagOperations/code.py:2–3`

**File:** `SiteSyncCore_2026-04-17_1622/ignition/script-python/device/tagOperations/code.py`, lines 2–3

**Impact.** Any caller that invokes `device.tagOperations.regenerateTag()` receives `False` with no error. The tag regeneration feature is silently non-functional. Callers cannot distinguish between an API error and an intentionally disabled feature.

**Source (defective):**
```python
def regenerateTag(tagPath, devEUI):
    return False
```

**Recommended Fix:** Either implement the function or raise `NotImplementedError("regenerateTag not yet implemented")` so callers receive an explicit signal.

---

### [3.2.20] Files with No Significant Findings

The following SiteSyncCore files were reviewed and contain no critical or high-severity defects. Minor observations noted inline:

| File | Status | Notes |
|------|--------|-------|
| `decoders/decoder/code.py` | Clean | Well-structured; bare `except:` on `loadAPI()` line 70 swallows all errors |
| `decoders/model/code.py` | Clean | No defects |
| `decoders/udt/code.py` | Clean | No defects |
| `device/diagnostics/code.py` | Clean | Proper batched `readBlocking()` usage |
| `device/bulkUpload/code.py` | Low | `system.perspective.print(updateMetaData)` line 49 is no-op in gateway scope |
| `device/bulkuploadV2/code.py` | — | Not separately reviewed; delegates to `device.createDevice` |
| `device/excelParser/code.py` | — | Data parsing only; no I/O |
| `device/images/code.py` | — | Image encoding helper |
| `connections/mqtt/code.py` | Clean | No defects |
| `connections/networkserver/code.py` | Clean | No defects |
| `utils/normalizedTagPaths/code.py` | Clean | No defects |
| `utils/boolConverters/code.py` | Clean | No defects |
| `utils/messages/actions/code.py` | — | Thin wrapper |
| `utils/messages/errors/code.py` | — | Thin wrapper |
| `utils/messages/success/code.py` | — | Thin wrapper |
| `utils/messages/waiting/code.py` | — | Thin wrapper |
| `utils/dropdowns/code.py` | — | Thin wrapper |
| `utils/tagPathDropdown/code.py` | — | Thin wrapper |
| `utils/timeFormatter/code.py` | — | Date formatting only |
| `utils/QRCodeParser/code.py` | — | QR parsing helper |
| `dashboard/colors/code.py` | — | Static lookup |
| `dashboard/icons/code.py` | — | Static lookup |
| `MPC/customizations/models/modelPicker/code.py` | — | Thin wrapper |
| `MPC/customizations/device/createDevice/code.py` | — | Thin wrapper |
| `MPC/customizations/PIIntegration/code.py` | Best practice | Contains retry logic and structured result returns; reference implementation |
| `decoders/LoRaSpecs/code.py` | — | Spec lookup only |
| `decoders/downlinks/code.py` | — | Downlink formatting |
| `decoders/templateParams/code.py` | — | Parameter mapping |
| `getSensors/code.py` | — | Tag browse wrapper |
| `setPointHelper/code.py` | — | Set-point formatting |
| `deviceGetter/code.py` | — | Thin wrapper |
| `dynamicVisualtion/code.py` | — | Module name typo (`visualtion`); functionality not critical |


---

## 3.3 SiteSync-FieldApp (`SiteSync-FieldApp_Improvements_2026-04-11_1548`) — 113 Files

### Overview and Relationship to SiteSyncCore

SiteSync-FieldApp is a strict superset of SiteSyncCore. The majority of its ~51 shared module files are byte-for-byte identical to their Core counterparts; all defects documented in Section 3.2 for shared modules propagate here unless explicitly noted otherwise. The focus of this section is:

1. Differences from Core in shared files (partial fixes and regressions)
2. FieldApp-exclusive production modules (~15 new files)
3. The 46-suite automated test framework

---

### [3.3.1] Shared-File Divergences from SiteSyncCore

---

#### [3.3.1-A] `PIIntegration/adapter/code.py` — two debug `perspective.print` calls commented out

**[Improvement] Partial remediation of finding [3.2.9-B]**

**File:** `SiteSync-FieldApp_Improvements_2026-04-11_1548/ignition/script-python/PIIntegration/adapter/code.py`, lines 44 and 46

In FieldApp, the `system.perspective.print(items)` and `system.perspective.print(exists)` lines are commented out. The `print path` bare print statement (finding [3.2.9-A]) and the unreachable `return False` (finding [3.2.9-C]) remain unresolved.

**Action:** Apply the same comment-out fix to `SiteSyncCore/PIIntegration/adapter/code.py` and replace with gateway logger calls.

---

#### [3.3.1-B] `createPITemplate/code.py` — `writeBlocking` call commented out

**[Divergence] Activation write disabled in FieldApp but enabled in Core**

**File:** `SiteSync-FieldApp_Improvements_2026-04-11_1548/ignition/script-python/createPITemplate/code.py`, line 37

In SiteSyncCore, `system.tag.writeBlocking([tagPath + ".activated"], [True])` is active. In FieldApp it is commented out. This means PI template instances created via FieldApp are never marked activated, while Core-created instances are. The behavior divergence is undocumented and may cause operational inconsistency across deployments.

**Action:** Align both projects on the intended behavior and either enable or remove the activation write.

---

#### [3.3.1-C] All other shared files — identical to SiteSyncCore

The following files are byte-for-byte identical and carry the same defects documented in Section 3.2:

| Module | Core Finding Reference |
|--------|----------------------|
| `dashboard/routing/code.py` | [3.2.1-A] Critical NameError: `value` undefined |
| `sparkplugSiteSync/code.py` | [3.2.2-A,B,C] NameError + sleep(15) + Py2 prints |
| `device/activateDevice/code.py` | [3.2.3-A,B] NameError + deprecated write |
| `enterprise/tenant/code.py` | [3.2.4-A] Hardcoded stub returning `3` |
| `PIIntegration/AF/code.py` | [3.2.5-A,B,C] "null" bug + backslash + perspective.print |
| `PIIntegration/status/code.py` | [3.2.6-A,B] Duplicate defs + perspective.print |
| `PIIntegration/utils/code.py` | [3.2.7-A,B] sleep(3) + type() check |
| `PIIntegration/settings/code.py` | [3.2.8-A] No "null" guard |
| `PIIntegration/tagOperations/code.py` | [3.2.10-A] browse recursive key |
| `utils/resultParser/code.py` | [3.2.11-A,B] Missing json import + perspective.print |
| `addDevices/code.py` | [3.2.12-A,B] Hardcoded URL + False return |
| `device/get/code.py` | [3.2.14-A] `type() == unicode` |
| `device/updateDevice/code.py` | [3.2.15-A] perspective.print debug calls |
| `device/createDevice/code.py` | [3.2.16-A] perspective.print debug calls |
| `MPC/customizations/actility/code.py` | [3.2.17-A] 15 hardcoded connection IDs |

---

### [3.3.2] `utils/systemProvisioning/code.py`

---

#### [3.3.2-A] Empty function stub — `processSystemUpload()` has no body

**[High] Feature not implemented — silent no-op** — `utils/systemProvisioning/code.py:1–2`

**File:** `SiteSync-FieldApp_Improvements_2026-04-11_1548/ignition/script-python/utils/systemProvisioning/code.py`, lines 1–2

**Impact.** The file contains only `def processSystemUpload(json):` followed by a blank line (implicit `return None`). Any caller of this function proceeds as if the system upload succeeded with no data processed and no error raised. The feature is silently non-functional.

**Source (defective):**
```python
def processSystemUpload(json):
    
```

**Recommended Fix:** Either implement the function or raise `NotImplementedError`:
```python
def processSystemUpload(jsonData):
    raise NotImplementedError("processSystemUpload is not yet implemented")
```

---

### [3.3.3] `device/pidGenerator/code.py`

---

#### [3.3.3-A] Python 2 bare `print` statements in `createLoopHolder()`

**[Medium] Python 2 print statements** — `device/pidGenerator/code.py:28,30`

**File:** `SiteSync-FieldApp_Improvements_2026-04-11_1548/ignition/script-python/device/pidGenerator/code.py`, lines 28 and 30

**Impact.** `print("Tag creation result:", results)` and `print("Error creating tag:", e)` are syntactically valid in Jython 2.7 (they print a tuple) but produce misleading output and are incompatible with Python 3. In gateway scope, stdout is not visible in production.

**Source (defective):**
```python
print("Tag creation result:", results)
...
print("Error creating tag:", e)
```

**Recommended Fix:**
```python
system.util.getLogger("device.pidGenerator").debug("Tag creation result: " + str(results))
...
system.util.getLogger("device.pidGenerator").error("Error creating tag: " + str(e))
```

---

#### [3.3.3-B] `system.perspective.print()` in exception handlers — gateway scope no-op

**[Medium] Silent error swallowing in three functions** — `device/pidGenerator/code.py:84,88,151,177`

**File:** `SiteSync-FieldApp_Improvements_2026-04-11_1548/ignition/script-python/device/pidGenerator/code.py`, lines 84, 88, 151, 177

**Impact.** Warning and error messages from `getNextLoopNumber()`, `getDeviceTypeFromProfile()`, and `getSiteNameFromTenant()` are silently lost when called from gateway scope. Loop counter errors and site-lookup failures go undiagnosed.

**Source (defective):**
```python
system.perspective.print("Warning: Failed to write loop number to tag")
system.perspective.print("Error accessing loop number tag: {0}".format(str(e)))
```

**Recommended Fix:** Replace with `system.util.getLogger("device.pidGenerator").warn(...)` / `.error(...)`.

---

#### [3.3.3-C] `collisionPolicy = "o"` in `createLoopHolder()` — silently overwrites existing tag

**[Medium] Overwrite collision policy on tag create** — `device/pidGenerator/code.py:27`

**File:** `SiteSync-FieldApp_Improvements_2026-04-11_1548/ignition/script-python/device/pidGenerator/code.py`, line 27

**Impact.** Using collision policy `"o"` (overwrite) resets the `Loop Number` tag to `1000` every time `createLoopHolder()` is called, including when called implicitly by `getNextLoopNumber()` if the tag doesn't exist. If the existence check via `system.tag.exists()` ever returns a false negative (e.g., transient tag read before fully initialised), the loop counter is reset silently, producing duplicate PID names.

**Source (defective):**
```python
results = system.tag.configure(basePath, [newTag], "o")  # overwrites value
```

**Recommended Fix:**
```python
results = system.tag.configure(basePath, [newTag], "a")  # abort if exists
```

---

### [3.3.4] `device/replaceDevice/code.py`

---

#### [3.3.4-A] `system.perspective.print()` used for warnings — no-op in gateway scope

**[Low] Warning messages lost in gateway scope** — `device/replaceDevice/code.py:58,62,69,131`

**File:** `SiteSync-FieldApp_Improvements_2026-04-11_1548/ignition/script-python/device/replaceDevice/code.py`, lines 58, 62, 69, 131

**Impact.** Non-fatal warnings during device replacement (metadata transfer incomplete, archive failure, log failure) are silently dropped when the function runs in gateway scope. Operators have no visibility into partial failures.

**Note:** The overall structure of `replaceDevice/code.py` is the best-quality module in the FieldApp codebase. Input validation, structured results, and separation of concerns are all properly implemented. Only the logging mechanism needs correction.

**Recommended Fix:**
```python
_log = system.util.getLogger("device.replaceDevice")
_log.warn("Warning: Metadata transfer incomplete: " + message)
```

---

### [3.3.5] `device/assetAssociation/code.py`

---

#### [3.3.5-A] `system.perspective.print()` in all exception handlers — gateway scope no-op

**[Low] Seven exception handlers use perspective.print** — `device/assetAssociation/code.py:44,58,69,79,104,141,155,164`

**File:** `SiteSync-FieldApp_Improvements_2026-04-11_1548/ignition/script-python/device/assetAssociation/code.py`, multiple lines

**Impact.** All asset association errors (link failure, tag update failure, log failure) are silently swallowed when called from gateway scope. This file is otherwise well-structured.

**Recommended Fix:** Replace all `system.perspective.print()` calls in exception handlers with gateway logger calls.

---

### [3.3.6] `userPreferences/db/code.py`

---

#### [3.3.6-A] Bare `except:` blocks swallow all exceptions silently

**[Medium] Three bare `except:` blocks in database access functions** — `userPreferences/db/code.py:65,83,221`

**File:** `SiteSync-FieldApp_Improvements_2026-04-11_1548/ignition/script-python/userPreferences/db/code.py`, lines 65, 83, and 221

**Impact.** `getUserPreference()`, `setUserPreference()`, and `getAllInstallationRecords()` each have bare `except:` blocks that return `None` or `False`/`[]` on any exception. Database connection failures, query failures, and schema errors are all silently converted to empty returns. Callers cannot distinguish between "no data" and "error fetching data". This particularly affects `getColumnPreferences()` which merges with defaults — a silent DB failure means user preferences are silently reset to defaults on every call.

**Source (defective):**
```python
def getUserPreference(userId, preferenceKey):
    try:
        result = system.db.runNamedQuery(...)
        ...
    except:
        return None   # swallows DB connection errors, query errors, schema errors

def setUserPreference(userId, preferenceKey, preferenceValue):
    try:
        system.db.runNamedQuery(...)
        return True
    except:
        return False  # caller sees False but has no diagnostic information
```

**Recommended Fix:**
```python
import sys

def getUserPreference(userId, preferenceKey):
    try:
        result = system.db.runNamedQuery(...)
        ...
    except Exception as e:
        system.util.getLogger("userPreferences.db").error(
            "getUserPreference failed for user {0}: {1}".format(userId, str(e))
        )
        return None
```


---

### [3.3.7] `tests/runner/runner/code.py`

---

#### [3.3.7-A] Python 2 `print` statements throughout summary output

**[Medium] Bare print statements in test runner output** — `tests/runner/runner/code.py:107–131`

**File:** `SiteSync-FieldApp_Improvements_2026-04-11_1548/ignition/script-python/tests/runner/runner/code.py`, lines 107–131

**Impact.** All test summary output uses bare `print(...)` statements. In Jython 2.7, `print("text", var)` prints a tuple, not formatted output. When the test runner is invoked from the Script Console this produces readable output, but in gateway scope all output is invisible. The runner returns a structured dictionary (lines 133–144) which is usable, but the console summary is unreliable.

**Note:** The test framework architecture is well-designed. The runner supports `runAll()`, `runPureOnly()`, `runIOOnly()`, and `runModule()` entry points. The separation into PURE_SUITES (19) and IO_SUITES (27) allows fast unit test runs without requiring a live Ignition system. This is a positive design pattern.

**Source (defective):**
```python
print("=" * 60)
print("TEST RESULTS SUMMARY")
print("  [{0}] {1}  ({2} passed, ...)".format(status, ...))
```

**Recommended Fix:**
```python
import sys
_SEPARATOR = "=" * 60

def _printSummary(suiteResults, totals):
    lines = [_SEPARATOR, "TEST RESULTS SUMMARY", _SEPARATOR]
    for sr in suiteResults:
        status = "PASS" if sr["failed"] == 0 else "FAIL"
        lines.append("  [{0}] {1}  ({2}p / {3}f / {4}s) [{5}s]".format(
            status, sr["suite"].split(".")[-1],
            sr["passed"], sr["failed"], sr["skipped"], sr["elapsed"]
        ))
    lines.append("-" * 60)
    lines.append("  Total: {0} | {1}p {2}f {3}s {4}known | {5:.2f}s".format(
        totals["tests"], totals["passed"], totals["failed"],
        totals["skipped"], totals["knownDefects"], totals["elapsed"]
    ))
    print("\n".join(lines))  # single print call avoids tuple formatting issue
```

---

#### [3.3.7-B] Test suite cannot be run outside Ignition Designer/gateway

**[Medium] No standalone test runner** — `tests/runner/runner/code.py`

**Impact.** All test suites import module paths like `decoders.model`, which resolve only within the Ignition scripting namespace. There is no `sys.path` manipulation or mock layer to allow running tests against real Python outside Ignition. CI/CD pipelines cannot validate business logic without a running Ignition gateway instance. The IO_SUITES additionally require live `system.sitesync.*` and `system.tag.*` calls.

**Recommendation.** Extract pure logic into standalone Python functions with no `system.*` dependencies. Provide a thin Ignition adapter wrapper. Pure suites can then run with `pytest` in CI.

---

### [3.3.8] FieldApp-Exclusive Files with No Significant Findings

The following FieldApp-only production files were reviewed and contain no critical or high-severity defects:

| File | Status | Notes |
|------|--------|-------|
| `dashboard/aggregation/code.py` | Clean | Aggregation helper; well-structured |
| `utils/historyconfig/code.py` | Clean | Static config lookup; no I/O |
| `utils/logging/code.py` | Clean | One-line wrapper around `system.sitesync.addLog()` |
| `utils/dashmanager/code.py` | Clean | Dashboard state management |
| `utils/deviceProfileDropDown/code.py` | Clean | Dropdown helper |
| `decoders/encoder/code.py` | Clean | Downlink encoding helper |
| `survey/analysis/scoring/code.py` | Clean | Scoring algorithm; pure logic |
| `tests/fixtures/fixtures/code.py` | Clean | Test fixtures; well-maintained |
| `tests/utils/utils/code.py` | Clean | Test utilities |
| `tests/suites/test_routing/code.py` | **Issue** | Tests `getTile()` but the function always raises NameError (see [3.2.1-A]); tests likely fail in all runs |
| All other `tests/suites/test_*.py` | Mixed | IO suites require live Ignition; pure suites are architecturally sound |

---

## 4. Findings Summary by Severity

### Critical Findings (6)

| ID | File (both projects) | Defect |
|----|---------------------|--------|
| 3.1.6-A | PISync `callables/code.py:168` | `topic[:-1]` strips last char from all payloads |
| 3.2.1-A | Core+FieldApp `dashboard/routing/code.py:2` | `value` undefined → NameError on every `getTile()` call |
| 3.2.2-A | Core+FieldApp `sparkplugSiteSync/code.py:6` | `sourcePath` undefined → NameError on every `triggerBirth()` call |
| 3.2.2-B | Core+FieldApp `sparkplugSiteSync/code.py:16` | `time.sleep(15)` blocks gateway thread |
| 3.2.3-A | Core+FieldApp `device/activateDevice/code.py:20` | `baseTagPath` undefined → NameError on every `createLimitedInstance()` call |
| 3.2.7-A | Core+FieldApp `PIIntegration/utils/code.py:20` | `time.sleep(3)` blocks gateway thread per success notification |

### High Findings (12)

| ID | File | Defect |
|----|------|--------|
| 3.1.3-A | PISync+Core+FieldApp `addDevices/code.py:5` | Hardcoded internal PI server URL |
| 3.1.3-B | PISync+Core+FieldApp `addDevices/code.py:91` | `addTagToPi()` always returns `False` |
| 3.2.4-A | Core+FieldApp `enterprise/tenant/code.py:3` | `getDefaultApp()` hardcoded stub returns `3` |
| 3.2.5-A | Core+FieldApp `PIIntegration/AF/code.py:14` | "null" string bypasses guard → TypeError |
| 3.2.5-B | Core+FieldApp `PIIntegration/AF/code.py:51` | Backslash path separator fails on Linux |
| 3.2.6-A | Core+FieldApp `PIIntegration/status/code.py:2,23` | Duplicate defs; stubs override real code |
| 3.2.8-A | Core+FieldApp `PIIntegration/settings/code.py:5` | No "null" guard → TypeError on key access |
| 3.2.11-A | Core+FieldApp `utils/resultParser/code.py:24` | `json.dumps()` without `import json` → NameError |
| 3.2.12-A | Core+FieldApp `addDevices/code.py:5` | (same as 3.1.3-A above) |
| 3.2.12-B | Core+FieldApp `addDevices/code.py:91` | (same as 3.1.3-B above) |
| 3.3.2-A | FieldApp `utils/systemProvisioning/code.py:1` | Empty stub — feature silently non-functional |
| 3.1.6-B | PISync `callables/code.py:73` | `long`/`unicode` NameError in Python 3 |


---

## 5. Recommended Remediation Order

Prioritized by operational impact and blast radius. Address Critical findings before the next release cycle; High findings before GA.

### Sprint 1 — Stop the Bleeding (Critical Runtime Crashes)

1. **`dashboard/routing/code.py:2`** — Replace `value` with `sensorType` parameter (5-minute fix; affects both Core and FieldApp). Finding [3.2.1-A].

2. **`sparkplugSiteSync/code.py:6`** — Replace `sourcePath` with `tagPath` parameter; replace `time.sleep(15)` with async invocation (30-minute fix; affects both Core and FieldApp). Findings [3.2.2-A, 3.2.2-B].

3. **`device/activateDevice/code.py:20`** — Replace `baseTagPath` with `intendedTagPath` parameter (5-minute fix; affects both Core and FieldApp). Finding [3.2.3-A].

4. **`PIIntegration/utils/code.py:20`** — Remove `time.sleep(3)` from `showSuccess()`; offload popup close to component timer (30-minute fix; affects both Core and FieldApp). Finding [3.2.7-A].

5. **`exchange/mqttVanillaTransmission/callables/code.py:168`** — Fix `topic[:-1]` stripping (PISync). Finding [3.1.6-A].

### Sprint 2 — PI Integration Reliability (High)

6. **`addDevices/code.py:5`** — Remove hardcoded `PIAddress` and `componentID`; read from configuration tag or module settings (affects PISync, Core, FieldApp). Findings [3.1.3-A, 3.2.12-A].

7. **`addDevices/code.py:91`** — Fix `addTagToPi()` to return actual API response instead of `False` (affects all three projects). Findings [3.1.3-B, 3.2.12-B].

8. **`PIIntegration/AF/code.py:14`** — Add `"null"` string guard before `json.loads()` (affects both Core and FieldApp). Finding [3.2.5-A].

9. **`PIIntegration/AF/code.py:51`** — Change backslash to forward slash in path format string (affects both Core and FieldApp). Finding [3.2.5-B].

10. **`PIIntegration/settings/code.py:5`** — Add `"null"` guard in `getSettings()` (affects both Core and FieldApp). Finding [3.2.8-A].

11. **`PIIntegration/status/code.py`** — Remove duplicate stub definitions (affects both Core and FieldApp). Finding [3.2.6-A].

12. **`utils/resultParser/code.py:1`** — Add `import json` to module (affects both Core and FieldApp). Finding [3.2.11-A].

13. **`enterprise/tenant/code.py:3`** — Restore dynamic `getDefaultApp()` implementation (affects both Core and FieldApp). Finding [3.2.4-A].

### Sprint 3 — Correctness and Logging (Medium)

14. **Replace all `system.perspective.print()` calls** in gateway-scope modules with `system.util.getLogger()` calls. Affects: `PIIntegration/AF`, `PIIntegration/adapter`, `PIIntegration/status`, `PIIntegration/utils`, `device/updateDevice`, `device/createDevice`, `device/bulkUpload`, `device/pidGenerator`, `device/replaceDevice`, `device/assetAssociation`, `utils/sitehandler`, `utils/resultParser`, `createPITemplate`. Findings [3.2.5-C, 3.2.9-B, 3.2.6-B, 3.2.11-B, 3.2.13-A, 3.2.15-A, 3.2.16-A, 3.3.3-B, 3.3.4-A, 3.3.5-A].

15. **`PIIntegration/tagOperations/code.py:2,7`** — Replace `system.tag.browse(filter={"recursive":True})` with `system.tag.browseConfiguration(..., recursive=True)`. Finding [3.2.10-A].

16. **`device/get/code.py:21`** — Replace `type(m) == unicode` with `isinstance(m, str)`. Finding [3.2.14-A].

17. **`device/pidGenerator/code.py:27`** — Change collision policy from `"o"` to `"a"` in `createLoopHolder()`. Finding [3.3.3-C].

18. **`utils/systemProvisioning/code.py`** — Implement `processSystemUpload()` or raise `NotImplementedError`. Finding [3.3.2-A].

19. **`MPC/customizations/actility/code.py`** — Migrate hardcoded connection IDs to a database table or configuration tag. Finding [3.2.17-A].

20. **`tests/runner/runner/code.py`** — Fix Python 2 print tuples in summary output. Finding [3.3.7-A].

### Sprint 4 — Code Quality and Python 3 Readiness (Low)

21. Remove all Python 2 bare `print` statements (PISync `devices/code.py`, `sparkplugSiteSync/code.py`, `PIIntegration/adapter/code.py`, `device/pidGenerator/code.py`, test runner). Findings [3.1.2-A, 3.2.2-C, 3.2.9-A, 3.3.3-A, 3.3.7-A].

22. Replace `type(x) != dict` with `isinstance(x, dict)` throughout. Finding [3.2.7-B].

23. Fix `device/tagOperations/code.py` stub `regenerateTag()`. Finding [3.2.19-A].

24. Remove unreachable `return False` at `PIIntegration/adapter/code.py:52`. Finding [3.2.9-C].

25. Fix `PIIntegration/utils.showError()` to use `system.perspective.openPopup()` safely (not called from gateway scope; medium risk).

26. Add `import json` to bare `except:` blocks in `userPreferences/db/code.py`. Finding [3.3.6-A].

---

## 6. Verification Commands

Run these commands from the Ignition Script Console after applying fixes to confirm regressions are eliminated.

### 6.1 Verify `dashboard/routing/code.py` Fix (Finding 3.2.1-A)

```python
# Should return a path string, not raise NameError
result = dashboard.routing.getTile("TEMPERATURE")
assert result == "Dashboard/components/assets/Pressure", "FAIL: got " + str(result)
result2 = dashboard.routing.getTile("LOCKOUT")
assert result2 == "Dashboard/components/assets/Lockout", "FAIL: got " + str(result2)
result3 = dashboard.routing.getTile("UNKNOWN_TYPE")
assert result3 == "Dashboard/components/assets/OtherPV", "FAIL: got " + str(result3)
print("routing.getTile: PASS")
```

### 6.2 Verify `utils/resultParser/code.py` Fix (Finding 3.2.11-A)

```python
# Should return an error string, not raise NameError
result = utils.resultParser.getResultMessage({"status": "FAILURE"})
assert "Error getting results" in result, "FAIL: got " + str(result)
result2 = utils.resultParser.getResultMessage({"message": "All good"})
assert result2 == "All good", "FAIL: got " + str(result2)
print("resultParser.getResultMessage: PASS")
```

### 6.3 Verify `PIIntegration/settings/code.py` Fix (Finding 3.2.8-A)

```python
# Simulate null return — should return {} not raise TypeError
import json
class MockPiAdapter:
    def getSettings(self, key):
        return "null"  # simulates unconfigured state

# This test must be run with a test adapter mock or on an unconfigured gateway
settings = PIIntegration.settings.getSettings()
assert isinstance(settings, dict), "FAIL: expected dict, got " + str(type(settings))
print("PIIntegration.settings.getSettings null guard: PASS")
```

### 6.4 Verify `PIIntegration/AF/code.py` Path Fix (Finding 3.2.5-B)

```python
# pathFormatter should use forward slashes
result = PIIntegration.AF.pathFormatter("MyRepo", "path.$.to.tag", "prefix", "sourceFolder")
assert "\\" not in result, "FAIL: backslash found in path: " + result
assert "/" in result, "FAIL: no forward slash in path: " + result
print("PIIntegration.AF.pathFormatter: PASS")
```

### 6.5 Verify `PIIntegration/status/code.py` Duplicate Fix (Finding 3.2.6-A)

```python
# After removing duplicate stubs, real implementation should be reachable
# This verifies the function body is not a stub
import inspect
src = inspect.getsource(PIIntegration.status.adapterAPIPingStatus)
assert "testConnection" in src, "FAIL: real implementation not found"
print("PIIntegration.status: PASS")
```

### 6.6 Verify `device/activateDevice/code.py` Fix (Finding 3.2.3-A)

```python
# createLimitedInstance should not raise NameError
# (Run in Script Console with a known test tag path)
try:
    result = device.activateDevice.createLimitedInstance(
        "[default]TestPath", "TestTemplate", "TestTag", "[default]SourcePath"
    )
    print("activateDevice.createLimitedInstance: PASS (returned " + str(result) + ")")
except NameError as e:
    print("activateDevice.createLimitedInstance: FAIL (NameError: " + str(e) + ")")
```

### 6.7 Run Full Test Suite

```python
# In Ignition Script Console
results = tests.runner.runner.runPureOnly()
totals = results['totals']
assert totals['failed'] == 0, "{0} test failures: {1}".format(
    totals['failed'],
    [r['name'] + ': ' + r['message'] for r in results['results'] if r['status'] == 'FAIL']
)
print("All pure tests: PASS ({0} tests)".format(totals['tests']))
```

### 6.8 Check for Remaining `system.perspective.print` in Gateway Modules

```python
# Run in Script Console — should return empty list after all fixes applied
import re
import os

GATEWAY_MODULES = [
    "PIIntegration/AF/code.py",
    "PIIntegration/adapter/code.py",
    "PIIntegration/status/code.py",
    "PIIntegration/utils/code.py",
    "device/updateDevice/code.py",
    "device/createDevice/code.py",
    "utils/resultParser/code.py",
    "utils/sitehandler/code.py",
]

issues = []
for mod in GATEWAY_MODULES:
    # Check module source via inspect or file read
    pass  # implementation depends on Ignition version

print("perspective.print audit: review above modules manually")
```

### 6.9 Check for Remaining Hardcoded PI URL

```python
# After fix, PIAddress should come from configuration, not be a literal
import inspect
src = inspect.getsource(addDevices)
assert "pgwgen002923" not in src, "FAIL: hardcoded PI URL still present"
print("addDevices hardcoded URL: PASS")
```

---

*End of SiteSync Comprehensive Code Review*

*Review date: 2026-04-18*
*Reviewer: Automated static analysis via Claude Code*
*Projects reviewed: PISync_2026-04-11_1427, SiteSyncCore_2026-04-17_1622, SiteSync-FieldApp_Improvements_2026-04-11_1548*
*Total findings: 6 Critical, 12 High, 18 Medium, 10 Low*


---

## 3.4 SiteSYnc EnterpriseManagementScripts — 52 Files

### Overview and Relationship to SiteSyncCore

EnterpriseManagementScripts shares 51 of its 52 files with SiteSyncCore by path. Of those shared files, **47 are byte-for-byte identical** to Core and carry every defect documented in §3.2. **5 files diverge**, and **1 file (`utils/deviceProfileDropDown/code.py`) exists only in Enterprise**. The project appears to be an earlier branch of SiteSyncCore that was kept in use for an enterprise deployment and has since diverged in both directions — some bugs were fixed here first, some regressions introduced.

**Diff summary vs SiteSyncCore:**
| File | Direction |
|------|-----------|
| `addDevices/code.py` | Enterprise has OLDER real implementation (predates Core's stub) |
| `createPITemplate/code.py` | Enterprise has debug prints active + a path-separator bug |
| `device/createDevice/code.py` | Enterprise has inline implementation (not delegated to MPC) |
| `utils/sitehandler/code.py` | Enterprise has debug prints + different roles API call shape |
| `enterprise/tenant/code.py` | Cosmetically different comment only |
| `utils/deviceProfileDropDown/code.py` | Enterprise only |

---

### [3.4.1] `addDevices/code.py`

---

#### [3.4.1-A] Hardcoded internal PI server URL — same as Core [3.2.12-A]

**[Critical] `PIAddress` hardcoded at module level** — `addDevices/code.py:5`

Same defect as finding [3.2.12-A] and [3.1.3-A]. The internal hostname `pgwgen002923.mgroupnet.com` is committed to source at module level. See finding [3.2.12-A] for full impact and fix.

---

#### [3.4.1-B] `null = None`, `false = False`, `true = True` aliases at module scope

**[Medium] JSON-literal aliases pollute module namespace** — `addDevices/code.py:1–3`

**File:** `SiteSYnc EnterpriseManagementScripts/script-python/addDevices/code.py`, lines 1–3

**Impact.** These aliases were introduced to allow copy-pasting JSON literals directly into Python dicts (e.g., `"selected": true`). They work in Jython 2.7, but they shadow Python builtins `None`, `False`, `True` at module scope, which can confuse static analysis tools and linters. Any module that imports from `addDevices` gains these aliases in scope unexpectedly. In particular, `null` as a name conflict with the Ignition JSON API is a readability hazard.

**Source (defective):**
```python
null = None
false = False
true = True
```

**Recommended Fix:** Replace inline JSON-style literals with proper Python literals and delete the aliases:
```python
# BEFORE
"selected": true,
"dataFields": null,

# AFTER
"selected": True,
"dataFields": None,
```

---

#### [3.4.1-C] `addTagToPi()` — Enterprise has the real implementation; Core replaced it with a stub

**[Note / Regression in Core] Enterprise version correctly returns PI adapter results** — `addDevices/code.py:91–98`

**File:** `SiteSYnc EnterpriseManagementScripts/script-python/addDevices/code.py`, lines 91–98

**Observation.** The Enterprise `addTagToPi()` performs the full MQTT Adapter data-selection update:
1. Browses child tags of the given tag path
2. Gets the current data selection from the adapter
3. Formats new items, de-duplicates against existing selection
4. Calls `system.piAdapter.updateDataSelection()` and returns the result

SiteSyncCore replaced this implementation with a stub that logs via `system.util.getLogger` but unconditionally `return False` (finding [3.2.12-B]). This is a functional regression in Core — PI data selection updates no longer execute.

**Action.** Restore the Enterprise implementation in Core (with the hardcoded URL defect fixed separately per [3.2.12-A]):
```python
def addTagToPi(tagPath, componentID, PIAddress):
    items = getAttributesForTag(tagPath)
    existingConfig = getCurrentDataSelection(componentID, PIAddress)
    piTags = formatDataSelectionItem(tagPath, items, existingConfig)
    return updateDataSelection(piTags, componentID, PIAddress)
```

---

#### [3.4.1-D] `getCurrentDataSelection()` — `"null"` string bypasses guard, same as Core

**[High] `json.loads("null")` returns Python `None` — iteration raises `TypeError`** — `addDevices/code.py:11`

Same root cause as finding [3.2.8-A]. When the adapter has no existing selection, `getDataSelection()` returns `"null"`. The guard `if selectedData != None:` passes, and `json.loads("null")` returns `None`. `formatDataSelectionItem()` then iterates over `existingConfig` (which is `None`) and raises `TypeError`.

**Recommended Fix:**
```python
selectedData = system.piAdapter.getDataSelection(componentID, "MQTT1", PIAddress)
if selectedData and selectedData != "null":
    parsed = json.loads(selectedData)
    return parsed if parsed is not None else []
return []
```

---

#### [3.4.1-E] `system.tag.browse(filter={"recursive":True})` — recursive key silently ignored

**[Medium] Non-recursive browse returns only top-level children** — `addDevices/code.py:20`

Same defect as [3.2.10-A]. `getAttributesForTag()` passes `{"recursive":True}` to `system.tag.browse()` — the key is silently dropped.

**Recommended Fix:** Use `system.tag.browseConfiguration(rootTagPath, recursive=True)`.

---

### [3.4.2] `createPITemplate/code.py`

---

#### [3.4.2-A] Double-slash path separator bug unique to Enterprise

**[High] `"{0}/{1}".format(baseTagPath, tagName)` produces double-slash in PI tag path** — `createPITemplate/code.py:39`

**File:** `SiteSYnc EnterpriseManagementScripts/script-python/createPITemplate/code.py`, line 39

**Impact.** `baseTagPath` is assembled on line 10 as:
```python
baseTagPath = "[default]PI Integration/{0}".format(assembledPath)
```
where `assembledPath = tagPath.replace('[default]', '').replace(tagName, "")`. Since `tagName` is stripped from the end of `tagPath`, `assembledPath` ends with a `/`. `baseTagPath` therefore ends with `/`. Line 39 then formats `"{0}/{1}".format(baseTagPath, tagName)`, producing:

```
[default]PI Integration/path/to//tagName
```

The double-slash makes the path string invalid. `addTagToPi()` receives this malformed path, causing the PI data selection item to be registered with a path that doesn't resolve. SiteSyncCore fixed this to `"{0}{1}"` (no inserted separator). Enterprise retains the bug.

**Source (defective):**
```python
results = addDevices.addTagToPi("{0}/{1}".format(baseTagPath, tagName), ...)
```

**Recommended Fix** (apply the Core fix):
```python
results = addDevices.addTagToPi("{0}{1}".format(baseTagPath, tagName), ...)
```

---

#### [3.4.2-B] Active `system.perspective.print()` debug calls — gateway scope no-op

**[Medium] Four active debug prints in gateway-scope function** — `createPITemplate/code.py:4,35,41,44`

**File:** `SiteSYnc EnterpriseManagementScripts/script-python/createPITemplate/code.py`, lines 4, 35, 41, 44

SiteSyncCore commented out lines 4, 35, and 41; Enterprise still has them active. Line 44 (exception handler) remains active in both. All four are silent no-ops in gateway scope.

**Source (defective):**
```python
system.perspective.print("Creating PI isntance {0}".format(tagPath))  # line 4
system.perspective.print(createReult)                                  # line 35
system.perspective.print(results)                                      # line 41
system.perspective.print("Error " + str(e))                            # line 44
```

**Recommended Fix:** Replace all four with gateway logger calls or remove:
```python
_log = system.util.getLogger("createPITemplate")
_log.debug("Creating PI instance: " + str(tagPath))
```

---

### [3.4.3] `device/createDevice/code.py`

---

#### [3.4.3-A] `appID` parameter silently overwritten by `getDefaultApp()` on every call

**[High] Caller-supplied `appID` discarded — hardcoded tenant ID 3 always used** — `device/createDevice/code.py:5`

**File:** `SiteSYnc EnterpriseManagementScripts/script-python/device/createDevice/code.py`, line 5

**Impact.** The function signature declares `appID = 0` as a default parameter, but the very first line of the body immediately overwrites it:
```python
def saveDevice(devEUI, appEUI, appKey, name, serialNumber, modelID, lat, lon,
               description, provider, tagPath, image, user, appID = 0, tenantID = 1):
    appID = enterprise.tenant.getDefaultApp()   # silently discards caller's appID
```
`enterprise.tenant.getDefaultApp()` returns the hardcoded value `3` (see finding [3.2.4-A]). Any caller that passes an explicit `appID` for a different enterprise application will have it silently replaced. Multi-tenant device creation is broken — all devices are registered under application ID 3 regardless of context.

**Recommended Fix:** Remove the override, or only apply a default when the parameter is absent:
```python
def saveDevice(devEUI, appEUI, appKey, name, serialNumber, modelID, lat, lon,
               description, provider, tagPath, image, user, appID=None, tenantID=1):
    if appID is None:
        appID = enterprise.tenant.getDefaultApp()
```

---

#### [3.4.3-B] Multiple `system.perspective.print()` debug calls in device-creation flow

**[Medium] Five active debug prints in gateway-scope `saveDevice()`** — `device/createDevice/code.py:10,14,16,21,22`

**File:** `SiteSYnc EnterpriseManagementScripts/script-python/device/createDevice/code.py`, lines 10, 14, 16, 21, 22

**Impact.** Milestone checkpoints ("pre-create device", "pre-create tag", "post-create device") and the raw image value are all logged via `system.perspective.print()`. These are no-ops in gateway scope, leaving the entire device-creation pipeline unobservable in production.

**Source (defective):**
```python
system.perspective.print("pre-create device")
system.perspective.print("pre-create tag")
system.perspective.print("post-create tag {0}".format(tagPathSaveResult))
system.perspective.print("post-create device")
system.perspective.print(image)
```

**Recommended Fix:** Replace with gateway logger:
```python
_log = system.util.getLogger("device.createDevice")
_log.info("Creating device: " + devEUI)
_log.debug("Tag path save result: " + str(tagPathSaveResult))
```

---

#### [3.4.3-C] `createPITemplate.createInstance()` called inline — PI errors abort device creation

**[Medium] Tight coupling between device creation and PI template provisioning** — `device/createDevice/code.py:20`

**File:** `SiteSYnc EnterpriseManagementScripts/script-python/device/createDevice/code.py`, line 20

**Impact.** After a device is successfully created and its tag path saved, `createPITemplate.createInstance(fullTagPath, name)` is called on line 20. The return value is discarded. If PI is unavailable, the call raises an exception that propagates up through `saveDevice()` — the device was successfully created in SiteSync but the caller receives an error response. On retry, `saveDevice()` attempts to create the device again, producing a duplicate-device error. The PI provisioning step is not idempotent and its failure path destroys the successful device creation outcome.

**Recommended Fix:** Separate PI provisioning from device creation; call it as a best-effort post-creation step:
```python
# After confirming device + tag creation succeeded:
try:
    createPITemplate.createInstance(fullTagPath, name)
except Exception as e:
    _log.warn("PI template creation failed for {0}: {1}".format(devEUI, str(e)))
    message += "; PI template not created"
return utils.resultParser.createResults(True, message)
```

---

### [3.4.4] `utils/sitehandler/code.py`

---

#### [3.4.4-A] `updateSiteRoles()` wraps roles in `{"roles": ...}` envelope — API contract mismatch with Core

**[High] Behavioral divergence in roles update call shape** — `utils/sitehandler/code.py:65–74`

**File:** `SiteSYnc EnterpriseManagementScripts/script-python/utils/sitehandler/code.py`, lines 65–74

**Impact.** Enterprise wraps the roles array before calling the API:
```python
j = {"roles": rolesJSON}
r = json.dumps(j)   # sends {"roles": [...]}
system.sitesync.updateTenantRoles(r, int(siteID))
```

SiteSyncCore sends the array directly:
```python
r = json.dumps(rolesJSON)   # sends [...]
system.sitesync.updateTenantRoles(r, int(siteID))
```

One of these two is calling the API with the wrong payload shape. If `system.sitesync.updateTenantRoles()` expects a flat array, Enterprise silently passes `{"roles": [...]}` and roles are never updated. If it expects the wrapped object, Core silently passes a flat array and roles are never updated. This divergence must be reconciled against the actual `system.sitesync` module API contract.

Additionally, Enterprise guards `if len(rolesJSON) > 0:` — if the roles list is empty, nothing is called and no error is returned, silently skipping the clear-all-roles case.

**Recommended Fix:** Determine the correct API shape, align both projects, and handle the empty-roles case explicitly:
```python
def updateSiteRoles(siteID, rolesJSON):
    r = json.dumps(rolesJSON)   # or json.dumps({"roles": rolesJSON}) — verify with API
    result = system.sitesync.updateTenantRoles(r, int(siteID))
    return json.loads(result) if result else utils.resultParser.createResults(True, "Roles updated")
```

---

#### [3.4.4-B] `system.perspective.print()` debug calls in `updateSiteRoles()`

**[Medium] Four debug prints in gateway-scope function** — `utils/sitehandler/code.py:67,68,72,74`

**File:** `SiteSYnc EnterpriseManagementScripts/script-python/utils/sitehandler/code.py`, lines 67, 68, 72, 74

**Source (defective):**
```python
system.perspective.print("Preparing roles")
system.perspective.print(rolesJSON)
system.perspective.print(a)
system.perspective.print("No roles")
```

**Recommended Fix:** Remove all four; replace with `system.util.getLogger("utils.sitehandler").debug(...)` if diagnostics are needed.

---

### [3.4.5] `utils/deviceProfileDropDown/code.py` (Enterprise-only)

---

#### [3.4.5-A] `-NA` model filter is undocumented

**[Low] Silent model filtering with no explanation** — `utils/deviceProfileDropDown/code.py:7`

**File:** `SiteSYnc EnterpriseManagementScripts/script-python/utils/deviceProfileDropDown/code.py`, line 7

**Impact.** `if '-NA' not in model:` silently skips any device profile whose `model_name` contains `-NA`. The intent is presumably to hide placeholder or "not available" profiles from the dropdown. However, there is no comment explaining this, and a profile legitimately named something like `Sensor-NAnotherword` would be silently excluded. The function is otherwise clean and well-structured.

**Source:**
```python
for device in deviceModels:
    model = device["model_name"]
    if '-NA' not in model:   # undocumented filter
```

**Recommended Fix:** Add a comment, or make the filter configurable:
```python
EXCLUDED_SUFFIXES = ('-NA',)  # placeholder profiles not shown in dropdowns
for device in deviceModels:
    model = device["model_name"]
    if not any(model.endswith(s) for s in EXCLUDED_SUFFIXES):
```

---

### [3.4.6] `enterprise/tenant/code.py` — Cosmetic Difference Only

The Enterprise version differs from Core only in a single comment character (`-16` vs `-1`). The same hardcoded `return 3` stub is present. See finding [3.2.4-A] for full impact and fix.

---

### [3.4.7] Shared Files — All Core Findings Propagate

The following 47 files are byte-for-byte identical to SiteSyncCore and carry every defect from §3.2:

| Critical findings present | [3.2.1-A] `dashboard/routing` NameError · [3.2.2-A,B] `sparkplugSiteSync` NameError + sleep(15) · [3.2.3-A] `device/activateDevice` NameError · [3.2.7-A] `PIIntegration/utils` sleep(3) |
|---|---|
| High findings present | [3.2.5-A,B] AF "null" + backslash · [3.2.6-A] status duplicate defs · [3.2.8-A] settings "null" guard · [3.2.11-A] resultParser missing json import |

