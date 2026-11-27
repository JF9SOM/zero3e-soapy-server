# プロジェクト：Radxa ZERO 3E による HackRF SoapyRemote サーバー構築

## 目的
HackRF One の近く（アンテナ側）に Radxa ZERO 3E を置き、SoapyRemote サーバー（SoapySDRServer）を動かしたい。
HackRF の IQ データをギガビットLAN経由で Mac（またはWindows PC）に送り、Mac側の FBSAT59で受信する。
FBSAT59 には SoapyRemote 経由のリモートSDRを読み込む機能がすでに内蔵されている。
ZERO 3E 側のサーバー構築と、FBSAT59 からの接続確認までを行う。
このリポジトリでは、セットアップ手順・設定ファイル・スクリプトを管理する。

## ハードウェア（入手済み）
- Radxa ZERO 3E（RK3566、Cortex-A55×4、RAM［1GB / 2GB］）
  - ギガビットEthernet（RJ45）
  - USB 3.0 Type-C ホスト ×1：HackRF を接続する
  - USB 2.0 Type-C OTG ×1：電源入力用
  - ストレージは microSD のみ（eMMC なし）
- Radxa ZERO 3E 用 PoE HAT（IEEE 802.3af、40ピンGPIOに取り付け）
- HackRF One（USB 2.0 High-Speed、2〜20 Msps、8bit IQ）
- Mac 側：［USB-C ギガビットLANアダプタの型番］
- PoE 給電機器：［PoE スイッチ／インジェクタの型番、802.3af か at か］

## これまでの検討結果
### 帯域
- HackRF は 1サンプル2バイトなので、10 Msps で約160Mbps、20 Msps で約320Mbps になる（計算値）。
- そのため、ギガビットの有線LANで直結する。
- SoapyRemote の転送形式は CS8（8bit）を使い、帯域を最小にしたい。
  - クライアント側で stream args の remote:format=CS8 を指定する想定（要確認）
- 実際にどこまで出るかは未検証。まず 8〜10 Msps から試して、段階的に上げる。

### ネットワーク構成（Mac と直結）
- ZERO 3E：192.168.50.2/24 の固定IP、ゲートウェイなし
- Mac の有線LAN側：192.168.50.1/24 の手入力、ルーター欄は空欄
  - Mac のインターネット接続は Wi-Fi のまま使う
- 初期セットアップの apt には、自宅ルーターへ一時的に接続するか、Mac の「インターネット共有」を使う。
- FBSAT59 からの接続指定は、Remote SDRサーバーアドレスを設定して接続する。

### 電源（要注意・未検証）
- USB 3.0 ホストポートの電流は、製品資料で 500mA 上限とされている。
- HackRF 本体の消費電流は未確認。バイアスT は最大 50mA@3.3V。
- PoE HAT の 5V 出力電流は公表値が見つからない。802.3af なので、推定で 2A 前後。
- → 最初に USB 電流チェッカーで HackRF の実消費電流を測る（ユーザー作業）。
  足りない場合は、セルフパワーのハブか Y ケーブルで HackRF を別給電する。
- PoE を使わない場合は、5V/3A の USB-C 電源を使う。

### OS
- Armbian の Radxa ZERO 3 用イメージ（Debian 13 trixie、Minimal/CLI）を使う。

### サーバーソフト：SoapyRemote のみ
- soapyremote-server は Debian 公式パッケージに arm64 版がある（確認済み、0.5.2系）。
- 一緒に入れる予定のパッケージ：soapysdr-tools、soapysdr-module-hackrf、hackrf
  （soapyremote-server 以外のパッケージ名は、apt-cache で要確認）
- hackrfだけでなく、rtl-sdrも使うことを想定し、必要なパッケージを入れておく。
- SDR++ などの他のサーバーは入れない。

### 互換性で気をつけること（要確認）
- サーバー側（Debian の SoapySDR 0.8系 / SoapyRemote 0.5.2）と、Mac 側（FBSAT59 が使う SoapySDR / SoapyRemote クライアント）のバージョンの組み合わせで、問題なく接続できるか。
- SoapyRemote は制御に TCP、ストリームに UDP（既定）を使い、サーバーの発見には mDNS（avahi）を使う。Armbian 側でファイアウォールが有効になっていないかを確認すること。

## 作業フェーズ（案）
0. Armbian の microSD への書き込みと初回起動
1. 基本設定：ホスト名、ユーザー、SSH 鍵認証、固定IP、タイムゾーン（Asia/Tokyo）、NTP
2. HackRF の認識確認：hackrf_info、SoapySDRUtil --find="driver=hackrf"、SoapySDRUtil --probe、udev ルール（一般ユーザーで HackRF にアクセスできるように）
3. SoapyRemote の導入
   - まず、パッケージに systemd ユニットが同梱されているかを確認する（systemctl list-unit-files | grep -i soapy）。
   - 同梱されていればそれを使い、なければ自作する。
   - 起動時に自動起動させ、異常終了したら再起動させる。HackRF を抜き差ししたときの挙動も確認する。
4. 接続確認
   - Mac で SoapySDRUtil --find="driver=remote,remote=192.168.50.2" を実行して、HackRF が見えるか確認する。
   - その後、FBSAT59 から接続する。
5. 性能確認
   - iperf3 で LAN の実効速度を測る。
   - サンプルレートを段階的に上げ、ZERO 3E 側の CPU 使用率・温度、ドロップ（O/U 表示やログ）を記録する。
   - 転送形式（CS8 / CS16）、MTU、UDP / TCP の違いも比較する。
6. 運用：温度監視、ログ（journald）、設定のバックアップ、microSD の書き込みを減らす設定（任意）

## 作業ルール
- 事実は、確認済みのもの（出典やコマンド出力がある）と未検証・推測のものを明確に分けて書くこと。未検証のものには「要確認」「未検証」と付ける。
- 推測でパッケージ名やオプションを断定しない。まず apt-cache search、--help、man、ソースで確認すること。
- 破壊的な操作（ディスクの書き込み、SSH が切れる可能性のあるネットワーク設定の変更、rm など）は、実行前に内容を説明して確認を取ること。
- ネットワーク設定を変えるときは、切断に備えて元に戻す手順を先に示すこと。
- githubのJF9SOMアカウントにもレポジトリを構築し、commit後には、pushすること。 
- 1フェーズずつ進め、各フェーズの終わりに結果と次の手順を短くまとめること。

## 作業状況（2026-11-26 時点。詳細は各 docs を参照）
上の「これまでの検討結果」「作業フェーズ（案）」は計画時の記述。実施結果は次のとおり（確認済みは docs にコマンド出力ベースで記載）。

| フェーズ | 結果 | 記録 |
|---|---|---|
| 0 Armbian 書き込み | 完了（trixie vendor 6.1.115 Minimal。dd は 3 回目で成功） | [docs/phase0.md](docs/phase0.md) |
| 1 基本設定 | 完了（鍵認証のみ・root 禁止、タイムゾーン Asia/Tokyo、固定 IP）。時刻同期は NTP なしのまま運用と決定 | [docs/phase1-3-progress.md](docs/phase1-3-progress.md)、[docs/network.md](docs/network.md)、[docs/time-sync.md](docs/time-sync.md) |
| 2 HackRF 認識 | 完了（PortaPack 装着。USB 実測 0.85〜0.88 A / 約 4.86 V＝計画時の 500 mA 想定を超えるが動作） | [docs/phase2.md](docs/phase2.md) |
| 3 SoapyRemote | 完了（同梱 systemd ユニットを使用。自動起動・異常終了後の再起動・抜き差しを確認） | [docs/phase3.md](docs/phase3.md) |
| 4 Mac / FBSAT59 接続 | 完了（FBSAT59 の注意点あり） | [docs/phase4.md](docs/phase4.md) |
| 5 性能 | 完了（CS8/UDP で 16 Msps まで取りこぼしなし、18 Msps 以上は不足） | [docs/phase5.md](docs/phase5.md) |
| 6 運用 | 完了（温度監視タイマー、設定バックアップ） | [docs/phase6.md](docs/phase6.md) |
| 追加 | バイアスT（LaNA WB）、`apt upgrade`（カーネル関連 5 件は保留）、PoE の検討 | [docs/bias-t.md](docs/bias-t.md)、[docs/apt-upgrade.md](docs/apt-upgrade.md)、[docs/poe.md](docs/poe.md) |
| 追加（11/27） | RTL-SDR 併用（差し替え式、設定変更なしで自動認識、FBSAT59 で確認） | [docs/rtlsdr.md](docs/rtlsdr.md) |

### 計画時の「要確認」の結論
- CS8 転送: 帯域の実測から CS8 で流れていると判断（remote:format=CS8 指定でも確認）。FBSAT59 側の指定の有無はログ未確認
- バージョン互換: FBSAT59 同梱 SoapySDR 0.8.1-5 / SoapyRemote 0.5.2 とサーバー側 0.8.1-5+b2 / 0.5.2-4 で問題なし
- ファイアウォール: Armbian には ufw/nft/iptables が未導入（制限なし）。mDNS（avahi）は動作
- 電源（USB）: 上記のとおり。**PoE は未実施**（PSE 未購入。条件整理のみ）

### 現在の構成と運用上の注意
- ZERO 3E: 192.168.50.2/24（Mac 直結、ゲートウェイなし）。`ssh jf9som@192.168.50.2`（鍵認証）。Mac 側 AX88179A は 192.168.50.1/24 手入力
- 電源を切る前に `sudo poweroff`（`ext4 commit=120`）。RTC は電池なしで電源断で初期化される（時刻は電源断時間ぶん遅れる）
- インターネット共有（apt 等）は一時的にオン→作業後オフ。オフ直後に Mac の `en6` に IPv4 が付かないときは `networksetup -setnetworkserviceenabled AX88179A off/on`
- FBSAT59: 「Remote SDR自動検索を有効にする」オン＋デスクトップの FBSAT59.app から起動し直す（アプリ内再起動は不可）。リモート HackRF のバイアスT 切替の不具合は FBSAT59 側を修正済み（FBSAT59 リポジトリ `b6e0feb`）
- カーネル関連 5 件は `apt-mark hold` 中（`config/zero3e/apt-holds.txt`）。更新前に SD イメージのバックアップを推奨

### バックアップ（GitHub）
- `config/zero3e/`: 設定ファイル、温度監視一式、apt 手動パッケージ・保留・バージョン一覧。`scripts/backup_zero3e_config.sh` で更新（失敗時は既存コピーを保持）
- **対象外**: SSH 秘密鍵・ホスト鍵・パスワード、SSH の `authorized_keys`（復元は `ssh-copy-id`）、microSD のイメージ、netplan（root 専用のため手元のコピーを手動維持）、FBSAT59 のデータベース（`fbsat59.db`。FBSAT59 のソースは別リポジトリ）
- 復元手順の自動化は未実施。再構築は docs の手順＋`config/` のファイルで行う
