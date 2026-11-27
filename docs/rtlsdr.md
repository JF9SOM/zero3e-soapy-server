# RTL-SDR の併用（HackRF と差し替え式）— 2026-11-27

目的: HackRF と RTL-SDR を差し替えて使う。差し替え時にコマンド操作なしで使えるようにする。

## 結果（確認済み。ZERO 3E の設定変更なし）
- 使用機器: Nooelec NESDR SMArt v5（USB ID 0bda:2838、チューナー R820T）。
- 導入済みの `soapysdr-module-rtlsdr`（0.3.3-1+b4）・`rtl-sdr`（2.0.2-2+b1）・udev ルール（`60-librtlsdr0.rules`）のまま動作。`jf9som` は plugdev 所属。
- カーネルの DVB ドライバー（`dvb_usb_rtl28xxu`、vendor 6.1.115 に `=m` で含まれる）は、挿すと先に読み込まれる（`dmesg` で確認、`/dev/swradio0` 登録）。ブラックリスト設定（`/etc/modprobe.d/`）は無い。
  それでも `SoapySDRUtil --find` と `rtl_test` は、使用時に「Detached kernel driver」と表示して自動で切り離して利用でき、**ブラックリストは不要だった**。
- Mac から `SoapySDRUtil --find="driver=remote,remote=192.168.50.2"` で `remote:driver = rtlsdr` として列挙できた。
- `soapyremote-server` は稼働したまま（再起動なし）で、RTL-SDR ⇔ HackRF の差し替えを往復して確認（FBSAT59 の「列挙」で双方とも認識、スペクトラム表示）。

## ストリーム試験（Mac の radioconda Python、CS8 / UDP、各 10 秒、ゲイン 30 dB、100 MHz）
| 要求レート | 実効レート | overflow |
|---|---|---|
| 1.024 Msps | 0.991 Msps | 0 |
| 2.048 Msps | 2.003 Msps | 0 |
| 2.4 Msps | 2.340 Msps | 0 |
- 実効レートが要求より約 2〜3 % 低い理由は**未確認**（開始時間の影響か、RTL-SDR 側の実レートかを切り分けていない）。
- ZERO 3E 上で `rtl_test -s 2048000` を約 6 秒実行したところ、「lost at least …」が数回出た（損失 100 万サンプルあたり最小 266）。SoapyRemote 経由ではない直接試験。連続受信での影響は**未確認**。
- `rtl_test -t` の「No E4000 tuner found」「PLL not locked」は E4000 用試験オプションの結果で、故障ではない。

## バイアスT
- 使用中の RTL-SDR はバイアスT 非対応（ユーザー申告）のため、バイアスT の確認は不要。

## 未確認
- 長時間受信での取りこぼし、RTL-SDR の消費電流の実測
- 試験用スクリプトは、`scripts/rx_test.py` の接続先を `192.168.50.2`、`remote:driver=rtlsdr` に変えた一時コピーで実施（リポジトリ内の `rx_test.py` は HackRF・旧 IP 固定のまま）
