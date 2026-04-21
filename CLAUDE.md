# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

This is an **Ignition project export** (Inductive Automation 8.1.50) — not a standalone Python app. The files you see are what the Ignition Designer/Gateway serialize to disk: `code.py` + `resource.json` per script resource, `view.json` per Perspective view, `query.sql` per named query, etc. Code runs inside the Ignition Gateway JVM, not under CPython.

- **Runtime:** Jython 2.7.3 (Python 2.7 semantics on the JVM), Java 17 (Azul / Microsoft OpenJDK).
- **Active project at repo root:** `SIteSyncLocation` (see `project.json`). Its resources live under `ignition/`, `named-query/`, `com.inductiveautomation.perspective/`, `com.inductiveautomation.vision/`, `com.inductiveautomation.webdev/`, `global-props/`.
- **Sibling directories are separate project exports / snapshots** used for reference and cross-project review: `PISync_2026-04-11_1427/`, `SiteSyncCore_2026-04-17_1622/`, `PI_Integration_Manager_2026-04-17_1632/`, `SiteSync-FieldApp_Improvements_2026-04-11_1548/`, `FileTranslator_20260322203920/`, `SiteSYnc EnterpriseManagementScripts/`. Don't assume changes in one flow to the others — each is its own deployable.
- **`ignition-sdk_examples-main/`** is unrelated reference material (Java/Gradle/Maven module SDK examples), not part of the SiteSync project.

## Running / debugging Jython locally

```bash
./jython.sh path/to/script.py      # run any script on the bundled jython-standalone-2.7.3.jar
./jython.sh                        # interactive REPL
./jython.sh test_jython_setup.py   # smoke-test Java integration
```

- `jython.sh` auto-adds any `ignition-libs/*.jar` to the classpath if that directory exists.
- `JAVA_HOME` is pinned in `.vscode/settings.json` to `/usr/local/sdkman/candidates/java/21.0.10-ms` for the terminal; the Gateway itself runs Java 17.
- **Debugging:** VS Code gutter breakpoints do **not** fire — `debugpy` is CPython-only. Use the project's own helper:
  ```python
  from utils.debug import brk   # ignition/script-python/utils/debug/code.py
  brk()                         # drops into pdb if stdin is a tty, logs & returns otherwise
  ```
  Then launch the **"Jython 2.7 Debug"** configuration in `.vscode/launch.json`.

There is **no test suite, lint, or build step** wired up at the repo level. Validation happens by importing the project into an Ignition Gateway. `test_jython_setup.py` and `test_debug_helper.py` are ad-hoc smoke tests, not a framework.

## Code-review skill

This repo is the primary target for the `ignition-code-review` skill (rigorous Jython-2.7-on-Java-17 review). When the user asks for a review, audit, bug hunt, or security pass on any `.py` file under an `ignition/script-python/` tree, **invoke that skill** — a generic Python review will miss non-obvious failure modes (signed-byte Java interop, `system.*` scope/deprecation bugs, Python 2.7 `except X, e:` vs `as` subtleties, Tag Change Script reentrancy, SQL injection via `runPrepQuery` misuse, etc.). Prior review output is in `CODE_REVIEW.md`, `CODE_REVIEW (1).md`, `PISYNC_CodeReview.txt` — read these before re-reviewing to avoid duplicate findings.

## Architecture in one pass

### Ignition resource layout (what maps to what)

| On disk | In the Designer |
|---|---|
| `ignition/script-python/<pkg>/<module>/code.py` | Project script library `<pkg>.<module>` — importable as `<pkg>.<module>` from any Gateway/Designer script |
| `ignition/script-python/<pkg>/<module>/resource.json` | Scope + metadata. `"scope": "A"` = All, `"G"` = Gateway, `"C"` = Client — matters; a Gateway-only script imported from a Perspective session will fail at runtime |
| `ignition/event-scripts/`, `ignition/global-props/`, `ignition/designer-properties/` | Binary-serialized project event scripts and properties (`data.bin`) — not directly readable; edit via Designer |
| `named-query/<folder>/<name>/{query.sql,resource.json}` | Named Query. `resource.json` defines DB binding, parameters (`sqlType` ints per `java.sql.Types`), cache policy |
| `com.inductiveautomation.perspective/views/<path>/view.json` | One Perspective view. 91 views total — all JSON; safe to grep/edit but structure is load-bearing |
| `com.inductiveautomation.perspective/session-scripts/`, `session-props/`, `style-classes/`, `stylesheet/` | Perspective session-scope resources |
| `com.inductiveautomation.vision/client-tags/` | Vision client tags |
| `com.inductiveautomation.webdev/resources/` | Webdev endpoints |

### Script packages (under `ignition/script-python/`)

- `utils/*` — shared helpers imported across the project. `boolConverters`, `debug`, `resultParser`, `timeFormatter`, `normalizedTagPaths`, `QRCodeParser`, `sitehandler`, `dropdowns`, `deviceProfileDropDown`, `tagPathDropdown`. Treat these as the cross-cutting library; changes here ripple everywhere.
- `SiteSync/Location` — GVL device tag management: devEUI→folder cache (`_devEUI_cache`), ThingPark uplink parser, site temperature read.
- `LocationAPI` — UDT-instance GPS lookup endpoint (batched `system.tag.readBlocking` over LAT/LNG pairs).
- `connections/mqtt`, `connections/networkserver` — wrap `system.sitesync.*` calls for MQTT broker settings / network server lifecycle.
- `decoders/*` — JS decoder CRUD, test harness, and the API-connection wrapper. All persistence flows through `system.sitesync.*`.
- `device/*` — device activation, diagnostics, bulk upload v1/v2, Excel parser, image handling.
- `enterprise/tenant` — tenant-level scripts (currently largely stubbed — `getDefaultApp` returns a literal 3).
- `dashboard/*`, `createPITemplate` — UI routing / icons / colors, and PI UDT template creation.

### The `system.sitesync.*` namespace

Custom **scripting function module** exposed by the SiteSync Gateway module itself. You will see calls like `system.sitesync.getMQTTSettings(tenantID)`, `system.sitesync.updateDecoder(decoder)`, `system.sitesync.createInstance(...)`. These are **not** part of stock Ignition — their implementations live in the SiteSync Gateway module (not in this repo) and most return JSON strings that the Jython wrapper then `json.loads`. When something looks "missing," it's probably Gateway-side Java.

## Conventions the codebase already follows

- **Tabs, width 4** for Python files (`.vscode/settings.json`). Matching the existing style in any file you edit avoids Designer serialization churn.
- **Python 2.7 syntax only.** No f-strings, no `print(...)` with parens-required, no `pathlib`, no `typing`. Use `"{}".format(x)` or `"%s" % x`. Exception binding is written both `except X as e:` (supported in 2.7) and `except X, e:` (legacy) — both work; prefer `as`.
- **`system` and `utils` are implicit globals** inside Gateway/Designer script scope. Pyright is configured to suppress `reportUndefinedVariable` for exactly this reason (`pyrightconfig.json`) — don't add dummy imports to silence linters.
- **Logging:** `system.util.getLogger("<dotted.name>")` at module top, then `_logger.debug(...)` / `.warn(...)` / `.error(...)`. Don't `print` from Gateway scope.
- **Tag reads/writes are batched:** code consistently builds a path list and calls `system.tag.readBlocking(paths)` / `writeBlocking(paths, values)` once. Preserve this — looped single reads are a perf regression.
- **Tag-path separators:** `/` separates tag children; `.` accesses tag properties (`.Enabled`, `.dataType`). Mixing them silently yields `Bad_NotFound` writes — a real past bug recorded in `PISYNC_CodeReview.txt`.
- **`.ignition-stubs/`** is gitignored and excluded from Pyright / python.analysis; it's IDE-completion scaffolding, not source. Don't edit or commit it.

## Don'ts specific to this repo

- Don't introduce `bytes`/`str` distinctions, `async`/`await`, type annotations, or f-strings — Jython 2.7 will SyntaxError at Gateway load.
- Don't hand-edit `data.bin` files under `event-scripts/`, `global-props/`, or `designer-properties/` — they're Java-serialized blobs.
- Don't move scripts between scopes without updating `resource.json` `"scope"`; a Client-scope script calling Gateway-only `system.*` will blow up at runtime, not at import.
- Don't assume sibling project directories (`PISync_*`, `SiteSyncCore_*`, …) share code with the root project — they're independent exports. Fix bugs in each one that ships separately.
