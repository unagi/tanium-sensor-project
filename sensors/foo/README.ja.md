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
- **出力フォーマット**: 各ユーザーディレクトリに対して `alice\tExist` や `bob\tNo` のようなタブ区切り行を生成し、改行で結合します。該当ユーザーが 1 件もない場合は、Tanium 標準の `[no results]` 行を最初の列に出力し、2 列目は空欄（`[no results]\t`）として戻します。
- **サニタイズ**: ユーザー名は ASCII の印字可能文字だけを許容し、タブ/改行などの制御文字は `?` に差し替えます。印字可能文字が 1 つも無い場合は `User` 列を `<unknown>` として返します。

## エラーコード

stderr には必ずエラーコードを付与します。以下の表を README で維持し、オペレーターが即座に対処できるようにしてください。

| Code   | OS      | 事象                                           | 対処                                                                       |
|--------|---------|----------------------------------------------|----------------------------------------------------------------------------|
| FOO001 | Linux   | `/home` が存在しない                          | ルートパーティションまたは fixture の mount を確認。                       |
| FOO002 | Linux   | `/home` を列挙できない                        | パーミッションやファイルシステム破損を修正。                               |
| FOO003 | Linux   | `<user>/.ssh/id_ed25519` を stat できない     | `.ssh` ディレクトリの ACL/所有権を修復し再実行。                            |
| FOO101 | macOS   | `/Users` が存在しない                         | Users ボリュームまたは fixture を準備してから再実行。                      |
| FOO102 | macOS   | `/Users` の列挙に失敗                         | SIP/ACL 等でブロックされていないか確認し、権限を戻す。                     |
| FOO103 | macOS   | `<user>/.ssh/id_ed25519` を stat できない     | `.ssh` ディレクトリの権限/ロックを解除。                                   |
| FOO201 | Windows | `C:\Users` が存在しない                       | システムドライブまたは fixture コピーの有無を確認。                        |
| FOO202 | Windows | `C:\Users` の列挙に失敗                       | AV/ポリシーなどでリスト取得が遮断されていないか確認。                      |
| FOO203 | Windows | `<user>\.ssh\id_ed25519` を stat できない     | NTFS ACL を更新して `.ssh` ディレクトリを読み取り可能にする。             |

エラー時は引き続き `stdout` を空文字のままにし、Tanium 側が失敗と判断できるようにします。一方、正常終了かつ該当ユーザーが 0 件のときは `[no results]\t` を返し、空文字にはしません。

## Fixtures

fixtures は `tests/sensors/foo/fixtures/<os>/files` に配置します。`files` 直下が実際の OS ルートを模倣します。

```
tests/sensors/foo/fixtures/win/files/Users/alice/.ssh/id_ed25519
tests/sensors/foo/fixtures/mac/files/Users/charlie/.ssh/id_ed25519
tests/sensors/foo/fixtures/linux/files/home/erin/.ssh/id_ed25519
```

テストでは `prepare_sensor_files("foo", <os>, tmp_path)` を呼び、`files` ツリーをテンポラリへコピーして `base_dir` として渡します。

## Tanium 設定

`sensors/foo/tanium_settings.yaml` に Tanium 取り込み用メタデータをまとめています。`multi_column` センサーとしてタブ区切り 2 列（`User`, `SSH Key Status`）を返す点や TTL・カテゴリをここで定義します。`User` 列は text 型として宣言し、`[no results]` プレースホルダーや `<unknown>` のサニタイズ仕様を description で説明しています。将来コンソール側で利用可能な結果型のリストが変わった場合でも、判断に迷うときは `Text` へフォールバックする方針です。出力形式を変えた場合は必ず YAML も更新してください。

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
