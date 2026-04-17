# SiteSync Ignition Jython 2.7 Code Review

**Scope:** five `script-python` folders in this repo, totalling ~230 Python files.
**Runtime:** Ignition Jython 2.7 (JVM-hosted Python 2.7 dialect).
**Method:** direct file reads + folder-level `diff -rq`. No code in the reviewed
folders was modified. Every finding includes a `path:line` reference and, where
applicable, a before/after diff block the reader can adopt.

---

## 1. Executive Summary

| Severity     | Count | What it means                                                                        |
|--------------|------:|--------------------------------------------------------------------------------------|
| Critical     |    11 | Latent runtime bug, broken API call, or security/credential issue                    |
| High         |    18 | Jython-2.7-only syntax that breaks under Py3, fragile/swallowed error handling       |
| Medium       |    15 | Performance red flag, logging inconsistency, large stale duplicate folders           |
| Low          |    12 | Dead code, typos, commented-out blocks, style                                        |

**Top five risks, in order:**

1. `PISync_2026-04-11_1427/.../PIIntegration/activate/code.py:6-10` — `replaceNull()`
   returns `0` in **both** branches. Null replacement is effectively a constant.
2. `PI_Integration_Manager_2026-04-17_1632/.../adapter/code.py:59` — `removeFromDataSelection`
   calls `system.piAdapter.createDataSelection` (wrong API) with a bad signature.
   Removal silently performs an unrelated create.
3. `PI_Integration_Manager_2026-04-17_1632/.../status/code.py:1-28` — duplicate
   function definitions: stubs defined first, real implementations later, causing
   confusion and inviting the wrong version to be called if the file is ever split.
4. `PISync_2026-04-11_1427/.../addDevices/code.py:5-6` and
   `SiteSyncCore_2026-04-17_1622/.../addDevices/code.py:5-6` — a public HTTPS
   endpoint (`https://pgwgen002923.mgroupnet.com:5590/...`) and MQTT component
   id are hard-coded as module globals. Environment-specific config belongs in
   gateway system properties / named queries, not the git-tracked module.
5. `SiteSync-FieldApp_Improvements/.../connections/{mqtt,networkserver}/code.py` and
   `.../decoders/decoder/code.py:50-64` — secrets (MQTT passwords, join-server
   passwords, API tokens, API passwords) are hand-marshalled into JSON blobs and
   passed verbatim to `system.sitesync.*`. Audit that the backend stores them
   encrypted and that these calls don't appear in Ignition audit/perspective logs.

**Cross-cutting finding:** the repo contains three near-duplicate copies of the
SiteSync script tree (`SiteSYnc EnterpriseManagementScripts`, `SiteSyncCore_2026-04-17_1622`,
`SiteSync-FieldApp_Improvements_2026-04-11_1548`). FieldApp is the newest and
only fully-tested copy; the other two drift behind and will accumulate silent
bugfix/regression gaps. Pick one canonical tree and delete the rest from source
control (or clearly mark them read-only snapshots).

---

## 2. Cross-Cutting Findings

### 2.1 Folder duplication / stale copies

`diff -rq` results (see Verification section for commands):

- **Enterprise vs FieldApp**: 15 files differ + 13 orphan trees exist **only**
  in FieldApp (`tests/`, `survey/`, `userPreferences/`, `dashboard/aggregation/`,
  `decoders/encoder/`, `device/{assetAssociation,pidGenerator,replaceDevice}/`,
  `utils/{dashmanager,historyconfig,logging,systemProvisioning}/`,
  `utils/messages/comingSoon/`).
- **Core vs FieldApp**: 13 files differ + 14 FieldApp-only trees (same set as above
  plus `utils/deviceProfileDropDown/`).
- **Enterprise vs Core**: only 5 files differ + 1 orphan (`utils/deviceProfileDropDown/`
  exists in Enterprise only).

**Interpretation:** Enterprise ≈ Core (they are close siblings, both older than
FieldApp). FieldApp is the evolved branch with tests, the new encoder, user
preferences persistence, and several unique device workflows.

**Recommendation (Medium):** designate `SiteSync-FieldApp_Improvements_2026-04-11_1548`
as the single source of truth and archive or delete `SiteSYnc EnterpriseManagementScripts`
and (likely) `SiteSyncCore_2026-04-17_1622` once their divergent changes are
ported. Every bug listed in §3-§4 below that is present in FieldApp is almost
certainly also present in at least one of the stale copies — fix it in the
canonical tree only.

### 2.2 Jython 2.7 → Python 3 migration risks

Ignition has announced Jython 2.7 will eventually be replaced; these patterns
will not survive the move:

- **`print` statement (not `print(...)`)** found in:
  - `SiteSync-FieldApp_Improvements/.../getSensors/code.py:47,63,74,81,91,134,135,180,226,257,259,260,369,441,482,552,553,558`
  - `SiteSync-FieldApp_Improvements/.../device/excelParser/code.py:34`
  - `PISync_2026-04-11_1427/.../PIIntegration/devices/code.py:8,10`
  - `PI_Integration_Manager_2026-04-17_1632/.../adapter/code.py:21`
- **`long` type literal** — `PISync_2026-04-11_1427/.../exchange/mqttVanillaTransmission/callables/code.py:72,125` uses
  `isinstance(x, (..., long, ...))` and `type(x) in (int, long)`. `long` does not
  exist in Py3 (it's `int`).
- **`unicode` type literal** — same file, lines 72 and 127
  (`isinstance(..., unicode)`, `type(...) is unicode`). Replace with `str`
  (Py3) or guard with a version check.
- **`dict.keys()` used as list** — numerous `if x in dict.keys()` patterns (e.g.
  `getSensors/code.py:29,40,56,146,422; addDevices/code.py:63; bulkUpload:44`).
  Works in both, but `.keys()` returns a view in Py3 and should just be `if x in dict`
  for correctness + speed.
- **`!=` vs identity for `None`** — `resultParser/code.py:` uses `== None` /
  `!= None` throughout (also `PISync.../addDevices:11`, `adapter/code.py:23`,
  etc.). `is None` / `is not None` is the idiomatic form and the only one that
  survives comparisons with objects overriding `__eq__`.

**Before/after (generic pattern):**

```python
# before — Jython-only
if tagQualifiedValue.value is None:  # ok, but combined with:
if not isinstance(tagQualifiedValue.value, (bool, int, long, float, unicode)):
    raise DropReason(...)

# after — Jython 2.7 AND Py3 safe
try:
    long_t = long               # noqa: F821 (Py2 / Jython)
except NameError:
    long_t = int
try:
    unicode_t = unicode         # noqa: F821
except NameError:
    unicode_t = str

if not isinstance(tagQualifiedValue.value, (bool, int, long_t, float, unicode_t)):
    raise DropReason(...)
```

### 2.3 Logging inconsistency

Only a handful of scripts use `system.util.getLogger(...)` (e.g.
`SiteSyncCore/.../addDevices/code.py:92`, `.../PIIntegration/activate/code.py:13`,
`.../MPC/customizations/device/createDevice/code.py`). Most error paths use
`system.perspective.print(...)`, which:

- Only reaches session-scoped browser consoles; it is invisible in gateway logs.
- Silently no-ops when invoked from gateway-scoped scripts (e.g. tag change events,
  timer scripts, named queries). `tagChangeEvent()` in
  `PISync.../exchange/mqttVanillaTransmission/callables/code.py:231` correctly
  uses `system.util.getLogger(loggerName)` — follow that example everywhere.

**Before/after (generic pattern):**

```python
# before
except Exception as e:
    system.perspective.print("Error creating device: " + str(e))
    return False

# after
_LOGGER = system.util.getLogger("SiteSync-DeviceOnboarding")
...
except Exception as e:
    _LOGGER.error("Error creating device", e)   # logs stacktrace to gateway log
    return {"status": "error", "message": str(e)}
```

### 2.4 Credential / secret handling

- Hard-coded remote endpoint + component id:
  `PISync_2026-04-11_1427/.../addDevices/code.py:5-6` and
  `SiteSyncCore_2026-04-17_1622/.../addDevices/code.py:5-6`:
  ```python
  PIAddress = "https://pgwgen002923.mgroupnet.com:5590/api/v1/configuration"
  componentID = "MQTT1"
  ```
  Even though the current production caller uses
  `PIIntegration.adapter.addToDataSelection` (not these globals), the constants
  remain committed and leak an internal hostname.
  **Fix:** move to an Ignition system property, a named query, or a UDT tag and
  read once at function entry.

- `connections/mqtt/code.py:15-31`, `connections/networkserver/code.py:12-25`,
  `decoders/decoder/code.py:50-64`: MQTT password, join-server password, API
  token, and API password are assembled into JSON and forwarded to
  `system.sitesync.updateMqttSettings` / `updateJoinServerImpl` /
  `updateAPIConnection`. This is a trust-boundary crossing — the review
  recommends **confirming** on the Java side that:
  1. the module persists these encrypted (not plaintext on disk);
  2. the module does not echo them back via any `get*Settings` getter;
  3. no caller ever feeds the payload into `system.perspective.print`.

- `PI_Integration_Manager_2026-04-17_1632/.../AF/code.py:14` passes
  `AFsettings['token']` directly as an HTTP URL component to
  `system.piAdapter.doesTagExtistInPI(AFsettings['url'], AFsettings['token'], path, "AF")`.
  Verify that the Java adapter treats the token as an auth-header rather than
  interpolating it into a URL (leaking it to proxy logs).

### 2.5 Tag-path injection & input validation

Tag paths are assembled by string concatenation with no escaping. Any user-entered
value that flows into these helpers is effectively trusted:

- `SiteSync-FieldApp_Improvements/.../device/tagOperations/code.py:39-49`:
  ```python
  def assembleFullPath(provider, basePath, name):
      if basePath is None or basePath == "":
          return "[" + provider + "]" + name
      else:
          return "[" + provider + "]" + basePath + "/" + name
  ```
  Neither `provider`, `basePath`, nor `name` is validated. `]`, `/`, `\` or
  control characters in `name` change the resulting tag path semantics.
- `device/createDevice/code.py:46-60` has a `pathValidator()` regex
  (`r"^[A-Za-z0-9_][A-Za-z0-9_ /'':()-]*$"`) but it is (a) not applied to
  `provider`, (b) double-quoted twice (`'':` — likely a typo, the `'` is listed
  twice), and (c) only called from `validateDevice`. Bulk upload does not run it
  (`bulkUpload/code.py:67-106`).

**Recommendation (High):** centralize tag-path assembly in
`device.tagOperations.assembleFullPath` and call `device.createDevice.pathValidator`
on every component before concatenation. Raise on invalid input rather than
silently producing a malformed path.

### 2.6 Broad except blocks / silent failures

Swallow-and-ignore error handling in critical paths:

- `SiteSync-FieldApp_Improvements/.../userPreferences/db/code.py:65, 84, 192, 220` —
  four `except:` bare blocks that return `None`, `False`, `None`, `[]`. A DB
  outage, a malformed JSON blob, or a schema migration is indistinguishable from
  "no preferences set".
- `.../decoders/decoder/code.py:7-8` — `getDecoder` returns `{}` on any exception,
  same category.
- `.../decoders/decoder/code.py:70` — `loadAPI` wraps `system.sitesync.getAPIConnection`
  in a bare `except:` and sets `api = None`. The calling UI cannot distinguish
  "no API configured" from "adapter module crashed".
- `.../device/excelParser/code.py:70, 92, 104` — cell-parse errors fall through
  silently to `value = "" ` / `value = "error loading"`.
- `.../getSensors/code.py:46, 62, 112, 244` — per-tag exceptions are printed and
  swallowed.

**Before/after pattern:**

```python
# before
def getUserPreference(userId, preferenceKey):
    try:
        result = system.db.runNamedQuery(
            "userPreferences/getUserPreference",
            {"userId": str(userId), "preferenceKey": preferenceKey}
        )
        if result.rowCount > 0:
            import json
            return json.loads(result.getValueAt(0, 0))
        return None
    except:
        return None

# after
_LOGGER = system.util.getLogger("SiteSync-UserPreferences")

def getUserPreference(userId, preferenceKey):
    try:
        result = system.db.runNamedQuery(
            "userPreferences/getUserPreference",
            {"userId": str(userId), "preferenceKey": preferenceKey}
        )
    except Exception as e:
        _LOGGER.warn("getUserPreference DB error for %s/%s: %s" % (userId, preferenceKey, e))
        return None   # intentional: UI falls back to defaults

    if result.rowCount == 0:
        return None
    import json
    try:
        return json.loads(result.getValueAt(0, 0))
    except ValueError as e:
        _LOGGER.error("Malformed JSON preference for %s/%s: %s" % (userId, preferenceKey, e))
        return None
```

### 2.7 Tag I/O batching & performance

Ignition's `system.tag.readBlocking` / `writeBlocking` accept **lists**; one call
with N paths is dramatically cheaper than N calls with one path each. Several hot
loops violate this:

- `SiteSync-FieldApp_Improvements/.../getSensors/code.py:34` and `:50` —
  `getDevicesMakeAndModel` reads `manufacturer` and `sensorType` one tag at a
  time while iterating `system.tag.browse` results. For a site with 500
  devices this is ~1000 individual JNI round trips.
- `.../rowFormatterSimple` / `rowFormatter` (`getSensors/code.py:191-247,
  339-393`) calls `system.tag.browse` **per device** inside
  `getDevicesProductType` / `getDevicesbyModel`. With 500 devices and 10
  tags each that is 5,000 browse results materialised serially.
- `.../device/bulkUpload/code.py:44-48` — `updateMetaData` runs a tag write
  inside a row loop without batching.
- `SiteSyncCore_2026-04-17_1622/.../addDevices/code.py:25` — `getDataType` reads
  a `.dataType` property per attribute in `formatDataSelectionItem`.

**Before/after pattern:**

```python
# before
for i in tags.getResults():
    model = str(i['value'].value)
    if model != "None":
        mfgPath = str(i['fullPath']).replace('model', 'manufacturer')
        mfg = system.tag.readBlocking([mfgPath])[0].value        # N round trips

# after
results = list(tags.getResults())
mfgPaths = [str(i['fullPath']).replace('model', 'manufacturer') for i in results]
prdPaths = [str(i['fullPath']).replace('model', 'sensorType')   for i in results]
mfgVals  = system.tag.readBlocking(mfgPaths)    # 1 round trip
prdVals  = system.tag.readBlocking(prdPaths)    # 1 round trip
for i, mfgQv, prdQv in zip(results, mfgVals, prdVals):
    ...
```

Also note: `getSensors/code.py:261, 296-297` references an undefined
`deviceTagPaths` inside `getTrackedColumns` (it's a parameter in the sibling
function but a free variable here). This function would raise `NameError` on
first use.

---

## 3. Per-Folder Findings

## 3.1 `PISync_2026-04-11_1427/`

Six scripts, ~650 LOC. Handles device activation in PI Integration tag folders
plus a generic MQTT Vanilla Transmission helper.

### 3.1.1 `PISync_2026-04-11_1427/ignition/script-python/PIIntegration/activate/code.py`

**[CRITICAL] `replaceNull()` always returns `0`** — `code.py:6-10`

Both branches of the `if` return `0`. Non-null values are silently replaced with
`0` before being serialised into `deviceJSON`. That is the payload pushed to
MQTT.

```python
# before
def replaceNull(value):
    if value == None:
        return 0
    else:
        return 0

# after
def replaceNull(value, default=0):
    return default if value is None else value
```

**[CRITICAL] `selectAll` defined twice with different signatures** — `code.py:39-42` and `code.py:119-125`

The second definition (3 args, prints, sets row['selected'] to caller-provided
`select`) shadows the first (2 args, unconditional `True`). Any caller that was
written against the first will pass the wrong number of arguments. The first is
also dead code.

```python
# before (two definitions in the same file)
def selectAll(tableData):
    for row in tableData:
        row['selected'] = True
    return tableData
...
def selectAll(dataset, select):
    system.perspective.print(select)
    for row in dataset:
        system.perspective.print(row)
        row['selected'] = select
        system.perspective.print(row)
    return dataset

# after (pick one, drop the other; drop the prints)
def selectAll(dataset, select=True):
    for row in dataset:
        row['selected'] = select
    return dataset
```

**[LOW] typo `createReult`** — `code.py:94`

Variable is spelled `createReult` (missing the second `s`). It is returned on
line 97, so the typo does not break behaviour, but it makes grep harder and
looks unprofessional. Rename to `createResult`. The same typo exists in
`SiteSyncCore_2026-04-17_1622/.../createPITemplate/code.py:34` and
`PISync_2026-04-11_1427/.../createPITemplate/code.py:29`.

**[HIGH] unused `searchDirectory` parameter** — `code.py:100, 109`

`getAllDevicesInTargetFolder(searchDirectory)` and
`getAllFlickerableTagsTargetFolder(searchDirectory)` both ignore the argument
and hard-code `[default]PI Integration`.

```python
# before
def getAllDevicesInTargetFolder(searchDirectory):
    tagPaths = []
    results = system.tag.browse(path = "[default]PI Integration",
                                filter = {"recursive": True, 'tagType': "UdtInstance"})
    ...

# after
def getAllDevicesInTargetFolder(searchDirectory="[default]PI Integration"):
    results = system.tag.browse(path=searchDirectory,
                                filter={"recursive": True, "tagType": "UdtInstance"})
    return [str(r["fullPath"]) for r in results.getResults()
            if "/LoRaMetrics" not in str(r["fullPath"])]
```

**[LOW] `flickerDevice` is a 1-line wrapper with commented body** — `code.py:45-61`

18 lines of commented-out logic. Either delete the comment, or put the function
behind a feature flag — dead code rots.

**[MEDIUM] bare `forceCheckIn(tagList)` returns `False` unconditionally** — `code.py:4-5`

Stub with no docstring and no caller visible in any reviewed folder. If it is
genuinely unused, delete. If it's a placeholder, raise `NotImplementedError` so
a caller gets a clear signal.

### 3.1.2 `PISync_2026-04-11_1427/ignition/script-python/addDevices/code.py`

**[CRITICAL] hard-coded external endpoint + MQTT component id** — `code.py:5-6`

```python
# before
PIAddress   = "https://pgwgen002923.mgroupnet.com:5590/api/v1/configuration"
componentID = "MQTT1"

# after — read once from a UDT tag or gateway system property
def _piConfig():
    vals = system.tag.readBlocking([
        "[default]PI Integration/_config/PIAddress",
        "[default]PI Integration/_config/componentID",
    ])
    return vals[0].value, vals[1].value
```

**[HIGH] `null = None; false = False; true = True` at module top** — `code.py:1-3`

These are here so a JSON-ish dict literal can use JS-style `null/true/false`
tokens inside the Python source. The cleaner fix is to use proper Python
literals (`None`, `True`, `False`) directly inside the dict, or to load the
template from a JSON file. Under Py3 those names are reserved words and cannot
be rebound at all.

```python
# before
null = None
false = False
true = True
...
j = {"selected": true, "dataFields": null, ...}

# after
j = {"selected": True, "dataFields": None, ...}
```

**[MEDIUM] `counter = 0` dead variable inside loop** — `code.py:62`

Declared and never used. Delete.

**[LOW] large commented-out block** — `code.py:65-72`

Alternate payload shape left in as comments. Either check in both formats
behind a config flag or delete.

### 3.1.3 `PISync_2026-04-11_1427/ignition/script-python/PIIntegration/devices/code.py`

Four lines long after imports. Two print statements, no error handling.

**[HIGH] Py2-only print statement** — `code.py:8, 10`

```python
# before
def findUnactivatedDevices(...):
    ...
    print tag
    ...
    print devicePath

# after
_LOGGER = system.util.getLogger("SiteSync-PIDevices")
...
_LOGGER.debug("tag: %s" % tag)
...
_LOGGER.debug("device path: %s" % devicePath)
```

### 3.1.4 `PISync_2026-04-11_1427/ignition/script-python/PIIntegration/topics/code.py`

4 lines. Pure string replace. No findings.

### 3.1.5 `PISync_2026-04-11_1427/ignition/script-python/createPITemplate/code.py`

Creates a UDT instance template under `[default]PI Integration` and returns
the `TagConfigurationModel` result.

**[HIGH] duplicates `PIIntegration.activate.createInstance`** — `createPITemplate/code.py:3-33` vs `PIIntegration/activate/code.py:68-97`

Near-identical function in two modules. Pick one home and have the other import it.

**[LOW] same `createReult` typo** — `code.py:29`

**[LOW] stray `system.perspective.print(createReult)`** — `code.py:30`

Debug artefact left in production code.

### 3.1.6 `PISync_2026-04-11_1427/ignition/script-python/exchange/mqttVanillaTransmission/callables/code.py`

324 lines. Well-commented MQTT Vanilla Transmission helper (Cirrus Link engine
or transmission module). Overall quality is the best of the whole review — good
docstrings, proper custom exceptions, `system.util.getLogger`, traceback
capture. Two genuine issues:

**[HIGH] `long` / `unicode` only exist in Jython 2.7** — `code.py:72, 125, 127`

See §2.2 for the compat pattern.

**[MEDIUM] `topic = str(topic)[:-1]` inside `publish()`** — `code.py:168`

Silently drops the last character of the topic. If `resolvePublishParameters`
returns a trailing `/` intentionally (for hierarchical topics) that `[:-1]`
strip makes sense — but only by coincidence with the caller. Document the
contract or move the strip upstream (into `resolvePublishParameters`) so it is
visible to the reader and to test coverage.

```python
# before
topic = str(topic)[:-1]
payload = str(payload)

# after
# resolvePublishParameters returns topic with a trailing slash when
# payloadFormat=="value" so the measurement name can be stripped; normalise here.
if topic.endswith("/"):
    topic = topic[:-1]
payload = str(payload)
```

**[LOW] `Qos = qos if qos in (0,1,2) else 0`, then re-validated in `publish()`** — `code.py:36, 163-166`

Redundant validation; if `resolvePublishParameters` already coerces QoS to the
set `{0,1,2}`, the `if qos not in (0,1,2)` guard in `publish()` is unreachable.
If `publish()` is intended as a public helper independent of
`resolvePublishParameters`, document that explicitly.

---

## 3.2 `PI_Integration_Manager_2026-04-17_1632/`

Six small scripts, ~240 LOC. Perspective-facing wrapper around
`system.piAdapter.*`. **This folder has the worst defect density of the five.**

### 3.2.1 `PI_Integration_Manager_2026-04-17_1632/ignition/script-python/status/code.py`

**[CRITICAL] Two versions of the same functions in the same file** — `code.py:1-28`

Lines 2-8 define stubs (`return {}`, `return False`); lines 23-28 redefine them
identically. Between them (lines 10-19) is a commented-out "real"
implementation for `adapterAPIPingStatus` / `PIWebAPIPingStatus`. Only the
bottom pair wins today; anyone reading top-down will form the wrong mental
model.

```python
# before (lines 1-28)
import json
def getTransmitterStatus():
    ##returns connectivity status of MQTT Transmission clients
    return {}

def isUsingTransmission():
    return False

#
#def adapterAPIPingStatus():
#	results = system.piAdapter.testConnection("adapter")
#	j = {"status":True, "message":"Adapter API is reachable"}
#	return j
#
#
#def PIWebAPIPingStatus():
#	j = {"status":False, "message":"PI Web API is not reachable, SSL cert issue. Check logs for more information"}
#	return j

import json            # second import
def getTransmitterStatus():
    return {}

def isUsingTransmission():
    return False

# after
import json

def getTransmitterStatus():
    """Returns connectivity status of MQTT Transmission clients. Stub until TX integration lands."""
    return {}

def isUsingTransmission():
    return False
```

**[HIGH] bare module-name references** — `code.py:32, 41`

`adapterAPIPingStatus` calls `adapter.getAdapterSettings()` and
`PIWebAPIPingStatus` calls `AF.getAFSettings()` without any import. In Ignition
this works because all `script-python` siblings are placed on the project
module path, but referring to sibling modules by bare identifier is brittle —
a rename breaks it, and static analysis (e.g. pylint, Ruff in a CI wrapper)
cannot trace it. Add explicit `import` statements at the top.

```python
# before
def adapterAPIPingStatus():
    settings = adapter.getAdapterSettings()            # NameError if siblings not on path
    j = system.piAdapter.testConnection(settings["apiURL"], settings["datasourceID"], "adapter")

# after (adapt the import path to match the Ignition project hierarchy)
import adapter
import AF

def adapterAPIPingStatus():
    settings = adapter.getAdapterSettings()
    ...
```

**[HIGH] stray `system.perspective.print(j)` on the PI Web API ping** — `code.py:44`

Leaks the status dict (including whatever URL + token the module echoes back)
to any Perspective session that triggered the ping. Delete or downgrade to
`_LOGGER.debug`.

### 3.2.2 `PI_Integration_Manager_2026-04-17_1632/ignition/script-python/adapter/code.py`

**[CRITICAL] `removeFromDataSelection` calls the wrong API** — `code.py:54-63`

```python
def removeFromDataSelection(specificStreamID):
    ##accepts user inputted streamID, removes from adapter
    creds = getPICredentials()


    exists = system.piAdapter.createDataSelection(creds['datasourceID'],  creds['apiURL'], specificStreamID, creds['format'])
    ...
```

It calls `system.piAdapter.createDataSelection`, not a `remove*` / `deleteDataSelection`
method, and the signature does not match the working `addToDataSelection` on
line 45 (which passes `datasourceID, json.dumps(items), apiURL, format`).
Removal silently performs a malformed create. Either this function is never
called in production (dead code — flag for deletion) or users see remove-stream
failures.

```python
# after (pseudocode — confirm the real remove API in the piAdapter module)
def removeFromDataSelection(specificStreamID):
    creds = getPICredentials()
    result = system.piAdapter.removeDataSelection(
        creds['datasourceID'], specificStreamID, creds['apiURL'], creds['format']
    )
    if result is None:
        return {"status": False, "message": "PI adapter returned no response"}
    return json.loads(result)
```

**[CRITICAL] Py2 `print path` statement** — `code.py:21`

Syntax error under Py3. Replace with `_LOGGER.debug("resolved PI path: %s" % path)`.

**[HIGH] pointless `getPICredentials` indirection** — `code.py:28-30`

```python
def getPICredentials():
    return getAdapterSettings()
    #return {"url":"",  "componentID":"", "prefix":"", "sourceFolder":"", "type":""}
```

Entire function is a pass-through with a commented dict as "documentation".
Either delete the function and call `getAdapterSettings()` directly, or
document the expected shape in a docstring.

**[HIGH] silent `json.loads` crashes on adapter returning `"null"`** — `code.py:22-26, 45-49, 61-63`

`system.piAdapter.*` returns the literal string `"null"` when nothing is found.
`json.loads("null")` returns Python `None`, not a dict — so `exists['status']`
downstream raises `TypeError` instead of the intended
`{"status": False, "message": "Did not find PITag"}`. Compare `getAdapterSettings`
(line 4) which **does** guard against `"null"`; propagate that guard:

```python
# before
exists = system.piAdapter.doesTagExtistInPI(creds['apiURL'], creds['datasourceID'], path, "adapter")
if exists != None:
    return json.loads(exists)
else:
    return {"status":False, "message":"Did not find PITag"}

# after
exists = system.piAdapter.doesTagExtistInPI(
    creds['apiURL'], creds['datasourceID'], path, "adapter"
)
if exists in (None, "null", ""):
    return {"status": False, "message": "Did not find PITag"}
return json.loads(exists)
```

**[LOW] typo on `doesTagExtistInPI`** — `code.py:22`

Method name is misspelled (`Extist` → `Exist`). Fix it in the Java adapter
module too — they have to match.

### 3.2.3 `PI_Integration_Manager_2026-04-17_1632/ignition/script-python/settings/code.py`

**[HIGH] `utils.*` and module-imports implicit** — `code.py:12-15`

Same bare-module-reference pattern as `status/code.py`. Add `import utils`.

**[HIGH] no `"null"` / exception guard on `getSettings()`** — `code.py:5-6`

```python
# before
def getSettings():
    a =  system.piAdapter.getSettings("generic")
    return json.loads(a)

# after
def getSettings():
    a = system.piAdapter.getSettings("generic")
    if a in (None, "null", ""):
        return {}
    try:
        return json.loads(a)
    except ValueError:
        return {}
```

**[LOW] `updateSettings` has no return value** — `code.py:8-15`

Caller cannot tell success from failure via the return — they must rely on the
side-effect UI popup. Consider returning the parsed result.

### 3.2.4 `PI_Integration_Manager_2026-04-17_1632/ignition/script-python/AF/code.py`

**[CRITICAL] `pathFormatter` uses a Windows backslash in an HTTP-style path** — `code.py:50`

```python
endpoint = "{0}\{1}/{2}".format(repo, prefix, ss)
```

`\{` is a stray escape (actually just a literal `\` followed by `{`). PI Web
API paths use forward slashes throughout; the backslash will either 404 or be
URL-encoded into `%5C`. If a backslash is genuinely required on the PI side,
use `"{0}\\{1}/{2}"` and add a comment, or better `urllib.urlencode` it.

```python
# before
endpoint = "{0}\{1}/{2}".format(repo, prefix, ss)

# after — use / everywhere unless PI AF definitively demands \
endpoint = "{0}/{1}/{2}".format(repo, prefix, ss)
```

**[HIGH] `getPICredentials` indirection (same as adapter.py)** — `code.py:42-44`

Delete the wrapper.

**[HIGH] bare `tagOperations.formatRequest` / `settings.getSettings` references** — `code.py:10, 23, 34`

Add explicit `import tagOperations`, `import settings`.

**[MEDIUM] `system.perspective.print(path)`** — `code.py:13`

Prints a resolved PI path (potentially containing a source-folder name) to the
Perspective session. Downgrade to `_LOGGER.debug`.

**[LOW] mix of tabs, double-spaces, and trailing backticks throughout** — whole file

`PIWebAPIPingStatus` in `status/code.py:40-47` is indented with **two spaces**
while everything else uses **one tab**; Jython 2.7 accepts it but future
maintainers and Py3 will not. Re-indent consistently (Ignition's Script Editor
defaults to tabs).

### 3.2.5 `PI_Integration_Manager_2026-04-17_1632/ignition/script-python/tagOperations/code.py`

**[MEDIUM] hard-coded `[default]PI Integration` monitored path** — `code.py:27`

```python
def getMonitoredTagPath():
    return "[default]PI Integration"
```

Lift to a UDT tag or project parameter so multi-tenant gateways can point to
different folders.

**[LOW] commented `system.perspective.print` debug** — `code.py:20`

Delete.

### 3.2.6 `PI_Integration_Manager_2026-04-17_1632/ignition/script-python/utils/code.py`

**[CRITICAL] `showSuccess` blocks the UI thread for 3 seconds** — `code.py:18-21`

```python
def showSuccess(successText):
    system.perspective.openPopup("success", "Popups/success",  params = {"successText":successText})
    time.sleep(3)
    system.perspective.closePopup("success")
```

`time.sleep(3)` inside a Perspective action blocks the whole session event
queue. If the user clicks anything else during that window, the click is
queued and the UI feels frozen. Replace with the popup's own auto-close timer
(set `dismissAfterMs` on the popup view, or use `system.util.invokeLater` +
`Thread(..., daemon=True)` to close asynchronously).

```python
# after — non-blocking close
def showSuccess(successText):
    system.perspective.openPopup(
        "success",
        "Popups/success",
        params={"successText": successText, "dismissAfterMs": 3000},
    )
    # Popups/success view's onStartup handles its own auto-close.
```

**[HIGH] `type(x) != dict`** — `code.py:24, 31`

Idiomatic is `not isinstance(x, dict)`. `type()` comparisons break for any
subclass (e.g. `PyDictionary` / `collections.OrderedDict`).

```python
# before
if type(resultMessage) != dict:
    j = json.loads(resultMessage)
else:
    j = resultMessage

# after
if isinstance(resultMessage, dict):
    j = resultMessage
else:
    j = json.loads(resultMessage)
```

**[LOW] `showError` silently swallows popup errors** — `code.py:13-16`

The inner `except Exception as e: system.perspective.print(e)` hides the real
failure. Log it.

---

## 3.3 `SiteSYnc EnterpriseManagementScripts/`

52 scripts. This folder is the **oldest** of the three SiteSync copies. `diff -rq`
vs FieldApp shows 15 divergent files and 13 trees missing entirely. Most
findings in §3.4 (FieldApp) apply here **plus** the regressions of not having
received the recent bugfixes. The unique items worth calling out:

### 3.3.1 Stale `addDevices/code.py`

- **[HIGH]** `addTagToPi` (lines 91-98) lacks the try/except + `system.util.getLogger`
  that FieldApp + Core adopted. Any exception propagates out of the caller
  without context. Port the FieldApp version:

```python
# current (Enterprise)
def addTagToPi(tagPath, componentID, PIAddress):
    items = getAttributesForTag(tagPath)
    existingConfig = getCurrentDataSelection(componentID, PIAddress)
    piTags = formatDataSelectionItem(tagPath, items, existingConfig)
    results = updateDataSelection(piTags, componentID, PIAddress)
    return results

# port of FieldApp version (addDevices/code.py:91-102)
def addTagToPi(tagPath, componentID="", PIAddress=""):
    logger = system.util.getLogger("SiteSync-PiTagCreator")
    logger.info("Creating PI tag: " + tagPath)
    try:
        tagPathArray = [tagPath]
        adapterResults = PIIntegration.adapter.addToDataSelection(tagPathArray)
        results = PIIntegration.AF.createPITag(tagPath)
        logger.info("Adapter add: %s; PI tag create: %s" % (adapterResults, results))
    except Exception as e:
        logger.error("Error creating PI tag %s: %s" % (tagPath, e))
    return False
```

### 3.3.2 Stale `createPITemplate/code.py`

Same pattern: missing the try/except wrapper around `system.tag.configure` that
FieldApp gained. Any tag configure error surfaces as an uncaught exception in
the Perspective session rather than a `None` return.

### 3.3.3 Stale `device/createDevice/code.py`, `utils/sitehandler/code.py`

Small drift — Enterprise's versions lack the FieldApp `enterprise.tenant`
lookups and newer `utils.resultParser` usage. Before deleting the Enterprise
tree, spot-check each divergent file for a unique fix worth porting forward.

### 3.3.4 Orphaned `utils/deviceProfileDropDown`

Exists only in Enterprise (not in Core). If the module has genuinely been
retired, delete it from Enterprise as part of the consolidation. If it is
still used by any Enterprise-only view, port the view into FieldApp so the
Enterprise tree can be archived wholesale.

### 3.3.5 High-level recommendation

Do not invest review effort per-file here — instead, pick a consolidation
approach (see §5) and remove the Enterprise tree from source control once the
few unique changes are merged into FieldApp.

---

## 3.4 `SiteSync-FieldApp_Improvements_2026-04-11_1548/`

113 scripts. The canonical, current tree. Findings below are the ones worth
the most engineering attention.

### 3.4.1 `getSensors/code.py`

The single most issue-dense file in the repo.

**[CRITICAL] `NameError: deviceTagPaths` in `getTrackedColumns`** — `code.py:294`

```python
def getTrackedColumns(deviceType, viewType):
    if viewType == "Simple":
        trackedColumns = getSimpleTags(deviceType).keys()
    else:
        firstInstance = deviceTagPaths.values()[0]   # <-- free variable
        trackedColumns = getAllTrackedTags(firstInstance).keys()
    return trackedColumns
```

`deviceTagPaths` is not a parameter, module global, or closure. The non-simple
branch raises `NameError` the first time it runs. Either this function is dead
code, or no-one ever hits the non-Simple view. Add the missing parameter:

```python
# after
def getTrackedColumns(deviceType, viewType, deviceTagPaths=None):
    if viewType == "Simple":
        return list(getSimpleTags(deviceType).keys())
    if not deviceTagPaths:
        return []
    firstInstance = next(iter(deviceTagPaths.values()))
    return list(getAllTrackedTags(firstInstance).keys())
```

**[CRITICAL] `rowFormatter` references undefined `engUnits`** — `code.py:383-385`

```python
if tagTitle in trackedColumns and viewType != "Simple":
    #print "Getting setpoints for " + str(tag["fullPath"])
#	tagP = getHiLow( str(tag["fullPath"]))
    #engUnits = system.tag.readBlocking(tagP)
    items[tagName + "High"] = engUnits[0].value
    items[tagName + "Low"] = engUnits[1].value
```

The two lines that actually define `engUnits` are commented out; the last two
that **use** it are live. Any non-Simple viewType path into this function raises
`NameError`. Either restore the two commented lines or remove the now-orphaned
assignments.

**[HIGH] batched-read anti-pattern** — `code.py:26-65, 191-247, 339-393`

See §2.7 for the batching rewrite. These browse + per-tag read loops are the
main cause of slow Perspective session loads on sites with many devices.

**[HIGH] Py2 `print` statements — eighteen of them** — `code.py:47,63,74,81,91,134,135,180,226,257,259,260,369,441,442,482,552,553,558`

Replace with `_LOGGER.debug(...)` or delete.

**[MEDIUM] copy-paste between `rowFormatter` and `rowFormatterSimple`** — `code.py:191-247, 339-393`

~150 lines of near-duplicate code. Extract a helper that takes a boolean
`includeSetpoints` / `includeMetaData` flag. This also makes the `engUnits`
bug disappear.

**[MEDIUM] `getSensorBase` / `getModelBase` return paths with `_types_/SiteSync/<type>`** — `code.py:116-131`

Using path-based UDT lookup couples the code to Ignition's tag type store. If
a site renames the UDT tree the code silently returns a non-existent path and
all downstream `browse` calls return empty — which the code does not detect.
Probe the result:

```python
# after
def getSensorBase(deviceType):
    path = tagProvider + "_types_/SiteSync/" + {
        "PRESSURE":      "PressureSensor",
        "VALVEPOSITION": "ValvePositionSensor",
        "CURRENT":       "CurrentSensor",
        "VOLTAGE":       "VoltageSensor",
    }.get(deviceType, deviceType)
    if not system.tag.exists(path):
        raise ValueError("Sensor UDT path does not exist: %s" % path)
    return path
```

**[LOW] literal `"None"` string check** — `code.py:28, 224`

```python
if model != "None":
```

Compares against the string `"None"` rather than the value `None`. This works
only because the upstream `str(i['value'].value)` coerces `None` → `"None"` —
brittle. Keep the `.value` untouched and compare with `is None`.

### 3.4.2 `device/createDevice/code.py`

**[HIGH] 44 lines commented out at top of `saveDevice`** — `code.py:6-44`

Historical implementation left as a comment above the new delegator call. It
has rotted (references `deviceProfileID`, `siteName` that the current signature
doesn't accept). Delete.

**[HIGH] `pathValidator` regex has a double single-quote** — `code.py:55`

```python
pattern = r"^[A-Za-z0-9_][A-Za-z0-9_ /'':()-]*$"
```

`'':` lists the apostrophe twice. Harmless but suggests the regex wasn't
reviewed. Intended was probably `"` as well:

```python
pattern = r"""^[A-Za-z0-9_][A-Za-z0-9_ /"':()-]*$"""
```

**[MEDIUM] `validateDevice` leaks device payload to Perspective** — `code.py:69`

`system.perspective.print(device)` in a validator dumps the whole device
request (including `applicationKey`, `joinEUI`) to the browser console.

**[LOW] `charCheck` over-engineered** — `code.py:62-66`

```python
def charCheck(string, stringLength):
    if len(string) == stringLength:
        return True
    else:
        return False

# after
def charCheck(string, stringLength):
    return len(string) == stringLength
```

### 3.4.3 `device/tagOperations/code.py`

**[HIGH] tag-path injection (see §2.5)** — `code.py:39-49`

**[MEDIUM] `regenerateTag` is a stub that always returns `False`** — `code.py:2-3`

Either remove the function or raise `NotImplementedError` so the caller's
optimistic path does not silently "succeed".

### 3.4.4 `device/bulkUpload/code.py`

**[HIGH] `charCheck(appKey, 32) > 0` — boolean compared with integer** — `code.py:76`

`charCheck` returns `True`/`False`. `True > 0` is `True`, `False > 0` is `False`,
so this works *by coincidence* through boolean→int coercion. The intent is
`if charCheck(appKey, 32):`.

```python
# before
if charCheck(appKey, 32) > 0:

# after
if charCheck(appKey, 32):
```

**[MEDIUM] `bulk_upload` uses deeply nested `if ok: ... else: return err` ladders** — `code.py:33-58, 67-106`

Refactor to early-return style to reduce cognitive load for future maintainers.

### 3.4.5 `device/excelParser/code.py`

**[HIGH] `fileName` parameter is actually a byte-array** — `code.py:1, 20`

```python
def excelToDataSet(fileName, hasHeaders = False, ...):
    ...
    fileStream = ByteArrayInputStream(fileName)
```

The parameter is named `fileName` but `ByteArrayInputStream(fileName)` expects
raw bytes. Rename the parameter (`fileBytes`) and/or document the contract.

**[HIGH] `print str(i).zfill(3), list(row)`** — `code.py:34`

Py2 print statement with the multi-arg tuple form. Delete or downgrade to
`_LOGGER.trace`.

**[HIGH] bare `except:` on cell-type parsing** — `code.py:70, 92`

Swallows cell access errors into `"error loading"` / `""`. At minimum log the
row/col:

```python
# before
try:
    value = cell.getStringCellValue()
except:
    value = "error loading"

# after
try:
    value = cell.getStringCellValue()
except Exception as e:
    _LOGGER.warn("Excel cell parse failed at row %d col %d: %s" % (i, j, e))
    value = ""
```

**[MEDIUM] `system.perspective.print(cell)` inside the per-cell loop** — `code.py:55`

Single upload can dump thousands of cell objects into the Perspective console.
Delete or put behind a debug flag.

**[MEDIUM] `wb` / `fileStream` not closed on exception** — `code.py:22, 101`

If anything between `wb = WorkbookFactory.create(fileStream)` and the final
`fileStream.close()` raises, the stream leaks. Use try/finally:

```python
# after
fileStream = ByteArrayInputStream(fileBytes)
try:
    wb = WorkbookFactory.create(fileStream)
    try:
        ... parsing ...
    finally:
        wb.close()
finally:
    fileStream.close()
```

### 3.4.6 `decoders/decoder/code.py`

**[CRITICAL] secrets assembled client-side** — `code.py:50-64`

`updateAPI` builds a JSON blob with `apiToken`, `apiUserName`, `apiPassword`
and forwards it to `system.sitesync.updateAPIConnection`. Confirm the backend
encrypts at rest and does not return the password in `loadAPI` (line 67-86)
without masking.

**[HIGH] bare `except:` in `loadAPI`** — `code.py:69-71`

```python
# before
def loadAPI(modelID):
    try:
        api = system.sitesync.getAPIConnection(modelID)
    except:
        api = None

# after
def loadAPI(modelID):
    try:
        api = system.sitesync.getAPIConnection(modelID)
    except Exception as e:
        _LOGGER.warn("loadAPI(%s) failed: %s" % (modelID, e))
        api = None
```

**[HIGH] empty `except Exception as e: return {}`** — `code.py:7-8`

`getDecoder` silently returns `{}` on any error, including JSON parse errors
downstream. Log it.

**[LOW] `updateAPI`'s `"name": "New API Connection"` is hard-coded** — `code.py:52`

The function accepts a `name` parameter but never uses it. Either remove the
parameter or wire it through.

### 3.4.7 `connections/mqtt/code.py`

**[CRITICAL] MQTT password passed plaintext through JSON** — `code.py:15-31`

See §2.4. Also, the function strips whitespace from **every** input (`.strip()`
calls on every field including the password): this corrupts any password that
intentionally begins or ends with whitespace. Validate the broker accepts
trimmed passwords before stripping.

**[MEDIUM] `tlsVerification` and `auth` come in as booleans, coerced via `utils.boolConverters.getInt`** — `code.py:23-24`

Confirm `getInt` is idempotent — if the caller has already bool-ified them, a
second conversion must not flip values.

### 3.4.8 `connections/networkserver/code.py`

Same family of issues as `mqtt/code.py`. **[CRITICAL]** plaintext
password/token forwarded to `system.sitesync.updateJoinServerImpl`; whitespace
is stripped from every field.

**[HIGH] inconsistent null-check across getters** — `code.py:4-9`

```python
if js != None and js != "null" and "error" not in js.lower():
```

The `"error" not in js.lower()` substring check is fragile — a valid server
URL containing the letters `error` would falsely reject. Compare against a
structured response (a shape like `{"status": "error", ...}` parsed post-JSON).

### 3.4.9 `userPreferences/db/code.py`

**[HIGH] four bare `except:` blocks swallowing DB errors** — `code.py:65, 84, 192, 220`

See §2.6. This is the only module in the whole repo that uses
`system.db.runNamedQuery` — use the opportunity to set a logging standard here
and copy it elsewhere.

**[MEDIUM] `getUserPreference` returns `None` in three different failure modes** — `code.py:54-66`

Empty row, JSON parse failure, and DB exception are indistinguishable to the
caller. Split: raise for catastrophic failures, return `None` only for "not
set".

**[LOW] `PREFERENCE_KEY_COLUMNS = "device_manager_columns"`** — `code.py:7`

Consider making this a per-tenant key so different tenants don't share
preferences by accident: `"device_manager_columns/%s" % tenantId`.

### 3.4.10 `utils/resultParser/code.py`

**[HIGH] `getResultMessage` references undefined `json`** — `code.py:24`

```python
return "Error getting results: " + json.dumps(results)
```

There is no `import json` at the top of the file. If `results` has no
`message` key, the fallback branch raises `NameError`. Add `import json`.

**[HIGH] `'status'.upper() == "SUCCESS"`** — `code.py:9`

Assumes `results['status']` is a string. `system.sitesync.*` sometimes returns
`{"status": True, ...}` (see adapter/code.py:34-36) — `.upper()` on `True`
throws `AttributeError`. Accept both:

```python
# after
status = results.get('status')
if isinstance(status, bool):
    return bool(status)
if isinstance(status, str) and status.upper() == "SUCCESS":
    return True
return False
```

### 3.4.11 `utils/sitehandler/code.py`

**[MEDIUM] `createSite` swallows nothing, but silently returns `False` on both
the happy-path missing-tenant branch and the error branch** — `code.py:25-38`

The `utils.messages.errors.showErrorMessage` side-effect is the only signal
the caller gets. Return a `resultParser.createResults(...)` instead.

**[LOW] redundant `import json`** — `code.py:32`

Already imported at module top.

### 3.4.12 `utils/logging/code.py`

One function, looks fine. Note: this is the only module defining a true
logging wrapper — consider renaming to `utils/siteLog/code.py` to avoid
shadowing Python's built-in `logging` module name (which Jython 2.7 does
expose).

### 3.4.13 `tests/runner/runner/code.py`

The runner is solid. Findings minor:

**[LOW] dynamic import via `__import__` swallows module-level exceptions** — `code.py:56-66`

Any `ImportError` in a suite's **imports** (e.g. a suite importing a stale
module) is reported as "Import error" but not as `sys.exc_info()`. Capture
`traceback.format_exc()` so the offending line is visible.

**[LOW] `print` statements for summary output** — `code.py:107-131`

Acceptable because this is intentionally a CLI-style report, but would be
nicer to produce a structured dict only and let the caller decide formatting.

---

## 3.5 `SiteSyncCore_2026-04-17_1622/`

51 scripts. Near-identical to FieldApp's production modules (no `tests/`,
`userPreferences/`, `survey/`, `dashboard/aggregation/`, `decoders/encoder/`,
or `utils/{logging,historyconfig,systemProvisioning,dashmanager}/`). Of the
FieldApp-only additions, only `tests/` has test coverage — so any bug that
exists in Core and has a FieldApp test reproducing it is definitively broken
in both places.

### 3.5.1 `addDevices/code.py`

**[CRITICAL] hard-coded URL + component id (same as PISync)** — `code.py:5-6`

```python
PIAddress = "https://pgwgen002923.mgroupnet.com:5590/api/v1/configuration"
componentID = "MQTT1"
```

Fix recipe in §3.1.2.

**[HIGH] `null = None; false = False; true = True`** — `code.py:1-3`

Same as PISync; remove.

**[HIGH] `addTagToPi` catches-and-logs but returns `False` unconditionally** — `code.py:91-102`

```python
def addTagToPi(tagPath, componentID = "", PIAddress = ""):
    logger = system.util.getLogger("SiteSync-PiTagCreator")
    logger.info("Creating PI tag: " + tagPath)
    try:
        tagPathArray = [tagPath]
        adapterResults = PIIntegration.adapter.addToDataSelection(tagPathArray)
        results = PIIntegration.AF.createPITag(tagPath)
        logger.info(...)
    except Exception as e:
        logger.error(...)

    return False
```

Both the happy path and the error path return `False`. Callers that rely on
the return value (for instance `createPITemplate.createInstance` on line 39 of
the same folder) cannot distinguish success from failure.

```python
# after
def addTagToPi(tagPath, componentID="", PIAddress=""):
    logger = system.util.getLogger("SiteSync-PiTagCreator")
    logger.info("Creating PI tag: " + tagPath)
    try:
        adapterResult = PIIntegration.adapter.addToDataSelection([tagPath])
        createResult  = PIIntegration.AF.createPITag(tagPath)
        logger.info("Adapter: %s; PI tag create: %s" % (adapterResult, createResult))
        ok = utils.resultParser.isResultSuccess(adapterResult) \
         and utils.resultParser.isResultSuccess(createResult)
        return utils.resultParser.createResults(ok, "addTagToPi: %s" % tagPath)
    except Exception as e:
        logger.error("Error creating PI tag %s: %s" % (tagPath, e))
        return utils.resultParser.createResults(False, str(e))
```

### 3.5.2 `createPITemplate/code.py`

**[HIGH] swallows all exceptions and returns `None`** — `code.py:43-45`

```python
except Exception as e:
    system.perspective.print("Error " + str(e))
    return None
```

Caller (typically a Perspective "Create PI Tag" button) cannot surface the
actual reason. Log with `system.util.getLogger` and return a structured
`resultParser.createResults(False, str(e))`.

**[LOW] typo `createReult`** — `code.py:34`

Same as §3.1.1.

**[LOW] commented debug print** — `code.py:4, 35, 40-41`

Three commented `system.perspective.print` calls. Delete.

### 3.5.3 Everything else

Apply the FieldApp findings (§3.4) to the matching files. Once Core is merged
into FieldApp per §5, the only Core-unique fixes to preserve are any edits
made after FieldApp's 2026-04-11 snapshot — confirm via `git log` on the two
folders before deleting.

---

## 4. Test Suite Assessment

Only the FieldApp folder has tests.

- **Framework:** a custom runner (`tests/runner/runner/code.py`) loading each
  suite by dotted path via `__import__(modulePath, fromlist=["run"])`. Each
  suite exposes a `run()` function that returns a list of `{name, status,
  message}` dicts.
- **Split:** 19 "pure" suites (no `system.*` calls, safe to run anywhere) and
  27 "I/O" suites (require a live gateway with SiteSync backend + tag
  provider). The split is well-kept — good practice for Ignition testing.
- **Reach:** 46 suites total. Areas with tests: resultParser, boolConverters,
  dropdowns, createDevice, tagOperations, updateDevice, bulkuploadV2,
  QRCodeParser, model, encoder, networkserver, icons, pidGenerator,
  historyconfig, dashmanager, userPreferences, installationReport, routing,
  tenant (pure), plus a parallel set of `_io` suites. Areas **without** tests:
  `getSensors/*`, `PIIntegration/*`, `connections/mqtt` (the pure logic
  fraction), `decoders/decoder` (the non-io entry points), `utils/logging`,
  `utils/sitehandler`.
- **Suggested next suites:**
  - A pure suite `test_resultParser_roundTrip` exercising the bool/string
    status ambiguity in §3.4.10.
  - A pure suite `test_pathValidator` pinning the regex behaviour flagged in
    §3.4.2 (including the `'':` edge case).
  - An io suite `test_userPreferences_io` proving that a DB outage surfaces as
    an error (not a silent `None`), reinforcing the §3.4.9 fix.

**Runner limitations worth noting:**

- `_importAndRun` catches any `Exception` from the suite's `run()` but not
  `java.lang.Exception`. A Java-side crash (e.g. a `NullPointerException` from
  `system.sitesync.*`) will still bubble up and abort the runner. Consider
  adding a `java.lang.Exception as JEx` handler analogous to the one in
  `PISync_2026-04-11_1427/.../callables/code.py:178`.
- Suites import by dotted path (`tests.suites.test_foo`). Any import of a
  stale sibling module (e.g. something that imports `PIIntegration` from the
  Enterprise tree) may succeed in one environment and fail in another,
  depending on project resource ordering — another reason to consolidate to
  one tree.

---

## 5. Recommended Remediation Order

Fix high-impact items first and preserve review context via focused PRs.

1. **Correctness bugs (1-2 days)** — merge fixes for the items that actively
   misbehave at runtime:
   - `PIIntegration/activate/code.py` `replaceNull` (§3.1.1)
   - duplicate `selectAll` / `status/code.py` stubs (§3.1.1, §3.2.1)
   - `adapter/code.py` `removeFromDataSelection` wrong API (§3.2.2)
   - `AF/code.py` backslash in path (§3.2.4)
   - `getSensors/code.py` undefined `deviceTagPaths` + `engUnits` (§3.4.1)
   - `resultParser.getResultMessage` missing `import json` (§3.4.10)
   - `utils/code.py` 3-second UI-blocking sleep (§3.2.6)

2. **Credential / config hygiene (½ day)** — move hard-coded endpoints out of
   source, audit that `system.sitesync.updateMqttSettings /
   updateJoinServerImpl / updateAPIConnection` do not echo secrets.
   - `PISync/addDevices:5-6` + `SiteSyncCore/addDevices:5-6`
   - follow-up with Java-side owner for the three plaintext-credential
     confirmations in §2.4

3. **Folder consolidation (1-2 days)** — decide canonical tree:
   - Recommended: promote `SiteSync-FieldApp_Improvements_2026-04-11_1548` to
     the only SiteSync source-of-truth.
   - `diff` Enterprise and Core individually against FieldApp; cherry-pick
     any unique fixes forward, then delete Enterprise and Core trees from
     source control.
   - Keeping three copies makes every bug in §3.4 also exist in §3.3 / §3.5,
     silently.

4. **Tighten error handling (1-2 days)**
   - Replace every bare `except:` or `except Exception: return None` with a
     logged, typed handler (§2.6 pattern).
   - Replace `system.perspective.print` with `system.util.getLogger` where the
     call site is gateway-scoped (tag changes, timers, named queries).

5. **Py3-readiness (can be incremental)**
   - Replace `print x` with `print(x)` or logger calls.
   - Replace `long` / `unicode` with version-safe aliases (§2.2 pattern).
   - Replace `x in d.keys()` with `x in d`, `type(x) != dict` with
     `isinstance(x, dict)`, `== None` with `is None`.

6. **Performance (1 day, once the correctness bugs stabilize)**
   - Batch `system.tag.readBlocking` / `writeBlocking` calls in
     `getSensors/code.py`, `device/bulkUpload/code.py`,
     `SiteSyncCore/addDevices/code.py`.

7. **Tests (ongoing)** — add the three suites suggested in §4 and expand I/O
   coverage for `PIIntegration/*` once the fixes in §3.2 land.

---

## 6. Verification Commands

```bash
# diffs used to establish duplication
diff -rq "SiteSYnc EnterpriseManagementScripts/script-python/" \
         "SiteSync-FieldApp_Improvements_2026-04-11_1548/ignition/script-python/"
diff -rq "SiteSyncCore_2026-04-17_1622/ignition/script-python/" \
         "SiteSync-FieldApp_Improvements_2026-04-11_1548/ignition/script-python/"
diff -rq "SiteSYnc EnterpriseManagementScripts/script-python/" \
         "SiteSyncCore_2026-04-17_1622/ignition/script-python/"

# one-shot grep to find every Py2 print statement
grep -rnE '^\s*print\s+[^(]' --include="*.py" . | grep -v 'print('
```

Results captured at review time:

- Enterprise vs FieldApp: 15 files differ, 13 orphan trees FieldApp-only.
- Core vs FieldApp: 13 files differ, 14 orphan trees FieldApp-only.
- Enterprise vs Core: 5 files differ, 1 orphan (`utils/deviceProfileDropDown`
  Enterprise-only).

---
*End of review.*






