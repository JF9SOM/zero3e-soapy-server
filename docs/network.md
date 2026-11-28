# ネットワーク構成（Mac 直結・固定 IP）— 2026-11-26

## 最終構成（確認済み）
- ZERO 3E: `end1` = 192.168.50.2/24、ゲートウェイなし（netplan / systemd-networkd）
- Mac: USB-C LAN アダプタ AX88179A（en6）を手入力 192.168.50.1/24、ルーター空欄。インターネットは Wi-Fi のまま
- 再起動後も維持を確認（固定 IP、soapyremote-server・avahi が自動起動、`SoapySDRUtil --find="driver=remote,remote=192.168.50.2"` で HackRF 検出）
- SSH: `ssh jf9som@192.168.50.2`（鍵認証のみ。ホスト鍵は初回起動時の ED25519 と指紋一致を確認して登録）

## ZERO 3E の netplan
- `/etc/netplan/20-end1-static.yaml`（chmod 600）
```yaml
network:
  version: 2
  renderer: networkd
  ethernets:
    end1:
      dhcp4: true      # インターネット共有など DHCP がある環境でも使えるよう残している
      dhcp6: false
      optional: true
      addresses: [192.168.50.2/24]
```
- Armbian 既定の `10-dhcp-all-interfaces.yaml`（`e*` を DHCP にする）は `/root/netplan-backup/` に退避。
  このファイルがあると `end1` の静的設定より先に一致して優先される（推測）ため退避した。
- 固定 IP のみにしたい場合は `dhcp4: false` に変更（CLAUDE.md の元の方針）。
- 適用は `sudo netplan try --timeout 120`（120 秒以内に Enter で確定しないと実行中の設定は自動で戻る）。
- 元に戻す: `sudo rm /etc/netplan/20-end1-static.yaml && sudo mv /root/netplan-backup/10-dhcp-all-interfaces.yaml /etc/netplan/ && sudo netplan apply`

## Mac 側
- 設定: `sudo networksetup -setmanual AX88179A 192.168.50.1 255.255.255.0`
- 戻す: `sudo networksetup -setdhcp AX88179A`（インターネット共有を使うときはオンにする。このとき ZERO 3E は DHCP で 192.168.2.x も取得する見込み・未検証）
- USB-C LAN アダプタは Mac 本体の USB-C ポートへ直接接続する（ハブ経由では認識されなかった）

## 注意・未解決
- インターネット（NTP）がない間は `System clock synchronized: no`。時刻ずれの影響は未確認（FBSAT59 のタイムスタンプ等）。対策案: 定期的にインターネット共有で同期 / Mac を NTP 源にする（未検討）
- `apt upgrade`（93 パッケージ、カーネル含む）は、インターネット共有をオンにして行う（未実施）

## FBSAT59 の接続先変更（2026-11-26）
- 固定 IP 構成（192.168.50.2）で FBSAT59 からの受信（3.2 MHz、スペクトラム表示）を確認。ログ: `SDR opened: HackRF One #0 …` → `SDRPipeline started (rate=3200000 Hz)`、エラーなし
- FBSAT59 の接続先は DB（`~/Library/Application Support/fbsat59/fbsat59.db` の `app_settings` の `sdr_settings`）に保存される。GUI なら SDR設定で「リモートホストを追加…」（旧ホストは「削除」）
  - 今回は FBSAT59 終了中に DB を直接更新（`device_args.remote` と `remote_hosts[0].host`）。バックアップ: 同フォルダの `fbsat59.db.bak-20261126`
- FBSAT59 の注意（フェーズ 4 参照）: 「Remote SDR自動検索を有効にする」オン＋アプリ終了後にデスクトップの FBSAT59.app から起動し直すこと（アプリ内再起動では `SOAPY_SDR_PLUGIN_PATH` が残る）

## 追記（2026-11-28）: Mac 以外の PC から接続する
ZERO 3E 側（192.168.50.2/24 固定、DHCP なし）は Mac に依存しない。クライアント PC の有線 LAN を手動で `192.168.50.x/24`（例 192.168.50.1、ゲートウェイ・DNS は空欄）にすれば接続できる。Wi-Fi（192.168.3.x）とは範囲が重ならず、インターネットは Wi-Fi 側を使い続けられる。

確認済み（Windows 11 PC、FBSAT59 インストール版同梱の SoapySDR を使用）:
- 有線 LAN を `192.168.50.1/24`（ゲートウェイ空欄）に設定、`Test-NetConnection 192.168.50.2 -Port 55132` が成功。Windows ファイアウォールの追加設定は不要だった（今回の構成で）。
- FBSAT59 から HackRF に接続でき、動作を確認（ユーザー確認）。
- 最初は接続できなかった。原因は FBSAT59 のログ上、Remote モジュールを除外した `soapy_modules_no_remote` が使われていたこと（`SoapySDR::Device::make() no match`）。**「Remote SDR 自動検索を有効にする」をオン → FBSAT59 を完全終了 → ショートカットから起動し直し**で解決（Mac と同じ）。

未確認: GPD の Linux（Ubuntu）からの接続。手順は、Ubuntu の設定 → Network → Wired の「+」で IPv4 を Manual（192.168.50.1 / 255.255.255.0、ゲートウェイ空欄）にする。

## 追記（2026-11-28）: Windows PC の SSH 公開鍵を ZERO 3E に追加
- 目的: Windows PC から `ssh jf9som@192.168.50.2` で入れるようにする（ZERO 3E は鍵認証のみのため、鍵がないと `Permission denied (publickey)`）。
- Windows（`FUJITSU`、`ssh windev` で入れる PC）に、ed25519 の鍵を新規作成（`C:\Users\pc\.ssh\id_ed25519`、**パスフレーズなし**、コメント `windows-fujitsu-to-zero3e`）。
- 公開鍵（フィンガープリント `SHA256:hOOwey1vW7JfWV/hNJZWoIDlleJxq431xVwsdgkPMj4`）を、ZERO 3E の `~/.ssh/authorized_keys` に 1 行追加（権限 600 のまま。登録は Mac と Windows の 2 本）。
- 追加の方法: ZERO 3E が Windows 直結で Mac から届かなかったため、**Windows を中継**して Mac の鍵で入り追記した（`ssh -J windev jf9som@192.168.50.2`）。ケーブルの付け替えは不要だった。
- 確認済み: Windows から `ssh jf9som@192.168.50.2 hostname` が成功（`radxa-zero3`）。初回接続で ZERO 3E のホスト鍵が Windows の `known_hosts` に登録された。
- 注意: 鍵にパスフレーズがないため、Windows の `pc` アカウントに入れる人は ZERO 3E にも入れる。使えなくするには、`authorized_keys` の `windows-fujitsu-to-zero3e` の行を削除する。
- バックアップ対象外: `authorized_keys` は GitHub のバックアップ対象外（復元は `ssh-copy-id` や上の方法で再登録）。公開鍵はこの文書の上記フィンガープリントで照合できる。秘密鍵はこのリポジトリに含めない。
