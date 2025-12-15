# Bar センサーガイド

`bar` センサーは各プラットフォームのビルド ID（Windows のビルド番号 / macOS のビルドバージョン / Linux カーネルリリース）を採取して単一行で返します。OS ごとのファイルは標準コマンド（`cmd /c ver`、`sw_vers -buildVersion`、`uname -r`）を実行し、ビルドらしいトークンを抽出します。

## 実装

- **エントリーポイント**: `win.py` / `mac.py` / `linux.py` はそれぞれ `run_sensor(base_dir: str | None = None) -> str` を実装し、直接実行時は `print(run_sensor())` を呼び出します。
- **コマンド実行**: `_capture_command_output` が `os.popen` でコマンドを実行し、`OSError` は飲み込んで空文字を返します。実行制限のある端末でもセンサーが落ちないようにするためです。
- **正規化**: `_sanitize_build_number` が出力をトリムし、OS ごとの正規表現でビルド ID を抽出します（例: `Version 10.0.19045` → `10.0.19045`）。コピー・ブロックのマーカーを保ち、3 OS のヘルパーを常に同期してください。
- **base_dir 引数**: このセンサーはファイルシステムへアクセスしないため `base_dir` は未使用ですが、他センサーと同じシグネチャを維持する目的で受け取ります。
- **出力形式**: 区切りなしの単一列テキスト（例: macOS は `23B81`, Linux は `6.8.0-1008-azure`）。フォーマットを変えた際は必ず `tanium_settings.yaml` も更新してください。

## Tanium メタデータ

`sensors/bar/tanium_settings.yaml` では `Bar - OS Build Number` という単一列センサーとして登録しています。`multi_column: false` や `result_type: text` など、実際の出力と矛盾しないよう常に同期させてください。

## テスト

- `tests/sensors/bar/test_<os>.py` が該当 OS でセンサーを実行し、妥当な形式のビルド ID かを正規表現で検証します。
- 実 OS のコマンドを叩くため、正しいプラットフォームかつ `CI=1` 環境でのみ実行されます。ローカルでは自動的に skip され、CI でのみ有効になります。
- ファイルシステムを参照しないので `tests/sensors/bar/fixtures` 配下の fixture ツリーは不要です。

## ローカル動作確認

センサーは副作用が無いため、そのまま実行して動作を確認できます。

```bash
python sensors/bar/win.py
python sensors/bar/mac.py
python sensors/bar/linux.py
```

異なる OS 上ではコマンドが失敗して空文字になる場合がありますが、ローカルの簡易チェックでは許容範囲です。プラットフォーム固有の確認は CI に任せてください。
