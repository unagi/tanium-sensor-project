# AGENTS.md — Tanium Sensor Agent Handbook

This handbook summarizes the rules every development agent must follow. The original brief mandates single-file sensors, fixture-driven tests, and banned heavy APIs—do not compromise on those requirements.

Always write and maintain this handbook in English so every agent references the same canonical guidance.

## 1. Repository Structure Basics

- Create `sensors/<sensor>/` per sensor and keep three files (`win.py`, `mac.py`, `linux.py`).
- Document every sensor directory with `README.md` (EN) and `README.ja.md` (JP) that describe the sensor purpose, implementation, fixtures/tests, and Tanium metadata. Copy `sensors/foo/README*.md` as the template when bootstrapping a new sensor.
- Each OS file **must remain self-contained**. Import only from the standard library; never add shared helper modules.
- Place test collateral under `tests/`. Store fixture trees under `tests/sensors/<sensor>/fixtures/<os>/files/...` so tests and fixtures live together.
- Keep Tanium deployment metadata in `sensors/<sensor>/tanium_settings.yaml`. This file defines the console settings (name, category, TTL, delimiter, column schema, etc.) for the sensor.

## 2. Sensor Implementation Rules

1. **Fixed signature**: Every OS file defines `run_sensor(base_dir: str | None = None) -> str` and ends with `if __name__ == "__main__": print(run_sensor())`.
2. **No access outside `base_dir`**: Only when `base_dir is None` may you compute the OS default path; otherwise operate strictly within `Path(base_dir)`.
3. **Copy/paste governance**:
   - Even if logic looks similar, do not create shared modules—**copy the logic intentionally**.
   - Mark duplicated regions so updates stay in sync:
     ```python
     # === SENSOR_COPY_BLOCK START ===
     ... shared logic ...
     # === SENSOR_COPY_BLOCK END ===
     ```
   - Keep the markers intact and update every OS variant together.
4. **Execution boundaries and banned APIs**:
   - Disallow any API that introduces asynchronous or parallel execution or unbounded disk I/O: `time.sleep`, `threading.Thread`, `asyncio.*`, `multiprocessing.*`, root-level `os.walk` (e.g., `/`, `C\\`), `Path.glob("**/*")`, `Path.rglob("*")`, or similar scans stay off-limits so each sensor remains single-shot and lightweight.
   - Synchronous process execution is allowed only when using deterministic, blocking calls such as `subprocess.run(..., check=True, capture_output=True)` with fully validated inputs. Starting background helpers (e.g., `subprocess.Popen`) or piping unchecked data directly into commands violates this rule.
   - Every external process call **must** set an explicit `timeout=` derived from the expected runtime (default to ≤1 second unless leadership approves a higher ceiling). If the timeout expires, fail fast, emit the sensor’s error code to `stderr`, and return no partial stdout data.
   - Even when synchronous, never launch heavy workloads, long-running daemons, or commands that pop up GUI windows or alter user sessions. Limit executions to fast, CLI-only utilities whose side effects you fully control.
   - Never trigger network traffic (HTTP calls, DNS lookups, `ping`, `curl`, etc.) or commands that modify host state (writing outside `base_dir`, restarting services, editing registry/system settings). Sensors must be read-only observers.
   - Honor the "one sensor run = one thread" principle and leave intent-revealing comments so future maintainers do not accidentally reintroduce async or multi-threading.
5. **Runtime bounds**: Decline any sensor requirement that is expected to take 10 seconds or longer in the worst case. If a design might exceed 1 second but stay under 10 seconds, obtain written approval from the development lead before committing to the implementation, and document that approval in the sensor README.
   - Record approvals under a `## Performance Exceptions` section in `sensors/<sensor>/README.md` using this template so audits stay consistent:
     ```
     | Date       | Reviewer        | Scenario / Justification                       | Timeout cap |
     |------------|-----------------|-----------------------------------------------|-------------|
     | 2025-12-15 | Jane Smith (DL) | Needs 3s to parse 500MB archive header safely | 3s          |
     ```
6. **Predictable footprint**: Never add behaviors that could enumerate unbounded directories, buffer huge files, or otherwise hammer disks. Cap traversal scope aggressively so even pathological endpoints stay lightweight.
7. **Return format**: Currently each sensor returns lines formatted as `"<user>\t<Exist|No>"`. Keep output consistent with Tanium’s expectations, and deterministically sort the rows with a case-sensitive key tailored to the sensor so identical inputs always yield identical outputs.
8. **Clean output**: Avoid blank lines, trailing whitespace, or redundant newlines. If there is no data, return an empty string rather than a newline so ingestion pipelines stay predictable.
9. **Error handling**: Define sensor-specific error codes for predictable failure modes (missing `base_dir`, unreadable file, malformed record, etc.). Emit concise human-readable diagnostics to `stderr` prefixed with the code, and leave `stdout` untouched so Tanium can detect failures programmatically.
   - Document every error code in `sensors/<sensor>/README.md` with a short description and the remediation steps (what the operator should verify or fix when the code appears) so responders can act without reading the source.
10. **Sensitive data handling**: Never write plaintext credentials, tokens, PII, or other sensitive material directly to `stdout` or `stderr`. Hash, truncate, or mask these values before logging, and prefer emitting only boolean/aggregate signals when practical.
    - When a sensor might encounter sensitive data and applies masking, document the technique (e.g., SHA-256 hash, first-3-last-2 masking) in `sensors/<sensor>/README.md` so reviewers and responders know what to expect.
    - Do not persist sensitive data to temporary files, caches, or logs under `base_dir`—read the minimum necessary bytes, derive the boolean you need, then immediately discard any buffers.
11. **Input sanitization**: Sanitize or escape anything sourced from outside the code (filesystem contents, env vars, or limited OS call outputs) so delimiters, tabs, or binary blobs cannot corrupt the payload. Never inject raw external strings directly into the formatter.
12. **Tanium settings file**: `tanium_settings.yaml` must describe how Tanium ingests the sensor output. Example schema:
   ```yaml
   tanium:
     name: Foobar - Logon Events
     category: Incident Response
     ttl_minutes: 15
     multi_column: true
     delimiter: "|"
     columns:
       - { name: Time, type: text }
       - { name: Hostname, type: text }
   ```
   Ensure `delimiter` and `columns` match the actual string format the OS files emit. For multi-column sensors, pick a delimiter that cannot appear in sanitized values; if that is impossible, escape the delimiter consistently so shared Tanium metadata tests keep passing.

## 3. Fixtures and Test Flow

- Use `tests/helpers/fixtures.py::prepare_sensor_files(sensor, os, tmp_path)` to copy `tests/sensors/<sensor>/fixtures/<os>/files` into a temp directory, then call `run_sensor(base_dir=str(copied_path))`.
- The fixture tree should mimic real OS roots: `files/Users` (= `C\\Users` or `/Users`) or `files/home` (= `/home`). Tests pass the `files` directory, and sensors append `Users` or `home` as needed.
- Need an empty directory (e.g., a user without `.ssh`)? Drop a placeholder file like `.gitkeep` so Git tracks it; otherwise fixtures will silently omit that directory.
- Common validation under `tests/tanium/` loads every `tanium_settings.yaml` and verifies sensor output (delimiter, column count/types). Keep manifests accurate or these shared tests will fail.
- **OS-native execution tests**: if a sensor shells out (e.g., `uname`, `sw_vers`, `cmd /c ver`), at least one pytest per OS must execute the real command so CI proves the integration path end-to-end. Gate these with `pytest.mark.skipif(not os.environ.get("CI"), ...)` and a platform check so local runs stay fast.
- **Test categorization**: structure pytest modules so spec output makes it obvious whether a case performs “Real Execution” (exercising actual filesystem/OS behavior) or “Mocked Behavior” (simulated edge cases). Using pytest class names for these groups keeps the pytest-spec report scannable and enforces a consistent naming convention across sensors.
- Performance validation: add at least one test per sensor that measures `run_sensor()` with `time.perf_counter()` (or mocks slow dependencies) and asserts the elapsed wall time stays within the approved budget. For logic that cannot run deterministically on the developer workstation (sanitization, transient filesystem errors), you may mock at the Python layer, but **do not** mock the OS command tests described above—actual binaries must run in CI.
- `pyproject.toml` configures pytest (`testpaths = ["tests"], `timeout = 1`, `timeout_method = "thread"`). Install `pytest-timeout` so these options work; Windows runners cannot use `signal`, so we stick with the thread-based timeout for portability.
- Keep each test under one second. Mark slow tests with `@pytest.mark.slow` so CI can skip them.

## 4. Tooling and CI

- Install dev tools via `pip install -e ".[dev]"` or `uv pip install -e ".[dev]"` (Ruff, Black, pytest, pytest-timeout, Poe).
- Local Poe tasks (run before every PR):
  ```bash
  uv run poe lint
  uv run poe format
  uv run poe test
  uv run poe test-global
  ```
  Additional per-OS runs (`uv run poe test-linux`, `uv run poe test-mac`, `uv run poe test-win`) now execute the Tanium metadata suite first (`tests/tanium`) and then run `pytest -k test_<os>` so every sensor under `tests/sensors/*` is covered without updating task definitions.
  If you are not using `uv`, activate your env first and run `poe <task>`.
- `.github/workflows/ci.yml` calls the same Poe tasks on GitHub Actions, so keep them up to date whenever workflows change.

## 5. Workflow Guidance

1. When adding sensors, copy `sensors/foo/` as a template, rename it, and adjust docstrings/logic per OS—keeping copy-block markers.
2. Build fixtures first under `tests/sensors/<sensor>/fixtures/<os>/files`, then add tests under `tests/sensors/<sensor>/test_<os>.py` that call `prepare_sensor_files()`.
3. Use concise ASCII comments only when logic is non-trivial.
4. Do not remove the `sys.path` bootstrap in `tests/conftest.py`; pytest relies on it for module imports.

## 6. Common Pitfalls

- **Shared module temptation**: Resist adding `common.py`; single-file copy/paste is intentional for Tanium deployment.
- **Wrong fixture root**: Always pass `<tmp>/.../files` as `base_dir`; let sensors append `Users`/`home`.
- **Missing `pytest-timeout`**: Without installing dev deps, pytest emits `PytestConfigWarning`. Run `pip install -e ".[dev]"` first.
- **Missing copy markers**: Without `# === SENSOR_COPY_BLOCK ...` diff tracking is painful. Keep markers synchronized.
- **CI-only OS calls**: Tests that execute real OS commands must skip automatically unless both the matching platform and `CI=1` are present so local workflows stay fast while CI still covers the live code paths.

Follow these rules and update AGENTS.md whenever new policies appear so every agent operates with the same context.
