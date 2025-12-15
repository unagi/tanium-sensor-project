# Foo Sensor Guide

This document walks through how the sample `foo` sensor is put together so you can clone the approach for new sensors.

## Implementation

- **Entry point**: Each OS file (`win.py`, `mac.py`, `linux.py`) implements `run_sensor(base_dir: str | None = None) -> str` and prints the result when executed directly.
- **Default base directories**:
  - Windows: `C:\\Users`
  - macOS: `/Users`
  - Linux: `/home`
- **Copy-aware logic**: The block wrapped by `# === SENSOR_COPY_BLOCK ...` must stay identical across the OS files; update all three files when making changes.
- **Scope control**: `base_dir` is converted to `Path(base_dir)` and all filesystem operations stay beneath that directory.
- **Output**: One tab-separated line per user directory, e.g. `alice	Exist` or `bob	No`.

## Fixtures

Fixtures live under `tests/sensors/foo/fixtures/<os>/files`. The `files` directory mirrors the real OS root the sensor expects. Examples:

```
tests/sensors/foo/fixtures/win/files/Users/alice/.ssh/id_ed25519
tests/sensors/foo/fixtures/mac/files/Users/charlie/.ssh/id_ed25519
tests/sensors/foo/fixtures/linux/files/home/erin/.ssh/id_ed25519
```

Tests call `prepare_sensor_files("foo", <os>, tmp_path)` which copy the entire `files` tree to a temporary directory and return that path as `base_dir`.

## Tanium settings

`sensors/foo/tanium_settings.yaml` captures the metadata required when importing the sensor into Tanium. It declares that the sensor emits two tab-delimited columns (`User`, `SSH Key Status`) and sets operational details like TTL and category. Keep the YAML in sync with any change to the emitted delimiter or column order.

## Tests

- Location: `tests/sensors/foo/test_<os>.py`
- Pattern:
  1. Copy fixtures with `prepare_sensor_files`.
  2. Call `run_sensor(base_dir=str(copied_dir))`.
  3. Assert on the resulting lines.

### Running the suite

```bash
pip install -e ".[dev]"
pytest tests/sensors/foo -m "not slow"
```

The autouse fixture in `tests/conftest.py` forbids `time.sleep`, `subprocess`, `threading.Thread`, and root-level `os.walk`, so tests will fail immediately if sensors call those APIs.

## Extending the pattern

1. Copy `sensors/foo` to a new directory and rename it.
2. Adjust default base paths, copy-block logic, and docstrings to fit the new sensor purpose.
3. Duplicate the fixture layout under `tests/sensors/<sensor>/fixtures` and populate with representative files.
4. Copy the tests, point them at the new sensor, and update assertions.

Keep the copy-block markers intact. These visual cues make it easy to update the logic consistently across OS targets.
