# フェーズ 0: Armbian の microSD への書き込み

## 結果（確認済み）
- イメージ: `Armbian_26.8.1_Radxa-zero3_trixie_vendor_6.1.115_minimal.img.xz`（394,195,116 バイト）
  - 取得元: https://dl.armbian.com/radxa-zero3/Trixie_vendor_minimal
  - SHA256: `e78de9cb4b2d8ff1710c65c509d08faef1ba88c07fc3276b9dd637597e8234e8`（公式 .sha と一致、`xz -t` も OK）
  - GPG 署名（.asc）: 未検証
- 書き込み: `xzcat ... | sudo dd of=/dev/rdiskN bs=4m status=progress`
  - 展開後 2224 MiB（2,332,033,024 バイト）を書き込み、エラーなしで完了
  - 書き込み後の照合（ベリファイ）: 未実施

## 起きた問題
- 1回目（約 28 MB）、2回目（約 1.75 GB）で `dd: Device not configured`（デバイスが切断）。
  - 失敗位置が毎回違うため、イメージではなくリーダー/カード/USB 接続の不安定さと推測（原因は未確定）。
- 3回目は接続を変えて完走。ただし速度は約 0.9 MB/s（以前は約 10 MB/s）。
- 書き込み後、macOS が「読み取れないディスク」と表示するが、ext4 のため正常。「初期化」は押さないこと。

## 次（フェーズ 1 の前提）
- 初回起動は Mac 直結 + インターネット共有（apt のため）。HackRF はまだ接続しない。
- 電源は USB-C 5V/3A（OTG ポート）。PoE と同時に使わない。
