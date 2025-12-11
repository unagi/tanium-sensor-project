# Tanium Custom Sensor Project

このリポジトリは Tanium カスタムセンサーを Python で開発するためのスタータープロジェクトです。センサーは OS ごとに単一ファイルで完結し、本番ではそのままコピペして利用できます。pytest + fixtures により現実的なファイルツリーを再現し、CI で Ruff/Black/pytest を実行して品質を担保します。

## ポリシー

- **単一ファイルセンサー**: 各 OS 実装は `sensors/<name>/<os>.py` に配置し、標準ライブラリ以外の import は禁止。1 ファイルを Tanium にコピーできる状態を維持します。
- **base_dir 契約**: `run_sensor(base_dir)` は `Path(base_dir)` 配下のみを操作します。fixtures で実機を再現しやすくするため、`base_dir=None` の場合だけデフォルトパスを設定します。
- **コピー対象ブロック**: 共有ロジックは OS ごとにコピペし、`# === SENSOR_COPY_BLOCK` で囲って同期管理します。
- **fixtures ドリブンテスト**: `tests/helpers/fixtures.py::prepare_sensor_files` で `fixtures/<os>/files` をテンポラリへ複製し、`C:\\Users` や `/home` を模倣したツリーを使ってテストします。
- **禁止 API**: `time.sleep` / `subprocess` / `threading.Thread` / ルート直下 `os.walk` は pytest 実行時に monkeypatch されており、呼ぶと即エラーとなります。
- **CI ガードレール**: GitHub Actions (`.github/workflows/ci.yml`) で Ruff / Black / pytest を実行し、テストあたり 1 秒以内を徹底します。

詳細は `AGENTS.md` を参照してください。

## 開発フロー

```bash
pip install -e ".[dev]"
ruff check .
black . --check
pytest -m "not slow"
```

## ディレクトリ構成

- `sensors/` — OS ごとに単一ファイルのセンサーコードと fixtures。
- `tests/` — pytest ベースのセンサー単位テスト、共通フィクスチャーヘルパー、禁止 API 設定。
- `.github/workflows/ci.yml` — GitHub Actions で lint / format / test を実行。

## 詳細ドキュメント

- [Foo センサーガイド (英語)](sensors/foo/README.md)
- [Foo センサーガイド (日本語)](sensors/foo/README.ja.md)
