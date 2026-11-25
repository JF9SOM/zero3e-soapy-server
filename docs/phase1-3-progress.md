# 進捗記録（フェーズ 1〜3 の途中まで）— 2026-11-25

## 現在の構成（初期セットアップ用の一時構成）
- Mac の「インターネット共有」（Wi-Fi → USB-C LAN アダプタ AX88179A）で ZERO 3E に DHCP とインターネットを提供
  - ZERO 3E: `radxa-zero3` / 192.168.2.2（DHCP）、NIC 名 `end1`
  - 最終構成の固定 IP（192.168.50.2/24）への切り替えは未実施
- ※ USB-C LAN アダプタは Mac 本体の USB-C ポートに直接接続すること（ハブ経由では認識されなかった）

## フェーズ 1（基本設定）
- 済: 初回設定（root パスワード、ユーザー `jf9som`（sudo 有効））
- 済: タイムゾーン Asia/Tokyo、NTP 同期（`System clock synchronized: yes`）
- 済: SSH 鍵認証（Mac の ed25519 公開鍵を登録）
- 済: SSH 強化 `/etc/ssh/sshd_config.d/10-hardening.conf`
  - `PermitRootLogin no` / `PasswordAuthentication no`
  - 検証: 鍵ログイン OK、root・パスワードログインは `Permission denied (publickey)`
  - 戻す手順（ZERO 3E 上で）: `sudo rm /etc/ssh/sshd_config.d/10-hardening.conf && sudo systemctl reload ssh`
- 未: ホスト名変更（任意）、固定 IP への切り替え

## フェーズ 3 先行（パッケージ導入）
- 導入: soapyremote-server 0.5.2-4+b2, soapysdr-tools 0.8.1-5+b2, soapysdr-module-hackrf 0.3.4-2,
  hackrf 2024.02.1-3, soapysdr-module-rtlsdr 0.3.3-1+b4, rtl-sdr 2.0.2-2+b1, avahi-daemon 0.8-16
- `soapyremote-server.service` はパッケージ同梱（自作不要）。enabled / active。
  - `ExecStart=/usr/bin/SoapySDRServer --bind`、`Restart=on-abnormal`
  - TCP 55132 で待ち受け、mDNS に `radxa-zero3._soapy._tcp` を登録（ログで確認）
- SoapySDR がモジュール hackrf / rtlsdr を認識。udev ルールあり、`jf9som` は plugdev 所属
- ファイアウォールなし（ufw/nft/iptables 未導入）

## 未確認 / 次回
- HackRF の実接続（hackrf_info、`SoapySDRUtil --find`、--probe）。USB 電流の実測（電流チェッカー）は未実施
- 再起動後の自動起動、異常終了時の再起動、HackRF 抜き差し時のサービス挙動
- Mac 側からの `SoapySDRUtil --find="driver=remote,remote=..."` と FBSAT59 との互換性
- 固定 IP 切り替え（切断に備えて戻す手順を先に提示する）、インターネット共有のオフ
- `apt upgrade`（2 パッケージ更新可、カーネル更新含む）は未実施
