# Bar Sensor Guide

The `bar` sensor reports the platform build identifier (Windows build number, macOS build version, or Linux kernel release). Each OS file shells out to the native command (`cmd /c ver`, `sw_vers -buildVersion`, or `uname -r`), sanitizes the first build-like token, and returns a single text line.

## Implementation

- **Entry point**: `win.py`, `mac.py`, and `linux.py` each implement `run_sensor(base_dir: str | None = None) -> str` and print the value when executed directly.
- **Command capture**: `_capture_command_output` shells out with `subprocess.run(..., check=False, timeout=0.5, capture_output=True, text=True)` so every invocation is synchronous, bounded, and reproducible. `stderr` records deterministic error codes whenever execution fails or times out.
- **Normalization**: `_sanitize_build_number` trims the stdout and applies an OS-specific regex to isolate the build identifier (e.g., `Version 10.0.19045` ➝ `10.0.19045`). The copy-block guards ensure the helper logic stays identical across OS targets.
- **Base directory**: The sensor never reads the filesystem—`base_dir` exists for API parity only. Tests set `base_dir=None`, but the function accepts custom values to keep the signature stable.
- **Output**: Returns a single-column string with no delimiter (e.g., `23B81` on macOS or `6.8.0-1008-azure` on Linux). Update `tanium_settings.yaml` if that format changes.
- **No-network requirement**: The commands run locally, avoid stdout piping, and respect the one-thread rule from `AGENTS.md`.

## Error codes

| Code   | OS       | Scenario                                 | Remediation                                                                  |
|--------|----------|------------------------------------------|-------------------------------------------------------------------------------|
| BAR001 | Linux    | `subprocess.run` failed or timed out     | Ensure `/bin/uname` exists and returns promptly.                              |
| BAR002 | Linux    | `uname -r` exited non-zero               | Investigate kernel misconfiguration; rerun after resolving the exit status.   |
| BAR101 | Windows  | `cmd.exe /d /s /c ver` failed or timed out | Confirm `cmd.exe` is accessible and not blocked by security policy.          |
| BAR102 | Windows  | `cmd.exe /d /s /c ver` returned non-zero | Check the command shell policy or DEP/antivirus that injects non-zero exit codes. |
| BAR201 | macOS    | `sw_vers -buildVersion` failed or timed out | Ensure `/usr/bin/sw_vers` exists and SIP hasn't removed it.               |
| BAR202 | macOS    | `sw_vers -buildVersion` returned non-zero | Inspect `sw_vers` for errors (e.g., corrupted plists) and rerun.              |

All error codes emit stderr only; stdout stays empty so Tanium can treat the run as a failure. During normal operation the sensor always returns exactly one build identifier, so the `[no results]` placeholder is never expected here.

## Tanium metadata

`sensors/bar/tanium_settings.yaml` registers a single-column text sensor named `Bar - OS Build Number`. Keep `multi_column: false`, `result_type: text`, and the description synchronized with any future changes to the emitted value.

## Tests

- `tests/sensors/bar/test_<os>.py` executes on the matching platform only (to avoid invoking OS-specific binaries on the wrong host). Inside each test we monkeypatch `subprocess.run` to return deterministic stdout so the regex assertions remain stable without shelling out in CI or local development.
- Because the sensor does not touch the filesystem, no fixture trees are needed under `tests/sensors/bar/fixtures`.

## Local validation

These sensors are side-effect free, so you can run them directly to spot-check behavior:

```bash
python sensors/bar/win.py
python sensors/bar/mac.py
python sensors/bar/linux.py
```

On non-matching platforms the command may fail and therefore produce an empty stdout value, which is acceptable during local smoke tests. CI covers the platform-specific validation paths on each OS.
