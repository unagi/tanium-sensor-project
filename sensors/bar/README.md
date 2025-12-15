# Bar Sensor Guide

The `bar` sensor reports the platform build identifier (Windows build number, macOS build version, or Linux kernel release). Each OS file shells out to the native command (`cmd /c ver`, `sw_vers -buildVersion`, or `uname -r`), sanitizes the first build-like token, and returns a single text line.

## Implementation

- **Entry point**: `win.py`, `mac.py`, and `linux.py` each implement `run_sensor(base_dir: str | None = None) -> str` and print the value when executed directly.
- **Command capture**: `_capture_command_output` uses `os.popen` and returns the command stdout, swallowing `OSError` so the sensor still returns an empty string instead of crashing on endpoints with execution restrictions.
- **Normalization**: `_sanitize_build_number` trims the stdout and applies an OS-specific regex to isolate the build identifier (e.g., `Version 10.0.19045` ➝ `10.0.19045`). The copy-block guards ensure the helper logic stays identical across OS targets.
- **Base directory**: The sensor never reads the filesystem—`base_dir` exists for API parity only. Tests set `base_dir=None`, but the function accepts custom values to keep the signature stable.
- **Output**: Returns a single-column string with no delimiter (e.g., `23B81` on macOS or `6.8.0-1008-azure` on Linux). Update `tanium_settings.yaml` if that format changes.

## Tanium metadata

`sensors/bar/tanium_settings.yaml` registers a single-column text sensor named `Bar - OS Build Number`. Keep `multi_column: false`, `result_type: text`, and the description synchronized with any future changes to the emitted value.

## Tests

- `tests/sensors/bar/test_<os>.py` executes the sensor on the matching platform and asserts that the returned value matches a reasonable regex for that OS.
- The tests call the real OS command, so they require both the correct platform *and* `CI=1`. Locally the tests skip automatically; in CI runners we rely on the hosted OS image to provide the command output.
- Because the sensor does not touch the filesystem, no fixture trees are needed under `tests/sensors/bar/fixtures`.

## Local validation

These sensors are side-effect free, so you can run them directly to spot-check behavior:

```bash
python sensors/bar/win.py
python sensors/bar/mac.py
python sensors/bar/linux.py
```

On non-matching platforms the command may fail or return an empty string, which is acceptable during local smoke tests. CI covers the platform-specific validation paths.
