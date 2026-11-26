# フェーズ 6: 運用 — 2026-11-26

## microSD の書き込み削減（Armbian 既定で設定済みを確認。追加変更なし）
- `/var/log` は zram（50 MB、`armbian-ramlog`、USE_RSYNC=true）。過去 5 回の起動分のジャーナルが残っている（`journalctl --list-boots`）
- zram スワップ（約 482 MB）、`/tmp` は tmpfs、ルートは `ext4 defaults,commit=120,errors=remount-ro`
- journald: `SystemMaxUse=20M`（`/etc/systemd/journald.conf`）
- `fake-hwclock` が 1 時間ごとに時刻を保存（NTP なしでも起動時はおおよその時刻から始まる見込み・未検証）
- 注意: `commit=120` のため、電源を抜く前に `sudo poweroff` を実行する（最大 2 分の書き込みが失われる可能性）

## 温度
- ガバナ ondemand、最大 1.8 GHz。SoC トリップ: passive 75°C / 85°C、critical 115°C（`/sys/class/thermal/thermal_zone0`）
- 実測: アイドル約 45〜50°C、20 Msps 受信中 50°C（フェーズ 5）。放熱対策の有無は未確認
- 監視: `zero3e-temp.timer`（5 分ごと、`OnBootSec=1min`）が `/usr/local/bin/zero3e-temp` を実行し、
  `soc=… gpu=… cpu0=…MHz` をジャーナルに記録。SoC 70°C 以上で WARNING。
  - 確認: `journalctl -t zero3e-temp`
  - 初回記録 `soc=51C gpu=48C cpu0=1800MHz`、`Result=success`
  - 外す: `sudo systemctl disable --now zero3e-temp.timer && sudo rm /etc/systemd/system/zero3e-temp.{service,timer} /usr/local/bin/zero3e-temp`

## 設定バックアップ
- `scripts/backup_zero3e_config.sh` で ZERO 3E から `config/zero3e/` へ取得（fstab、journald.conf、SSH 強化、温度監視一式、apt 手動パッケージ一覧、バージョン）
  - 秘密情報は対象外。netplan は root 専用のため取得スキップ（リポジトリ内のコピーを使用）
  - 取得失敗時に既存コピーを消さない（初版で消す不具合があり修正済み）
- 復元は各ファイルを同じパスに置いて `daemon-reload` / `netplan apply` 等（手順の自動化は未実施）

## 未実施
- ストリーミング中の HackRF 抜き差し、バイアスT テスト、`apt upgrade`（93 件、カーネル含む）、時刻の同期方法
