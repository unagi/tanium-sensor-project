# Tanium Custom Sensor Project

This repository bootstraps Tanium custom sensors written in Python. Each sensor is a single file per OS so the file can be copied straight into Tanium. Local development relies on pytest with file-based fixtures, while CI enforces Ruff, Black, and pytest to maintain quality.

## Policies

- **Single-file sensors**: Every OS implementation lives in `sensors/<name>/<os>.py` and must stand alone with only standard-library imports. This ensures you can copy the file directly into Tanium.
- **Base-directory contract**: `run_sensor(base_dir)` confines all filesystem work beneath `Path(base_dir)` so fixtures can emulate real machines. Production passes `None`, which each OS file converts into its default path.
- **Copy-block awareness**: Shared logic should be duplicated intentionally and wrapped with `# === SENSOR_COPY_BLOCK` markers so developers can keep OS variants in sync.
- **Fixture-driven tests**: Use `tests/helpers/fixtures.py::prepare_sensor_files` to clone `fixtures/<os>/files` into a temp directory before calling `run_sensor`. Fixtures model `C:\\Users`, `/Users`, or `/home` exactly.
- **Forbidden APIs**: `time.sleep`, `subprocess`, `threading.Thread`, and root-level `os.walk` are monkeypatched during tests to raise immediately. Design sensors so they never call these APIs.
- **CI guardrails**: Ruff, Black, and pytest run in GitHub Actions. Keep code formatted, lint-clean, and under the one-second timeout per test.

See `AGENTS.md` for the full policy document.

## Development Flow

```bash
pip install -e ".[dev]"
ruff check .
black . --check
pytest -m "not slow"
```

## Directory Layout

- `sensors/` — OS-specific single-file sensor code plus fixture trees.
- `tests/` — pytest suites, shared fixture helpers, forbidden API policies.
- `.github/workflows/ci.yml` — GitHub Actions workflow for lint, format, tests.

## Detailed Sensor Walkthroughs

- [Foo sensor guide (English)](sensors/foo/README.md)
- [Foo sensor guide (日本語)](sensors/foo/README.ja.md)
