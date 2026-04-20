# Jython 2.7 Development Environment for Ignition

This workspace is configured for developing and debugging Jython 2.7 scripts for Inductive Automation's Ignition platform.

## Environment Setup

### Prerequisites
- Java 8+ (OpenJDK recommended)
- Bash shell

### Files Created
- `jython2.7.4/` - Jython 2.7.4 runtime install tree (`jython.jar`, `Lib/`, `bin/`, `registry`) produced by the Maven `jython-installer` artifact
- `jython.sh` - Launcher script for Jython (sets `python.home=jython2.7.4`)
- `test_jython_setup.py` - Environment verification script
- `.vscode/launch.json` - VS Code debug configurations
- `.idea/runConfigurations/Jython_2_7.xml` - PyCharm run configuration

## Usage

### Running Scripts
```bash
# Run any Python script with Jython
./jython.sh your_script.py

# Start interactive Jython console
./jython.sh
```

### Debugging in VS Code

VS Code gutter breakpoints do **not** fire under Jython — `debugpy` is CPython-only. Use the `utils.debug` helper to drop into a `pdb` prompt in the integrated terminal instead:

```python
from utils.debug import brk
# ... code ...
brk()  # execution pauses here when stdin is a tty
```

Then:
1. Open the Run and Debug panel (Ctrl+Shift+D).
2. Select "Jython 2.7 Debug" and press F5.
3. When execution reaches `brk()`, the integrated terminal shows a `(Pdb)` prompt.

**pdb cheat-sheet:** `n` next line, `s` step in, `p <var>` print, `c` continue, `q` quit. If invoked with no tty (e.g. accidentally from a Gateway script), `brk()` logs a warning via `system.util.getLogger("utils.debug")` and returns without hanging.

### Debugging in PyCharm
1. Open Run/Debug Configurations
2. Select "Jython 2.7" configuration
3. Set breakpoints and run

## Key Differences: Jython 2.7 vs Python 3

### Imports
```python
# Jython 2.7 - Java imports
from java.lang import String, Exception
from java.util import ArrayList, HashMap

# Python 3 equivalent (not applicable)
# Java classes accessed through JPype or similar
```

### String Formatting
```python
# Jython 2.7 (Python 2.7 style)
print("Hello {}".format(name))
print("Value: %s" % value)

# Python 3 style (not supported)
# print(f"Hello {name}")
```

### Exception Handling
```python
# Jython 2.7
try:
    # code
except Exception, e:  # Note: comma syntax
    print e

# Python 3 style (not supported in Jython 2.7)
# try:
#     # code
# except Exception as e:
#     print(e)
```

### Data Types
- `unicode` type exists (Python 2.7)
- `long` type exists for arbitrary precision integers
- No `bytes` vs `str` distinction

## Ignition-Specific Development

### Mocking Ignition APIs
Since Ignition APIs aren't available outside the Gateway, create mock implementations:

```python
class MockSystem:
    class tag:
        @staticmethod
        def readBlocking(paths):
            return [{"value": "mock", "quality": MockQuality()}]

    class util:
        @staticmethod
        def getLogger(name):
            return MockLogger()

# Use in tests
system = MockSystem()
```

### Common Ignition Patterns
```python
# Tag change events
def tagChangeEvent(initialChange, event, udtInstancePath):
    if not initialChange:
        # Process tag change
        pass

# Publishing MQTT messages
def publish(module, server, topic, payload, qos, retain):
    if module == "transmission":
        system.cirruslink.transmission.publish(server, topic, payload, qos, retain)
```

## Troubleshooting

### Import Errors
- Ensure `jython.sh` is executable: `chmod +x jython.sh`
- Check Java version: `java -version`
- Verify the `jython2.7.4/` install tree is intact (must contain `jython.jar` and `Lib/`)

### Debugging Issues
- Use print statements liberally (Jython 2.7 style)
- Check exception tracebacks carefully
- Remember Jython runs on JVM - Java exceptions may occur

### Performance
- Jython is slower than CPython for CPU-intensive tasks
- Java integration has overhead
- Profile with Java profilers if needed

## Project Structure
```
ignition/
├── script-python/
│   └── exchange/
│       └── mqttVanillaTransmission/
│           └── callables/
│               └── code.py
```

## Testing
Run the environment test:
```bash
./jython.sh test_jython_setup.py
```

Expected output includes successful Java integration and mock Ignition functionality.