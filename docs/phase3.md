# フェーズ 3: SoapyRemote サーバーの動作確認 — 2026-11-26

## 構成
- `soapyremote-server.service`（パッケージ同梱、自作なし）: `ExecStart=/usr/bin/SoapySDRServer --bind`、`Restart=on-abnormal`、enabled
- 待ち受け: TCP 55132、mDNS（avahi）に `radxa-zero3._soapy._tcp`（radxa-zero3.local）を登録

## 確認結果
| 項目 | 結果 | 根拠 |
|---|---|---|
| 再起動後の自動起動 | OK | `sudo reboot` 後、手動操作なしで active (running)、55132 LISTEN、失敗ユニットなし |
| 異常終了後の再起動 | OK | `kill -9` で MainPID 832→1608、NRestarts=1、同秒で再起動（`Result=success`） |
| HackRF 抜き差し（待機中） | OK | サービスは無影響。再挿入後 `SoapySDRUtil --find` で再検出 |
| 抜き差し（ストリーミング中） | 下記（2026-11-26 実施） | `scripts/rx_unplug_test.py` |

## メモ
- 起動直後のログに `[ERROR] SoapySSDPEndpoint::sendTo(udp://[ff02::c]:1900) = -1`（IPv6 SSDP 送信失敗）。影響の有無は未確認（要確認）
- HackRF 再挿入時、PortaPack は「PortaPack Mayhem」→（HackRF モード ON）→「HackRF One」と再列挙される。HackRF モードに入り直す操作が必要
- `apt upgrade`（93 パッケージ、カーネル更新含む）は未実施

## ストリーミング中の抜き差し試験（2026-11-26、10 Msps CS8 UDP、`scripts/rx_unplug_test.py`）
- 開始約 8 秒後に HackRF の USB を抜き、約 10 秒後に再挿入（PortaPack の HackRF モードを再度オン）
- クライアント（Mac の Python）: 抜いた直後にデータが止まり、以後 `readStream` が毎秒 `SOAPY_SDR_TIMEOUT(-1)` を返し続けた（例外やクラッシュはなし）。**再挿入しても、その接続のストリームは復帰しなかった**（75 秒の試験終了まで 0 samples/s）。終了時の `deactivateStream` / `closeStream` は成功（`hackrf_stop_rx() failed -- No such device` のエラー表示あり）
- サーバー（ZERO 3E）: `soapyremote-server` は MainPID=834、NRestarts=0 のまま稼働（落ちない）。dmesg は USB 切断→再列挙（Device 003→004）のみ、過電流なし。サーバー CPU は 0%
- 再挿入後の**新しい接続**: 10 Msps で通常どおり受信（約 10.0 Msps、non-data コードなし）
- 結論: 抜き差しでサーバーは復旧不要。クライアント側は、ストリームが止まったら（TIMEOUT が続く）**切断して再接続**する必要がある。FBSAT59 がこの状態をどう扱うか（自動再接続の有無）は未確認
