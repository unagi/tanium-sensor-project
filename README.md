# Tanium Custom Sensor Project

This repository bootstraps Tanium custom sensors written in Python. Each sensor is a single file per OS so the file can be copied straight into Tanium. Local development uses fixtures and Poe tasks for consistent lint/test flows, while CI enforces Ruff, Black, and pytest to maintain quality.

## Policies

- **Single-file sensors**: Every OS implementation lives in `sensors/<name>/<os>.py` and must stand alone with only standard-library imports. This ensures you can copy the file directly into Tanium.
- **Base-directory contract**: `run_sensor(base_dir)` confines all filesystem work beneath `Path(base_dir)` so fixtures can emulate real machines. Production passes `None`, which each OS file converts into its default path.
- **Copy-block awareness**: Shared logic should be duplicated intentionally and wrapped with `# === SENSOR_COPY_BLOCK` markers so developers can keep OS variants in sync.
- **Fixture-driven tests**: Use `tests/helpers/fixtures.py::prepare_sensor_files` to clone `fixtures/<os>/files` into a temp directory before calling `run_sensor`. Fixtures model `C:\\Users`, `/Users`, or `/home` exactly.
- **Forbidden APIs**: `time.sleep`, `subprocess`, `threading.Thread`, and root-level `os.walk` are monkeypatched during tests to raise immediately. Design sensors so they never call these APIs.
- **Task runner first**: Use Poe tasks (see below) for lint and tests to avoid duplicating command strings across CI and local dev.
- **CI guardrails**: Ruff, Black, and pytest run in GitHub Actions. Keep code formatted, lint-clean, and under the one-second timeout per test.

See `AGENTS.md` for the full policy document.

## Development Flow

```bash
uv run poe lint
uv run poe format
uv run poe test
```

## Directory Layout

- `sensors/` — OS-specific single-file sensor code plus fixture trees.
- `tests/` — pytest suites, shared fixture helpers, forbidden API policies.
- `.github/workflows/ci.yml` — GitHub Actions workflow for lint, format, tests via Poe tasks.

## Detailed Sensor Walkthroughs

- [Foo sensor guide (English)](sensors/foo/README.md)
- [Foo sensor guide (日本語)](sensors/foo/README.ja.md)
