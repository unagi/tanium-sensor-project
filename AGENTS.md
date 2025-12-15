# AGENTS.md — Tanium Sensor Agent Handbook

This handbook summarizes the rules every development agent must follow. The original brief mandates single-file sensors, fixture-driven tests, and banned heavy APIs—do not compromise on those requirements.

## 1. Repository Structure Basics

- Create `sensors/<sensor>/` per sensor and keep three files (`win.py`, `mac.py`, `linux.py`).
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
4. **Forbidden APIs**: `time.sleep`, `subprocess.*`, `threading.Thread`, and root-level `os.walk` (e.g., `/`, `C:\\`) are prohibited. Tests monkeypatch them to raise immediately.
5. **Return format**: Currently each sensor returns lines formatted as `"<user>\t<Exist|No>"`. Keep output consistent with Tanium’s expectations.
6. **Tanium settings file**: `tanium_settings.yaml` must describe how Tanium ingests the sensor output. Example schema:
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
   Ensure `delimiter` and `columns` match the actual string format the OS files emit.

## 3. Fixtures and Test Flow

- Use `tests/helpers/fixtures.py::prepare_sensor_files(sensor, os, tmp_path)` to copy `tests/sensors/<sensor>/fixtures/<os>/files` into a temp directory, then call `run_sensor(base_dir=str(copied_path))`.
- The fixture tree should mimic real OS roots: `files/Users` (= `C\\Users` or `/Users`) or `files/home` (= `/home`). Tests pass the `files` directory, and sensors append `Users` or `home` as needed.
- Need an empty directory (e.g., a user without `.ssh`)? Drop a placeholder file like `.gitkeep` so Git tracks it; otherwise fixtures will silently omit that directory.
- Common validation under `tests/tanium/` loads every `tanium_settings.yaml` and verifies sensor output (delimiter, column count/types). Keep manifests accurate or these shared tests will fail.
- `pyproject.toml` configures pytest (`testpaths = ["tests"], `timeout = 1`, `timeout_method = "signal"`). Install `pytest-timeout` so these options work.
- Keep each test under one second. Mark slow tests with `@pytest.mark.slow` so CI can skip them.

## 4. Tooling and CI

- Install dev tools via `pip install -e ".[dev]"` or `uv pip install -e ".[dev]"` (Ruff, Black, pytest, pytest-timeout, Poe).
- Local Poe tasks (run before every PR):
  ```bash
  uv run poe lint
  uv run poe format
  uv run poe test
  ```
  Additional per-OS runs are available via `uv run poe test-linux`, `uv run poe test-mac`, and `uv run poe test-win`.
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

Follow these rules and update AGENTS.md whenever new policies appear so every agent operates with the same context.
