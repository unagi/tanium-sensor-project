# Tanium Custom Sensor Project

[![CI](https://github.com/unagi/tanium-sensor-project/actions/workflows/ci.yml/badge.svg)](https://github.com/unagi/tanium-sensor-project/actions/workflows/ci.yml)

このリポジトリは Tanium カスタムセンサーを Python で開発するためのスタータープロジェクトです。センサーは OS ごとに単一ファイルで完結し、本番ではそのままコピペして利用できます。Poe タスクで lint / test を統一し、CI では Ruff / Black / pytest を実行して品質を担保します。

## ポリシー

- **単一ファイルセンサー**: 各 OS 実装は `sensors/<name>/<os>.py` に配置し、標準ライブラリ以外の import は禁止。1 ファイルを Tanium にコピーできる状態を維持します。
- **base_dir 契約**: `run_sensor(base_dir)` は `Path(base_dir)` 配下のみを操作します。fixtures で実機を再現しやすくするため、`base_dir=None` の場合だけデフォルトパスを設定します。
- **コピー対象ブロック**: 共有ロジックは OS ごとにコピペし、`# === SENSOR_COPY_BLOCK` で囲って同期管理します。
- **fixtures ドリブンテスト**: `tests/helpers/fixtures.py::prepare_sensor_files` で `tests/sensors/<sensor>/fixtures/<os>/files` をテンポラリへ複製し、`C:\\Users` や `/home` を模倣したツリーを使ってテストします。
- **Tanium 設定マニフェスト**: 各センサーには `sensors/<name>/tanium_settings.yaml` を用意し、Tanium 上のメタデータ（name / category / TTL / `multi_column` / `delimiter` / columns）を定義します。`tests/tanium/` の共通テストがマニフェストと実出力の整合性（delimiter・列数・型）を検証します。
- **禁止 API**: `time.sleep` / `subprocess` / `threading.Thread` / ルート直下 `os.walk` は pytest 実行時に monkeypatch されており、呼ぶと即エラーになります。
- **タスクランナー優先**: lint とテストは Poe タスク (`poe lint` 等) 経由で実行し、コマンドを一箇所で管理します。
- **CI ガードレール**: `.github/workflows/ci.yml` で Poe タスクを呼び出し、1 テストあたり 1 秒以内を徹底します。

詳細は `AGENTS.md` を参照してください。

## 開発フロー

```bash
uv run poe lint
uv run poe format
uv run poe test
uv run poe test-global
```

## ディレクトリ構成

- `sensors/` — OS ごとに単一ファイルのセンサーコード。
- `sensors/<name>/tanium_settings.yaml` — Tanium 取り込み用メタデータ。
- `tests/sensors/<sensor>/fixtures/` — テストと同居する fixtures ツリー。
- `tests/tanium/` — `tanium_settings.yaml` と実出力の整合性を確認する共通テスト。
- `tests/` — pytest ベースのセンサー単位テスト、共通フィクスチャーヘルパー、禁止 API 設定。
- `.github/workflows/ci.yml` — Poe タスクを用いた GitHub Actions ワークフロー。

## 詳細ドキュメント

- [Foo センサーガイド (英語)](sensors/foo/README.md)
- [Foo センサーガイド (日本語)](sensors/foo/README.ja.md)
