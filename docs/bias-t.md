# バイアスT 試験（Nooelec LaNA WB）— 2026-11-26

## 前提（確認済み / 要確認）
- HackRF のバイアスT: 最大 50 mA @ 3.3 V（CLAUDE.md の記載）
- Nooelec LaNA WB: 公式データシート（Revision 1）で、入力電圧 3.3〜5.5 V（標準 5 V）、消費電流 標準 50 mA（35〜65 mA）、電源は USB / バイアスT / ピンヘッダのいずれか 1 系統のみ。周波数 300 MHz〜8 GHz（小売店の記載、要確認）
  - 消費電流の標準値が HackRF のバイアスT 上限と同等以上のため、短時間・中止条件つきで試験した
- SoapySDR（HackRF モジュール）の設定キー: `bias_tx`（`SoapySDRUtil --probe` / `getSettingInfo` で確認、既定 false）。リモート経由でも `writeSetting("bias_tx", ...)` で切替可

## 試験（`scripts/rx_bias_test.py`、1090 MHz、2 Msps、LNA 16 dB / VGA 20 dB / AMP 0）
- A: バイアスTオフ 12 秒 → B: オン 10 秒 → C: オフ 8 秒。終了時は必ずオフに戻す
- 結果（ユーザーの電流計）: バイアスTオンで **約 0.88 A**（オフ時は約 0.86 A 前後）→ 増加は約 0.02 A。中止条件（+0.04 A）以内
  - 増加分は LaNA の消費電流に対応すると推測（5V→3.3V の変換効率を仮定した見積もりで約 25〜30 mA 相当。実測値ではない）
- 受信電力: A/B/C とも約 -37.7 dBFS で変化なし。**アンテナ未接続**のため（RF 入力がない）。LNA の効果（ゲイン）の確認は未実施
- ZERO 3E / HackRF に異常なし（USB 切断・サービス再起動なし）

## 未確認
- アンテナ接続時の LNA の効果（バイアスTオン/オフのレベル差）、長時間のバイアスT運用
- FBSAT59 の Bias-T チェックボックス経由で、リモート HackRF のバイアスTが切り替わるか（FBSAT59 のログは `key='biastee'` で書き込み。HackRF モジュールのキーは `bias_tx` のため、実際に切り替わるか要確認）
