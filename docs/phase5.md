# フェーズ 5: 性能確認 — 2026-11-26

条件: Mac(Wi-Fi→USB-C LAN AX88179A 1GbE) ⇔ ZERO 3E(end1 1000Mbps) 直結、MTU 1500、バイアスT オフ、周波数 100 MHz、ゲイン 20 dB。
HackRF は USB 3.0 ポートに接続（PortaPack Mayhem 装着、実測 0.85〜0.88 A / 約 4.86 V）。

## LAN（iperf3、ZERO 3E → Mac、10 秒）
| 項目 | 結果 |
|---|---|
| TCP | 923 Mbps、再送 0 |
| UDP 320 Mbps | 損失 0 % |
| UDP 500 Mbps | 損失 0 % |

## FBSAT59（ZERO 3E 側、SoapySDRServer）
| サンプルレート | ZERO 3E → Mac 送信 | SoapySDRServer CPU | CPU 温度 | 備考 |
|---|---|---|---|---|
| 1 Msps | 17.2 Mbps | 低 | 42.5°C | |
| 3.2 Msps（FBSAT59 の上限） | 53.5 Mbps | 約 25 %（1コア相当） | 45.6°C | スペクトラム滑らか、O/U なし。電流 0.88 A |
- 送信量は レート×2 バイト×8 に約 5 % 上乗せ → CS8 で転送されている（帯域からの推測）

## SoapyRemote ストリーム試験（`scripts/rx_test.py`、Mac の radioconda Python + SoapySDR 0.8.1-6 / remote 0.5.2）
| レート | 形式 | プロトコル | 実効レート | overflow | 備考 |
|---|---|---|---|---|---|
| 10 Msps | CS8 | UDP | 9.993 Msps | 0 | 送信 168 Mbps、サーバー CPU 約 50 %、温度 48.3°C |
| 12 Msps | CS8 | UDP | 11.987 Msps | 0 | |
| 16 Msps | CS8 | UDP | 15.991 Msps | 0 | |
| 18 Msps | CS8 | UDP | 17.768 Msps | 12 | 約 1.3 % 不足 |
| 20 Msps | CS8 | UDP | 16.800 Msps | 472 | 送信 274 Mbps、サーバー CPU 約 83 %、温度 50.0°C |
| 20 Msps | CS8 | TCP | 18.248 Msps | 185 | |
| 20 Msps | CS16 | UDP | 8.287 Msps | 941 | 帯域が 2 倍必要（約 640 Mbps） |
- 結論（この条件）: **CS8 / UDP で 16 Msps までは取りこぼしなし**、18 Msps 以上で不足。CS16 は 20 Msps では不可
- 20 Msps で LAN（iperf3 UDP 500 Mbps 損失 0）に余裕があるのに不足するため、ボトルネックは LAN ではないと考えられる。
  サーバー CPU が 83 % まで上がっていたことから ZERO 3E 側の処理（SoapySDRServer）の可能性があるが、**未検証**（Mac 側 Python の読み取りループの影響も切り分けていない）
- 未比較: MTU 変更（ジャンボフレーム）、`remote:mtu` / `remote:window` の調整、リモートでの CS16 の中間レート

## 注意
- スクリプトの使い方: `python scripts/rx_test.py <rate> <CS8|CS16> <udp|tcp> <seconds>`（`SoapySDR` が import できる Python で実行。先に FBSAT59 などで HackRF を開いていないこと）
