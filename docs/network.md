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
