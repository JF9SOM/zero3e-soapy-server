# フェーズ 4: Mac / FBSAT59 からの接続確認 — 2026-11-26

## 結果
- Mac の `SoapySDRUtil --find="driver=remote,remote=192.168.2.2"`（Homebrew 版）で `HackRF One #0` を検出（`remote=tcp://192.168.2.2:55132`、`remote:driver=hackrf`）
- FBSAT59 から Remote SDR 経由で HackRF を認識・オープン（ログ: `SDRPipeline started (rate=1000000 Hz)` → `SDR closed: HackRF One #0 ...`）
- バージョン互換: FBSAT59 同梱 SoapySDR 0.8.1-5 / remote 0.5.2、サーバー側 SoapySDR 0.8.1-5+b2 / SoapyRemote 0.5.2-4（同系列。問題なく列挙・接続）

## ハマりどころ（FBSAT59 側の仕様。FBSAT59 のソース `src/main.py`、`rig_dialog.py` で確認）
1. 「Remote SDR自動検索を有効にする」がオフだと、`libremoteSupport.so` を読み込み先から外す（手動追加のリモートホストも動かない）。オンにしてアプリを再起動する必要がある。
2. 設定変更後の**アプリ内再起動**では、前回の `SOAPY_SDR_PLUGIN_PATH`（`~/Library/Caches/fbsat59/soapy_modules_no_remote`）が環境変数として残り、チェックを入れても反映されなかった（親プロセスが launchd になっていた。推測を含む）。
   - 対処: FBSAT59 を完全終了し、デスクトップの FBSAT59.app から起動し直す。起動後は `SOAPY_SDR_PLUGIN_PATH=~/.local/share/fbsat59-dev/soapy-bundle/soapy_modules` になり、HackRF を認識。
3. 設定画面でデバイス名が `リモート: <IP>` のままなら、リモート問い合わせが空だった状態（仮の表示）。
4. ソースのコメントによると、探索オン時、SDR 未接続の SoapyRemote サーバーがあると SDR 操作が固まる恐れがある（FBSAT59 側の既知事項。HackRF を抜いた状態でサーバーを動かしたまま起動する場合は要注意・未検証）。

## 未実施
- FBSAT59 での実受信（ストリーミング中の抜き差し含む）、`remote:format=CS8` の指定可否と帯域の確認
- フェーズ 5（iperf3、サンプルレート別の取りこぼし・CPU・温度）
