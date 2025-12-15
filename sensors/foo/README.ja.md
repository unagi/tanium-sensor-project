# Foo センサーガイド

このドキュメントでは、サンプルセンサー `foo` の作り方（実装・fixtures・テスト）を詳しく説明します。新しいセンサーを追加するときは、この構成を複製してください。

## 実装

- **エントリーポイント**: 各 OS ファイル（`win.py` / `mac.py` / `linux.py`）は `run_sensor(base_dir: str | None = None) -> str` を実装し、直接実行された場合は `print(run_sensor())` を呼びます。
- **デフォルト基準ディレクトリ**:
  - Windows: `C:\\Users`
  - macOS: `/Users`
  - Linux: `/home`
- **コピー対象ロジック**: `# === SENSOR_COPY_BLOCK ...` で囲まれた部分は 3 OS で同一に保つ必要があります。変更時は必ず全ファイルを同期してください。
- **スコープ制御**: `base_dir` を `Path(base_dir)` に変換し、その配下のみを操作します。
- **出力フォーマット**: 各ユーザーディレクトリに対して `alice\tExist` や `bob\tNo` のようなタブ区切り行を生成し、改行で結合します。

## Fixtures

fixtures は `tests/sensors/foo/fixtures/<os>/files` に配置します。`files` 直下が実際の OS ルートを模倣します。

```
tests/sensors/foo/fixtures/win/files/Users/alice/.ssh/id_ed25519
tests/sensors/foo/fixtures/mac/files/Users/charlie/.ssh/id_ed25519
tests/sensors/foo/fixtures/linux/files/home/erin/.ssh/id_ed25519
```

テストでは `prepare_sensor_files("foo", <os>, tmp_path)` を呼び、`files` ツリーをテンポラリへコピーして `base_dir` として渡します。

## Tanium 設定

`sensors/foo/tanium_settings.yaml` に Tanium 取り込み用メタデータをまとめています。`multi_column` センサーとしてタブ区切り 2 列（`User`, `SSH Key Status`）を返す点や TTL・カテゴリをここで定義します。出力形式を変えた場合は必ず YAML も更新してください。

## テスト

- 配置: `tests/sensors/foo/test_<os>.py`
- 流れ:
  1. `prepare_sensor_files` で fixtures をコピー。
  2. `run_sensor(base_dir=str(copied_dir))` を実行。
  3. 期待する行が含まれているか検証。

### テスト実行

```bash
pip install -e ".[dev]"
pytest tests/sensors/foo -m "not slow"
```

`tests/conftest.py` の autouse fixture により、`time.sleep` / `subprocess` / `threading.Thread` / ルート直下の `os.walk` は呼んだ瞬間に失敗します。

## 拡張手順

1. `sensors/foo` をコピーし、新しいセンサー名にリネーム。
2. デフォルトパスや copy-block 部分、docstring を目的に合わせて変更。
3. `tests/sensors/<sensor>/fixtures` に fixtures ツリーを複製し、現実的なファイルを配置。
4. テストをコピーして新センサー向けに import・期待値を更新。

`# === SENSOR_COPY_BLOCK ...` のマーカーは必ず維持してください。OS 間でのロジック差分管理が容易になります。
