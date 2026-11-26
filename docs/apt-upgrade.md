# apt upgrade（カーネル関連を保留）— 2026-11-26

## 方針
- 更新対象 93 件のうち、カーネル・ブートローダ関連 5 件を保留（`apt-mark hold`）し、残り約 88 件を更新。
  - 保留: `linux-image-vendor-rk35xx` / `linux-dtb-vendor-rk35xx` / `linux-headers-vendor-rk35xx` / `linux-u-boot-radxa-zero3-vendor` / `armbian-firmware`（いずれも 26.8.1 → 26.8.3 が候補）
  - 理由: 起動不能時のリスク回避（SD 書き直しになる可能性・未検証）。動作中の構成（カーネル 6.1.115-vendor-rk35xx）を維持
- 保留の解除: `sudo apt-mark unhold linux-image-vendor-rk35xx linux-dtb-vendor-rk35xx linux-headers-vendor-rk35xx linux-u-boot-radxa-zero3-vendor armbian-firmware`
  （カーネル更新の前には SD イメージのバックアップを推奨）

## 手順
1. Mac のインターネット共有をオン（Wi-Fi → AX88179A）。ZERO 3E は静的 192.168.50.2 に加え DHCP で 192.168.2.2 を取得（約 27 秒）
2. `sudo apt update && sudo apt upgrade -y`（2026-11-26 16:18:58〜16:26:40、`dpkg --audit` 問題なし）
3. 共有をオフ。Mac が `en6` に IPv4 を付け直さなかったため、`networksetup -setnetworkserviceenabled AX88179A off/on` で再適用
4. `sudo reboot` で確認

## 確認結果
- 再起動後: カーネル 6.1.115-vendor-rk35xx、`end1` = 192.168.50.2/24 のみ（DHCP のリース・デフォルトルート消失）
- soapyremote-server / avahi-daemon / ssh / zero3e-temp.timer すべて active、失敗ユニットなし、HackRF 認識、保留 5 件維持
- Mac から `SoapySDRUtil --find="driver=remote,remote=192.168.50.2"` で HackRF 検出
- `ca-certificates` 更新時に `rehash: warning: skipping ca-certificates.crt…`（害はないと推測・未確認）

## 注意
- インターネット共有をオン→オフにした直後、Mac の `en6` に IPv4 が付かないことがある。付かない場合は上記 off/on（または `networksetup -setmanual AX88179A 192.168.50.1 255.255.255.0` の再実行）
