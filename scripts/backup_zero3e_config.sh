#!/bin/zsh
# ZERO 3E の設定を Mac に引き出して config/zero3e/ に保存する（ZERO 3E は変更しない）。
# 使い方: scripts/backup_zero3e_config.sh [ホスト] [ユーザー]
# 秘密情報（鍵・パスワード）は対象外。root 専用ファイル（netplan 等）は
# sudo -n で読めたときだけ取得し、読めなければ警告のみ（リポジトリ内のコピーを使う）。
set -u
HOST="${1:-192.168.50.2}"; USER_="${2:-jf9som}"
DEST="$(cd "$(dirname "$0")/.." && pwd)/config/zero3e"
SSH=(ssh -o BatchMode=yes -o ConnectTimeout=5 "$USER_@$HOST")
mkdir -p "$DEST"

fetch() {  # fetch <remote path> [sudo]  失敗しても既存のコピーは消さない
  local rp="$1" out="$DEST$1" tmp; tmp="$(mktemp)"; mkdir -p "$(dirname "$out")"
  if [[ "${2:-}" == sudo ]]; then
    "${SSH[@]}" "sudo -n cat '$rp'" > "$tmp" 2>/dev/null || { rm -f "$tmp"; echo "SKIP (要 sudo。既存のコピーは保持): $rp"; return; }
  else
    "${SSH[@]}" "cat '$rp'" > "$tmp" 2>/dev/null || { rm -f "$tmp"; echo "SKIP (ZERO 3E に無い。既存のコピーは保持): $rp"; return; }
  fi
  mv "$tmp" "$out"; echo "OK: $rp"
}

fetch /etc/fstab
fetch /etc/systemd/journald.conf
fetch /etc/ssh/sshd_config.d/10-hardening.conf
fetch /etc/netplan/20-end1-static.yaml sudo
fetch /etc/systemd/system/zero3e-temp.service
fetch /etc/systemd/system/zero3e-temp.timer
fetch /usr/local/bin/zero3e-temp
# 手動インストールしたパッケージ、OS/カーネル情報
"${SSH[@]}" 'apt-mark showmanual | sort' > "$DEST/apt-manual-packages.txt" && echo "OK: apt-mark showmanual"
"${SSH[@]}" 'echo "kernel: $(uname -r)"; grep PRETTY_NAME /etc/os-release; dpkg-query -W soapyremote-server soapysdr-tools soapysdr-module-hackrf soapysdr-module-rtlsdr hackrf rtl-sdr avahi-daemon iperf3' > "$DEST/versions.txt" && echo "OK: versions"
echo "保存先: $DEST"
