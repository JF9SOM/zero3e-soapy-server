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
