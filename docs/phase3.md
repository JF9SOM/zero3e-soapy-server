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
| 抜き差し（ストリーミング中） | **未検証** | クライアント接続なしで試験したため。Mac 接続後（フェーズ 4）に確認 |

## メモ
- 起動直後のログに `[ERROR] SoapySSDPEndpoint::sendTo(udp://[ff02::c]:1900) = -1`（IPv6 SSDP 送信失敗）。影響の有無は未確認（要確認）
- HackRF 再挿入時、PortaPack は「PortaPack Mayhem」→（HackRF モード ON）→「HackRF One」と再列挙される。HackRF モードに入り直す操作が必要
- `apt upgrade`（93 パッケージ、カーネル更新含む）は未実施
