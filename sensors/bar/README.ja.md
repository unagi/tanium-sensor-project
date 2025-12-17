# Bar センサーガイド

`bar` センサーは各プラットフォームのビルド ID（Windows のビルド番号 / macOS のビルドバージョン / Linux カーネルリリース）を採取して単一行で返します。OS ごとのファイルは標準コマンド（`cmd /c ver`、`sw_vers -buildVersion`、`uname -r`）を実行し、ビルドらしいトークンを抽出します。

## 実装

- **エントリーポイント**: `win.py` / `mac.py` / `linux.py` はそれぞれ `run_sensor(base_dir: str | None = None) -> str` を実装し、直接実行時は `print(run_sensor())` を呼び出します。
- **コマンド実行**: `_capture_command_output` は `subprocess.run(..., check=False, timeout=0.5, capture_output=True, text=True)` 固定で実行し、失敗やタイムアウトがあれば OS ごとのエラーコードを stderr に出力します。非同期 API や無限待ちは禁止です。
- **正規化**: `_sanitize_build_number` が出力をトリムし、OS ごとの正規表現でビルド ID を抽出します（例: `Version 10.0.19045` → `10.0.19045`）。コピー・ブロックのマーカーを保ち、3 OS のヘルパーを常に同期してください。
- **base_dir 引数**: このセンサーはファイルシステムへアクセスしないため `base_dir` は未使用ですが、他センサーと同じシグネチャを維持する目的で受け取ります。
- **出力形式**: 区切りなしの単一列テキスト（例: macOS は `23B81`, Linux は `6.8.0-1008-azure`）。フォーマットを変えた際は必ず `tanium_settings.yaml` も更新してください。

## エラーコード

| Code   | OS      | 事象                                    | 対処                                                                       |
|--------|---------|-----------------------------------------|----------------------------------------------------------------------------|
| BAR001 | Linux   | `uname -r` 実行失敗またはタイムアウト   | `/bin/uname` が存在するか、セキュリティ製品にブロックされていないか確認。 |
| BAR002 | Linux   | `uname -r` の終了コードが非 0           | カーネルや実行環境の異常を調査し、成功するまで再実行。                   |
| BAR101 | Windows | `cmd.exe /d /s /c ver` 実行失敗/タイムアウト | `cmd.exe` が利用可能か、ポリシーがブロックしていないか確認。        |
| BAR102 | Windows | `cmd.exe /d /s /c ver` の終了コードが非 0 | シェルポリシーや AV でコードが書き換わっていないか確認。           |
| BAR201 | macOS   | `sw_vers -buildVersion` 実行失敗/タイムアウト | `/usr/bin/sw_vers` が存在し SIP が邪魔していないか確認。           |
| BAR202 | macOS   | `sw_vers -buildVersion` の終了コードが非 0 | `sw_vers` が参照する plist の破損を修復し再実行。                   |

いずれのケースでも（エラー発生時は）stdout を空文字のままにしているため、Tanium 側は stderr のコードを頼りに失敗を判別できます。通常運用では常に 1 行のビルド ID を返すため、このセンサーで `[no results]` プレースホルダーが使われることはありません。

## Tanium メタデータ

`sensors/bar/tanium_settings.yaml` では `Bar - OS Build Number` という単一列センサーとして登録しています。`multi_column: false` や `result_type: text` など、実際の出力と矛盾しないよう常に同期させてください。

## テスト

- `tests/sensors/bar/test_<os>.py` が該当 OS でのみ実行され（バイナリパスが OS 固有なため）、`subprocess.run` を monkeypatch して決め打ちの出力を返します。このため CI/ローカルともに OS が合っていれば毎回同じアサーションで通ります。
- ファイルシステムを参照しないので `tests/sensors/bar/fixtures` 配下の fixture ツリーは不要です。

## ローカル動作確認

センサーは副作用が無いため、そのまま実行して動作を確認できます。

```bash
python sensors/bar/win.py
python sensors/bar/mac.py
python sensors/bar/linux.py
```

異なる OS 上ではコマンドが失敗し stdout が空文字（=失敗扱い）になる場合がありますが、ローカルの簡易チェックでは許容範囲です。プラットフォーム固有の確認は CI に任せてください。
