# フェーズ 2: HackRF の認識と電源確認 — 2026-11-26

## 構成（測定時）
- HackRF One（older than r6、FW n_240227、API 1.08）に **PortaPack（Mayhem、HackRF モード ON）** を装着
  - dmesg で最初に「PortaPack Mayhem」として列挙され、約 7 秒後に「HackRF One」として再列挙される
  - `SoapySDRUtil --probe` で `clock source=external`
- ZERO 3E は USB-C 5V/3A 電源（PoE ではない）、HackRF は USB 3.0 ポートに接続（USB 電流計を挿入）
- LNA は接続済み。今回の測定はバイアスT オフ・LNA 外部電源なし

## 認識（確認済み）
- `hackrf_info`: HackRF One を検出
- `SoapySDRUtil --find="driver=hackrf"` / `--probe`: OK
  - ネイティブ形式 CS8、形式 CS8/CS16/CF32/CF64、1〜20 MSps、0〜7250 MHz、バイアスT（`bias_tx`）既定 false
- USB は 480M（High-Speed）。dmesg に過電流・切断なし
- udev は `jf9som`（plugdev）で一般ユーザー実行可

## USB 電流・電圧（USB 電流計の実測、HackRF 側）
| 状態 | 電流 | 電圧 |
|---|---|---|
| 受信前（PortaPack 液晶オン） | 0.855 A | 4.871 V |
| 10 Msps 受信中（30 秒） | 0.84〜0.86 A | （未記録） |
| 20 Msps 受信中（30 秒） | 0.84〜0.86 A | 約 4.86 V |
- 電流は受信負荷にほぼ依存せず、PortaPack＋HackRF のベース消費が大半と推測（PortaPack 液晶オフ時は未測定）
- CLAUDE.md の「USB 3.0 ホストは 500mA 上限」は、実測 0.85 A で超過している。ただし過電流・切断・電圧低下（4.86 V 前後）は見られず動作。長時間運用は未検証

## 受信テスト（`hackrf_transfer -r /dev/null -f 100e6 -a 0 -p 0`、各 30 秒）
| レート | サンプル数 | 実時間 | hackrf_transfer CPU | CPU 温度 |
|---|---|---|---|---|
| 10 Msps | 3.0e8 | 30.003 s | 約 19% | 37.8°C |
| 20 Msps | 6.0e8 | 30.006 s | 約 38% | 38.9°C |
- 取りこぼしの兆候なし（USB 側）。ネットワーク経由は未測定

## 未実施
- バイアスT オン時の電流（LNA の仕様確認が先）、PortaPack 液晶オフ時の電流、長時間運用
